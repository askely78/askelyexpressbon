
import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg in ["hi", "bonjour", "start", "menu"]:
        msg.body("👋 Bienvenue chez *Askely Express* !\n\n"
                 "Que souhaitez-vous faire ?\n"
                 "1️⃣ Envoyer un colis\n"
                 "2️⃣ M’inscrire comme transporteur")
    elif incoming_msg == "1":
        msg.body("📦 Très bien. Pour envoyer un colis, merci de répondre avec les informations suivantes séparées par des sauts de ligne :\n"
                 "- Ville de départ\n- Ville d’arrivée\n- Date souhaitée\n- Type de colis\n- Taille ou poids approximatif")
    elif incoming_msg == "2":
        msg.body("🚗 Merci de vouloir rejoindre notre réseau de transporteurs !\nVeuillez envoyer les informations suivantes séparées par des sauts de ligne :\n"
                 "- Nom complet\n- Numéro WhatsApp\n- Ville de départ\n- Destinations couvertes\n- Jours ou créneaux disponibles")
    else:
        msg.body("❓ Je n’ai pas compris votre demande. Envoyez 'menu' pour voir les options.")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
