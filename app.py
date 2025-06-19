import os, datetime
from flask import Flask, request, render_template, redirect, url_for, abort
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
import psycopg2

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "askely-secret")

# ---------- Configuration ----------
DB_URL          = os.getenv("DATABASE_URL")           # ex. postgres://...
TW_SID          = os.getenv("TWILIO_ACCOUNT_SID")
TW_TOKEN        = os.getenv("TWILIO_AUTH_TOKEN")
TW_WHATSAPP_NUM = os.getenv("TWILIO_WHATSAPP_FROM")   # ex. +14155238886
SITE_URL        = os.getenv("SITE_URL", "https://askelyexpressbon.onrender.com")

# ---------- Clients ----------
twilio_client = Client(TW_SID, TW_TOKEN)

def db_conn():
    return psycopg2.connect(DB_URL, sslmode="require")

# ---------- Accueil ----------
@app.route("/")
def home():
    return "Askely Express – API en ligne"

# ---------- WEBHOOK WHATSAPP ----------
@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    sender = request.form.get("From", "")       # format 'whatsapp:+2126...'
    body   = request.form.get("Body", "").strip().lower()
    resp   = MessagingResponse(); msg = resp.message()

    # Menu
    if body in {"bonjour", "salut", "hello", "hi"}:
        msg.body(
            "👋 *Bienvenue chez Askely Express* !\n"
            "1️⃣ Envoyer un colis\n"
            "2️⃣ Devenir transporteur\n"
            "3️⃣ Publier un départ (transporteur)\n"
            "📅 Tapez une *date* (JJ/MM/AAAA) pour voir les départs\n"
            "📄 Tapez *profil [id]* pour voir un transporteur"
        )
        return str(resp)

    # Choix 1 – Formulaire colis
    if body == "1":
        link = f"{SITE_URL}/envoi_colis?wa={sender}"
        msg.body(f"📦 Formulaire d'envoi : {link}")
        return str(resp)

    # Choix 2 – Formulaire transporteur
    if body == "2":
        link = f"{SITE_URL}/inscription_transporteur?wa={sender}"
        msg.body(f"🚚 Inscription transporteur : {link}")
        return str(resp)

    # Choix 3 – Publier départ
    if body == "3":
        with db_conn() as con, con.cursor() as cur:
            cur.execute("SELECT id FROM transporteurs WHERE whatsapp=%s", (sender,))
            row = cur.fetchone()
        if row:
            link = f"{SITE_URL}/publier_depart?wa={sender}"
            msg.body(f"🗓️ Publier un départ : {link}")
        else:
            msg.body("❌ Vous devez d'abord être transporteur (option 2).")
        return str(resp)

    # Profil
    if body.startswith("profil"):
        parts = body.split()
        if len(parts) == 2 and parts[1].isdigit():
            t_id = int(parts[1])
            with db_conn() as con, con.cursor() as cur:
                cur.execute("SELECT nom, whatsapp FROM transporteurs WHERE id=%s", (t_id,))
                p = cur.fetchone()
            if p:
                msg.body(f"👤 *{p[0]}*\n📱 WhatsApp : {p[1]}")
            else:
                msg.body("Profil introuvable.")
        else:
            msg.body("❓ Utilisez : profil [id]")
        return str(resp)

    # Recherche de date (liste départs)
    for fmt in ("%d/%m/%Y", "%d-%m-%Y"):
        try:
            date_req = datetime.datetime.strptime(body, fmt).date()
            with db_conn() as con, con.cursor() as cur:
                cur.execute("""
                    SELECT d.id, t.nom, t.whatsapp, d.ville_depart, d.ville_arrivee
                    FROM departs d JOIN transporteurs t ON t.id=d.transporteur_id
                    WHERE d.date_depart=%s
                """, (date_req,))
                rows = cur.fetchall()
            if rows:
                txt = f"🚚 *Départs disponibles le {date_req:%d/%m/%Y}* :\n"
                for rid, nom, wa, vdep, varr in rows:
                    txt += (f"• ID {rid} – {nom}\n"
                            f"  Trajet : {vdep} ➡ {varr}\n"
                            f"  WhatsApp : {wa}\n")
                msg.body(txt)
            else:
                msg.body("Aucun transporteur à cette date.")
            return str(resp)
        except ValueError:
            pass  # pas une date valide

    # Fallback
    msg.body("❓ Je n’ai pas compris. Tapez *bonjour* pour le menu.")
    return str(resp)

