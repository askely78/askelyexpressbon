
import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import psycopg2

app = Flask(__name__)

# Variables d'environnement
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
DATABASE_URL = os.getenv("DATABASE_URL")

# Configuration OpenAI
openai.api_key = OPENAI_API_KEY

# Fonction pour se connecter à la base de données
def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

# Fonction pour insérer un transporteur
def enregistrer_transporteur(nom, ville, telephone):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO transporteurs (nom, ville, telephone) VALUES (%s, %s, %s)", (nom, ville, telephone))
    conn.commit()
    cur.close()
    conn.close()

# Fonction pour insérer un colis
def enregistrer_colis(nom, telephone, ville_depart, ville_arrivee, description, date_souhaitee):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO colis (nom, telephone, ville_depart, ville_arrivee, description, date_souhaitee) VALUES (%s, %s, %s, %s, %s, %s)",
        (nom, telephone, ville_depart, ville_arrivee, description, date_souhaitee)
    )
    conn.commit()
    cur.close()
    conn.close()

@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg in ["bonjour", "menu", "start", "hi"]:
        msg.body("👋 Bienvenue chez *Askely Express* !\n\nQue souhaitez-vous faire ?\n"
                 "1️⃣ Envoyer un colis\n"
                 "2️⃣ Devenir transporteur\n"
                 "3️⃣ Autre demande")
    elif incoming_msg == "1":
        msg.body("Très bien. Pour envoyer un colis, merci d’envoyer les informations suivantes :\n"
                 "- Nom complet\n"
                 "- Téléphone\n"
                 "- Ville de départ\n"
                 "- Ville d’arrivée\n"
                 "- Description du colis\n"
                 "- Date souhaitée")
    elif incoming_msg == "2":
        msg.body("Pour vous inscrire comme transporteur, merci d’envoyer les informations suivantes :\n"
                 "- Nom complet\n"
                 "- Ville de départ\n"
                 "- Numéro WhatsApp")
    elif "-" in incoming_msg:
        lignes = incoming_msg.split("\n")
        if len(lignes) == 6:
            enregistrer_colis(*lignes)
            msg.body("✅ Votre demande d’envoi de colis a été enregistrée avec succès.")
        elif len(lignes) == 3:
            enregistrer_transporteur(*lignes)
            msg.body("✅ Merci ! Vous êtes maintenant inscrit comme transporteur.")
        else:
            msg.body("❌ Format non reconnu. Merci de suivre le format donné.")
    else:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Tu es un assistant pour un service de transport de colis nommé Askely Express."},
                    {"role": "user", "content": incoming_msg}
                ]
            )
            msg.body(completion.choices[0].message.content)
        except Exception as e:
            msg.body("❌ Une erreur est survenue avec l’intelligence artificielle. Réessaie plus tard.")

    return str(resp)

@app.route("/")
def home():
    return "Askely Express en ligne."

if __name__ == "__main__":
    app.run(debug=True)
