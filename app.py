
import os
import psycopg2
import openai
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuration Twilio
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")

# Connexion à la base de données PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# Fonction IA avec GPT-4o
def repondre_avec_ia(message_utilisateur):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es Askely, un assistant de voyage intelligent, aimable et professionnel."},
                {"role": "user", "content": message_utilisateur}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print("Erreur GPT :", e)
        return "❌ Une erreur est survenue avec l’intelligence artificielle. Essaie plus tard."

# Fonction pour envoyer un message (simulée ici)
def send_message(to, body):
    print(f"Envoi vers {to}: {body}")

# Route webhook WhatsApp
@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    numero_utilisateur = request.form.get("From")
    message_utilisateur = request.form.get("Body")
    reponse = repondre_avec_ia(message_utilisateur)

    twiml_response = MessagingResponse()
    twiml_response.message(reponse)
    return str(twiml_response)

if __name__ == "__main__":
    app.run(debug=True)
