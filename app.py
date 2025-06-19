import os, datetime
from flask import (
    Flask, request, render_template,
    redirect, url_for, abort, flash
)
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import psycopg2, psycopg2.extras

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "askely-secret")

DATABASE_URL  = os.getenv("DATABASE_URL")            # Postgres render.com
SITE_URL      = os.getenv("SITE_URL", "https://askelyexpressbon.onrender.com")

TW_SID        = os.getenv("TWILIO_ACCOUNT_SID")
TW_TOKEN      = os.getenv("TWILIO_AUTH_TOKEN")
TW_FROM_WHATS = os.getenv("TWILIO_WHATSAPP_FROM")     # ex +14155238886

twilio_client = Client(TW_SID, TW_TOKEN)

def db_conn():
    """Connexion context-manager à PostgreSQL."""
    return psycopg2.connect(DATABASE_URL, sslmode="require",
                            cursor_factory=psycopg2.extras.DictCursor)

# --------------------------------------------------
# ROUTE RACINE
# --------------------------------------------------
@app.route("/")
def home():
    return "Askely Express – API en ligne"

# --------------------------------------------------
# WEBHOOK WHATSAPP
# --------------------------------------------------
@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    sender = request.values.get("From", "")          # whatsapp:+212…
    body   = request.values.get("Body", "").strip().lower()
    resp   = MessagingResponse();  msg = resp.message()

    # ----- MENU PRINCIPAL ----- #
    if body in {"bonjour", "salut", "hello", "hi", "menu"}:
        msg.body(
            "👋 *Bienvenue chez Askely Express* !\n"
            "1️⃣ Envoyer un colis\n"
            "2️⃣ Devenir transporteur\n"
            "3️⃣ Publier un départ (transporteurs)\n"
            "📅 Tapez simplement une *date* (JJ/MM/AAAA) pour voir les départs"
        )
        return str(resp)

    # ----- CHOIX RAPIDES ----- #
    if body == "1":
        link = f"{SITE_URL}/envoi_colis?wa={sender}"
        msg.body(f"📦 Formulaire d’envoi : {link}")
        return str(resp)

    if body == "2":
        link = f"{SITE_URL}/inscription_transporteur?wa={sender}"
        msg.body(f"🚚 Inscription transporteur : {link}")
        return str(resp)

    if body == "3":
        with db_conn() as con, con.cursor() as cur:
            cur.execute("SELECT id FROM transporteurs WHERE whatsapp=%s", (sender,))
            if cur.fetchone():
                link = f"{SITE_URL}/publier_depart?wa={sender}"
                msg.body(f"🗓️ Publier un départ : {link}")
            else:
                msg.body("❌ Vous devez d’abord devenir transporteur (option 2).")
        return str(resp)

    # ----- LISTE DEPARTS PAR DATE ----- #
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            date_req = datetime.datetime.strptime(body, fmt).date()
            with db_conn() as con, con.cursor() as cur:
                cur.execute("""
                    SELECT d.id, t.nom, t.whatsapp, d.ville_depart, d.ville_arrivee
                    FROM departs d
                    JOIN transporteurs t ON t.id=d.transporteur_id
                    WHERE d.date_depart=%s
                    ORDER BY d.id
                """, (date_req,))
                rows = cur.fetchall()
            if rows:
                rep = f"🚚 *Départs le {date_req:%d/%m/%Y}* :\n"
                for r in rows:
                    rep += (f"• ID {r['id']} – {r['nom']} "
                            f"({r['ville_depart']} ➡ {r['ville_arrivee']})\n"
                            f"  WhatsApp : {r['whatsapp']}\n")
                msg.body(rep)
            else:
                msg.body("Aucun transporteur à cette date.")
            return str(resp)
        except ValueError:
            pass   # Pas une date → ignore & continue

    # Fallback
    msg.body("🤖 Je n’ai pas compris. Tapez *bonjour* pour le menu.")
    return str(resp)