# ---------- FORMULAIRE COLIS ----------
@app.route("/envoi_colis", methods=["GET", "POST"])
def envoi_colis():
    wa = request.args.get("wa")
    if not wa:
        return "⚠️ Accès refusé – utilisez le lien obtenu via WhatsApp.", 403

    if request.method == "POST":
        form = request.form
        date_envoi = form["date_souhaitee"]
        with db_conn() as con, con.cursor() as cur:
            # 1) Enregistrer le colis
            cur.execute("""
                INSERT INTO colis (nom, telephone, ville_depart, ville_arrivee, date_souhaitee, infos)
                VALUES (%s,%s,%s,%s,%s,%s) RETURNING id
            """, (form["nom"], form["telephone"], form["ville_depart"], form["ville_arrivee"],
                  date_envoi, form.get("infos")))
            colis_id = cur.fetchone()[0]

            # 2) Chercher transporteurs disponibles
            cur.execute("""
                SELECT t.nom, t.whatsapp, d.id
                FROM departs d JOIN transporteurs t ON t.id=d.transporteur_id
                WHERE d.date_depart=%s
            """, (date_envoi,))
            dispo = cur.fetchall()

        # 3) Notifier transporteurs
        for nom, wa_dest, dep_id in dispo:
            twilio_client.messages.create(
                from_="whatsapp:" + TW_WHATSAPP_NUM,
                to="whatsapp:" + wa_dest,
                body=(f"🚚 Nouveau colis pour le {date_envoi}\n"
                      f"Trajet : {form['ville_depart']} ➡ {form['ville_arrivee']}\n"
                      f"Répondez OK {colis_id} pour accepter.")
            )

        return render_template("confirmation.html", message="Colis enregistré !", transporteurs=dispo)
    return render_template("envoi_colis.html")

# ---------- FORMULAIRE TRANSPORTEUR ----------
@app.route("/inscription_transporteur", methods=["GET", "POST"])
def inscription_transporteur():
    wa = request.args.get("wa")
    if not wa:
        return "⚠️ Accès refusé – utilisez le lien obtenu via WhatsApp.", 403

    if request.method == "POST":
        form = request.form
        with db_conn() as con, con.cursor() as cur:
            cur.execute("""
                INSERT INTO transporteurs (nom, whatsapp, ville_depart, ville_arrivee, date_depart)
                VALUES (%s,%s,%s,%s,%s)
            """, (form["nom"], form["whatsapp"], form["ville_depart"],
                  form["ville_arrivee"], form["date_depart"]))
            con.commit()
        return render_template("confirmation.html", message="Inscription réussie !")
    return render_template("inscription_transporteur.html")

# ---------- FORMULAIRE « Publier départ » ----------
@app.route("/publier_depart", methods=["GET", "POST"])
def publier_depart():
    wa = request.args.get("wa")
    if not wa:
        return "⚠️ Accès refusé – utilisez le lien obtenu via WhatsApp.", 403

    # Vérifie l'existence du transporteur
    with db_conn() as con, con.cursor() as cur:
        cur.execute("SELECT id FROM transporteurs WHERE whatsapp=%s", (wa,))
        row = cur.fetchone()
        if not row:
            return "Vous devez d'abord être inscrit comme transporteur.", 403
        transporteur_id = row[0]

    if request.method == "POST":
        form = request.form
        with db_conn() as con, con.cursor() as cur:
            cur.execute("""
                INSERT INTO departs (transporteur_id, ville_depart, ville_arrivee, date_depart)
                VALUES (%s,%s,%s,%s)
            """, (transporteur_id, form["ville_depart"], form["ville_arrivee"], form["date_depart"]))
            con.commit()
        return render_template("confirmation.html", message="Départ publié !")
    return render_template("publier_depart.html")

# ---------- Confirmation générique ----------
@app.route("/confirmation")
def confirmation():
    msg = request.args.get("message", "Opération réussie.")
    return render_template("confirmation.html", message=msg)

# ---------- Lancement local ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)
