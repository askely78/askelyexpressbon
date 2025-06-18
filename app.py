
import os
import openai
import psycopg2
from flask import Flask, request, render_template
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Connexion PostgreSQL
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

# Page d'accueil
@app.route("/")
def index():
    return render_template("index.html")

# Liste des transporteurs
@app.route("/transporteurs")
def liste_transporteurs():
    cur.execute("SELECT nom, ville, telephone FROM transporteurs")
    transporteurs = cur.fetchall()
    return render_template("liste_transporteurs.html", transporteurs=transporteurs)

# Liste des colis
@app.route("/colis")
def liste_colis():
    cur.execute("SELECT expediteur, destinataire, date_envoi FROM colis")
    colis = cur.fetchall()
    return render_template("liste_colis.html", colis=colis)

# Webhook WhatsApp
@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    resp = MessagingResponse()
    msg = resp.message()

    if "colis" in incoming_msg.lower():
        msg.body("📦 Pour consulter vos colis, cliquez ici : https://askelyexpressbon.onrender.com/colis")
    elif "transporteur" in incoming_msg.lower():
        msg.body("🚚 Pour consulter les transporteurs, cliquez ici : https://askelyexpressbon.onrender.com/transporteurs")
    else:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": incoming_msg}]
            )
            response_text = completion.choices[0].message["content"]
            msg.body(response_text)
        except Exception as e:
            msg.body("❌ Une erreur est survenue avec l'intelligence artificielle. Veuillez réessayer plus tard.")

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