# --------------------------------------------------
# FORMULAIRE – ENVOI DE COLIS
# --------------------------------------------------
@app.route("/envoi_colis", methods=["GET", "POST"])
def envoi_colis():
    wa = request.args.get("wa")
    if not wa:
        return "Accès refusé – lien WhatsApp requis.", 403

    if request.method == "POST":
        f = request.form
        date_envoi = f['date_souhaitee']
        with db_conn() as con, con.cursor() as cur:
            # 1) enregistrer le colis
            cur.execute("""
              INSERT INTO colis (nom, telephone, ville_depart, ville_arrivee,
                                 date_souhaitee, infos)
              VALUES (%s,%s,%s,%s,%s,%s)
              RETURNING id
            """, (f['nom'], f['telephone'], f['ville_depart'], f['ville_arrivee'],
                  date_envoi, f.get('infos')))
            colis_id = cur.fetchone()[0]

            # 2) trouver transporteurs dispo
            cur.execute("""
              SELECT t.whatsapp
              FROM departs d
              JOIN transporteurs t ON t.id=d.transporteur_id
              WHERE d.date_depart=%s
            """, (date_envoi,))
            dests = [row[0] for row in cur.fetchall()]

        # 3) notifier
        for dest in dests:
            twilio_client.messages.create(
                from_="whatsapp:" + TW_FROM_WHATS,
                to="whatsapp:" + dest,
                body=(
                    f"🚚 Nouveau colis pour le {date_envoi} "
                    f"({f['ville_depart']} ➡ {f['ville_arrivee']}). "
                    f"ID {colis_id}"
                )
            )

        flash("Colis enregistré ! Les transporteurs disponibles seront notifiés.")
        return redirect(url_for('confirmation'))
    return render_template("envoi_colis.html")

# --------------------------------------------------
# FORMULAIRE – INSCRIPTION TRANSPORTEUR
# --------------------------------------------------
@app.route("/inscription_transporteur", methods=["GET", "POST"])
def inscription_transporteur():
    wa = request.args.get("wa")
    if not wa:
        return "Accès refusé – lien WhatsApp requis.", 403

    if request.method == "POST":
        f = request.form
        with db_conn() as con, con.cursor() as cur:
            cur.execute("""
              INSERT INTO transporteurs (nom, whatsapp, ville_depart,
                                         ville_arrivee, date_depart)
              VALUES (%s,%s,%s,%s,%s)
            """, (f['nom'], f['whatsapp'], f['ville_depart'],
                  f['ville_arrivee'], f['date_depart']))
            con.commit()
        flash("Inscription réussie !")
        return redirect(url_for('confirmation'))
    return render_template("inscription_transporteur.html")

# --------------------------------------------------
# FORMULAIRE – PUBLIER DÉPART (PROTÉGÉ)
# --------------------------------------------------
@app.route("/publier_depart", methods=["GET", "POST"])
def publier_depart():
    wa = request.args.get("wa")
    if not wa:
        return "Accès refusé – lien WhatsApp requis.", 403

    with db_conn() as con, con.cursor() as cur:
        cur.execute("SELECT id FROM transporteurs WHERE whatsapp=%s", (wa,))
        row = cur.fetchone()
        if not row:
            return "Vous devez d'abord être transporteur.", 403
        transporteur_id = row[0]

    if request.method == "POST":
        f = request.form
        with db_conn() as con, con.cursor() as cur:
            cur.execute("""
              INSERT INTO departs (transporteur_id, ville_depart,
                                   ville_arrivee, date_depart)
              VALUES (%s,%s,%s,%s)
            """, (transporteur_id, f['ville_depart'], f['ville_arrivee'],
                  f['date_depart']))
            con.commit()
        flash("Départ publié !")
        return redirect(url_for('confirmation'))
    return render_template("publier_depart.html")

# --------------------------------------------------
# PAGE CONFIRMATION
# --------------------------------------------------
@app.route("/confirmation")
def confirmation():
    return render_template("confirmation.html")

# --------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
