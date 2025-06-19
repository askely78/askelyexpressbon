
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
import psycopg2
import openai

app = Flask(__name__)

# Variables d'environnement
DATABASE_URL = os.environ.get("DATABASE_URL")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM")

# Config OpenAI
openai.api_key = OPENAI_API_KEY

@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip().lower()
    user_number = request.values.get("From", "")
    response = MessagingResponse()
    msg = response.message()

    if "envoyer un colis" in incoming_msg:
        msg.body("📦 Très bien. Pour envoyer un colis, merci de répondre avec les informations suivantes séparées par des sauts de ligne :
1. Nom du destinataire
2. Ville de destination
3. Date d'envoi souhaitée
4. Description du colis")
    elif "je suis transporteur" in incoming_msg:
        msg.body("🚚 Merci pour votre intérêt ! Pour vous inscrire comme transporteur, envoyez :
1. Votre nom complet
2. Vos destinations habituelles
3. Vos disponibilités
4. Votre numéro de téléphone")
    else:
        msg.body("👋 Bienvenue chez *Askely Express* !

Envoyez un message avec l'une des options suivantes :
• *Envoyer un colis* 📦
• *Je suis transporteur* 🚚")

    return str(response)

@app.route("/", methods=["GET"])
def index():
    return "Askely Express est en ligne."

if __name__ == "__main__":
    app.run(debug=True)
