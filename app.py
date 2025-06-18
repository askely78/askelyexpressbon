import os
from flask import Flask, request, render_template, jsonify
from twilio.twiml.messaging_response import MessagingResponse
import psycopg2
import openai

app = Flask(__name__)

# Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuration Twilio
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")

# Connexion PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

# PAGE WEB : Accueil
@app.route("/")
def index():
    return render_template("index.html")

# PAGE WEB : Liste des colis
@app.route("/colis")
def liste_colis():
    cur.execute("SELECT nom_expediteur, ville_depart, ville_arrivee, date_envoi FROM colis ORDER BY date_envoi DESC")
    colis = cur.fetchall()
    return render_template("liste_colis.html", colis=colis)

# PAGE WEB : Liste des transporteurs
@app.route("/transporteurs")
def liste_transporteurs():
    cur.execute("SELECT nom, numero_whatsapp, villes FROM transporteurs")
    transporteurs = cur.fetchall()
    return render_template("liste_transporteurs.html", transporteurs=transporteurs)

# WHATSAPP WEBHOOK
@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    sender = request.values.get("From", "")

    resp = MessagingResponse()
    msg = resp.message()

    try:
        if "envoyer" in incoming_msg.lower():
            msg.body("📦 Pour envoyer un colis, merci d’indiquer :\nNom, Ville de départ, Ville d’arrivée, Date souhaitée.")
        elif "transporteurs" in incoming_msg.lower():
            cur.execute("SELECT nom, numero_whatsapp FROM transporteurs")
            data = cur.fetchall()
            liste = "\n".join([f"{t[0]} : {t[1]}" for t in data])
            msg.body(f"🚚 Transporteurs disponibles :\n{liste}")
        else:
            # GPT-4o pour réponses libres
            completion = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": incoming_msg}]
            )
            answer = completion.choices[0].message.content.strip()
            msg.body(f"🤖 {answer}")
    except Exception as e:
        msg.body("❌ Une erreur est survenue avec l'intelligence artificielle. Réessayez plus tard.")
        print("Erreur IA :", e)

    return str(resp)
