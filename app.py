from flask import Flask, request, jsonify
import os
import openai
import psycopg2
from datetime import datetime
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Connexion base de données
DATABASE_URL = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

# Clé OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Menu automatique
@app.route("/", methods=["GET"])
def home():
    return "Askely Express est en ligne."

@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip().lower()
    sender = request.values.get("From", "")
    response = MessagingResponse()
    msg = response.message()

    if incoming_msg in ["bonjour", "salut", "hello", "menu"]:
        msg.body("""
👋 Bienvenue chez *Askely Express* !

Voici ce que je peux faire pour vous :

1️⃣ Envoyer un colis  
2️⃣ Inscrire un transporteur  
3️⃣ Aide intelligente (IA)

Répondez par le numéro correspondant pour commencer.
""")
    elif incoming_msg == "1":
        msg.body("📦 Très bien. Pour envoyer un colis, merci d’envoyer les informations suivantes :

Nom complet, Ville de départ, Ville d’arrivée, Poids approximatif (kg), Date d’envoi souhaitée.")
    elif incoming_msg.startswith("📦") or "," in incoming_msg:
        try:
            parts = incoming_msg.split(",")
            if len(parts) >= 5:
                nom, depart, arrivee, poids, date_envoi = [p.strip() for p in parts[:5]]
                cur.execute("INSERT INTO colis (nom, ville_depart, ville_arrivee, poids, date_envoi, created_at) VALUES (%s, %s, %s, %s, %s, %s)", 
                            (nom, depart, arrivee, poids, date_envoi, datetime.utcnow()))
                conn.commit()
                msg.body("✅ Votre demande d’envoi a été enregistrée avec succès ! Un transporteur vous contactera bientôt.")
            else:
                msg.body("❌ Format invalide. Veuillez envoyer : Nom, Ville départ, Ville arrivée, Poids, Date.")
        except Exception as e:
            msg.body("❌ Erreur lors de l’enregistrement. Merci de réessayer.")
    elif incoming_msg == "2":
        msg.body("🚚 Pour inscrire un transporteur, merci d’envoyer :

Nom complet, Téléphone, Ville, Jours de disponibilité.")
    elif incoming_msg.startswith("🚚") or "," in incoming_msg:
        try:
            parts = incoming_msg.split(",")
            if len(parts) >= 4:
                nom, tel, ville, jours = [p.strip() for p in parts[:4]]
                cur.execute("INSERT INTO transporteurs (nom, telephone, ville, jours_dispo, created_at) VALUES (%s, %s, %s, %s, %s)", 
                            (nom, tel, ville, jours, datetime.utcnow()))
                conn.commit()
                msg.body("✅ Inscription enregistrée. Bienvenue parmi les transporteurs Askely Express !")
            else:
                msg.body("❌ Format invalide. Veuillez envoyer : Nom, Téléphone, Ville, Jours.")
        except Exception as e:
            msg.body("❌ Une erreur s’est produite. Merci de réessayer.")
    elif incoming_msg == "3":
        msg.body("✍️ Posez votre question, je vais vous répondre avec l’IA.")
    else:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": incoming_msg}]
            )
            msg.body(completion.choices[0].message.content)
        except Exception as e:
            msg.body("🤖 Erreur avec l’intelligence artificielle. Veuillez reformuler ou réessayer plus tard.")

    return str(response)

if __name__ == "__main__":
    app.run(debug=True)