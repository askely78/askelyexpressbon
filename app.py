
import os
from flask import Flask, request, render_template
import psycopg2
import openai
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Configuration OpenAI
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Connexion à la base de données PostgreSQL
DATABASE_URL = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/colis")
def liste_colis():
    cur.execute("SELECT id, expediteur, destinataire, date_envoi FROM colis ORDER BY date_envoi DESC")
    colis = cur.fetchall()
    return render_template("liste_colis.html", colis=colis)

@app.route("/transporteurs")
def liste_transporteurs():
    cur.execute("SELECT id, nom, ville, telephone FROM transporteurs ORDER BY nom ASC")
    transporteurs = cur.fetchall()
    return render_template("liste_transporteurs.html", transporteurs=transporteurs)

@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg:
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Tu es Askely Express, un assistant de livraison et de transport."},
                    {"role": "user", "content": incoming_msg},
                ],
                max_tokens=500
            )
            reply = completion.choices[0].message["content"].strip()
        except Exception as e:
            reply = f"Erreur IA : {str(e)}"
    else:
        reply = "Bienvenue sur Askely Express ! Posez-moi une question sur vos colis ou transporteurs."

    msg.body(reply)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
