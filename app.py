
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").lower()
    resp = MessagingResponse()
    msg = resp.message()

    if "bonjour" in incoming_msg or "menu" in incoming_msg:
        msg.body("👋 *Bienvenue chez Askely Express !*\nEnvoyez un message parmi les choix suivants :\n\n📦 Envoyer un colis\n📝 Inscription transporteur\n🔎 Suivi de colis\nℹ️ Aide")
    elif "envoyer un colis" in incoming_msg:
        msg.body("📦 Très bien. Pour envoyer un colis, merci d’envoyer les informations suivantes (chacune sur une ligne) :\n\n1. Nom complet\n2. Téléphone\n3. Ville de départ\n4. Ville d’arrivée\n5. Date souhaitée")
    elif "inscription transporteur" in incoming_msg:
        msg.body("📝 Bienvenue transporteur ! Veuillez envoyer les informations suivantes (chacune sur une ligne) :\n\n1. Nom complet\n2. Téléphone\n3. Villes desservies\n4. Dates disponibles")
    elif "suivi de colis" in incoming_msg:
        msg.body("🔎 Merci de renseigner votre numéro de suivi pour localiser votre colis.")
    else:
        msg.body("❓ Je n'ai pas compris votre demande. Veuillez répondre avec :\n- Envoyer un colis\n- Inscription transporteur\n- Suivi de colis\n- Menu")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
