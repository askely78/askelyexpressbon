
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import psycopg2

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg in ["bonjour", "salut", "hello", "start", "menu"]:
        msg.body(
            "👋 *Bienvenue chez Askely Express !*

"
            "📦 *1.* Envoyer un colis
"
            "🚚 *2.* Devenir transporteur
"
            "🔍 *3.* Suivre un colis

"
            "Cliquez ou répondez avec le numéro correspondant."
        )
    elif incoming_msg.startswith("1"):
        msg.body(
            "📦 Très bien. Pour envoyer un colis, merci de répondre avec :
"
            "Nom expéditeur - Nom destinataire - Ville départ - Ville arrivée - Date (JJ/MM/AAAA)"
        )
    elif incoming_msg.startswith("2"):
        msg.body(
            "🚚 Pour devenir transporteur, envoyez :
"
            "Nom - Ville départ - Ville arrivée - Date (JJ/MM/AAAA) - Numéro WhatsApp"
        )
    elif incoming_msg.startswith("3"):
        msg.body("🔍 Pour suivre un colis, envoyez le *nom de l’expéditeur*.")
    elif incoming_msg.count("-") == 5:
        try:
            nom, dep, arr, date_str, numero = [x.strip() for x in incoming_msg.split("-")]
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO transporteurs (nom, ville_depart, ville_arrivee, date_depart, numero_whatsapp) VALUES (%s, %s, %s, %s, %s)",
                        (nom, dep, arr, date_str, numero))
            conn.commit()
            conn.close()
            msg.body("✅ Transporteur enregistré. Vous serez notifié lors des demandes clients.")
        except:
            msg.body("❌ Erreur dans l’enregistrement du transporteur.")
    elif incoming_msg.count("-") == 4:
        try:
            expediteur, destinataire, dep, arr, date_str = [x.strip() for x in incoming_msg.split("-")]
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id, nom, numero_whatsapp FROM transporteurs WHERE ville_depart=%s AND ville_arrivee=%s AND date_depart=%s",
                        (dep, arr, date_str))
            result = cur.fetchall()
            conn.close()
            if result:
                msg.body("🚚 Transporteurs disponibles :
" + "
".join([f"ID {r[0]} - {r[1]}" for r in result]) + "

Répondez avec `Choisir [ID]`")
            else:
                msg.body("❌ Aucun transporteur trouvé.")
        except:
            msg.body("❌ Erreur dans la demande.")
    elif incoming_msg.startswith("choisir"):
        try:
            transporteur_id = int(incoming_msg.split(" ")[1])
            conn = get_connection()
            cur = conn.cursor()
            cur.execute("SELECT numero_whatsapp FROM transporteurs WHERE id=%s", (transporteur_id,))
            numero = cur.fetchone()
            conn.close()
            if numero:
                msg.body(f"📞 Voici le numéro du transporteur : {numero[0]}")
            else:
                msg.body("❌ Transporteur non trouvé.")
        except:
            msg.body("❌ Format incorrect.")
    else:
        msg.body("🤖 Je n’ai pas compris. Tapez *menu* pour recommencer.")
    return str(resp)

@app.route("/")
def index():
    return "Askely Express est actif."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
