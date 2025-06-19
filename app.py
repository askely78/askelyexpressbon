import os
from flask import Flask, request, render_template, redirect, url_for
import psycopg2
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime

app = Flask(__name__)

# Connexion à la base PostgreSQL via DATABASE_URL
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/')
def accueil():
    return render_template('index.html')

@app.route('/envoi_colis', methods=['GET', 'POST'])
def envoi_colis():
    if request.method == 'POST':
        nom = request.form['nom']
        telephone = request.form['telephone']
        ville_depart = request.form['ville_depart']
        ville_arrivee = request.form['ville_arrivee']
        date_envoi = request.form['date_envoi']
        poids = request.form['poids']
        description = request.form['description']
        lien_whatsapp = request.form['lien_whatsapp']

        if not lien_whatsapp:
            return "Accès refusé : lien WhatsApp requis."

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO colis (nom, telephone, ville_depart, ville_arrivee, date_envoi, poids, description, lien_whatsapp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (nom, telephone, ville_depart, ville_arrivee, date_envoi, poids, description, lien_whatsapp))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('confirmation'))

    return render_template('envoi_colis.html')

@app.route('/inscription_transporteur', methods=['GET', 'POST'])
def inscription_transporteur():
    if request.method == 'POST':
        nom = request.form['nom']
        whatsapp = request.form['whatsapp']
        date_depart = request.form['date_depart']
        ville_depart = request.form['ville_depart']
        ville_arrivee = request.form['ville_arrivee']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO transporteurs (nom, whatsapp, date_depart, ville_depart, ville_arrivee)
            VALUES (%s, %s, %s, %s, %s)
        """, (nom, whatsapp, date_depart, ville_depart, ville_arrivee))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('confirmation'))

    return render_template('inscription_transporteur.html')

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').lower()
    resp = MessagingResponse()
    msg = resp.message()

    if 'bonjour' in incoming_msg:
        msg.body("👋 Bienvenue sur Askely Express !\n\nEnvoyez :\n1️⃣ pour envoyer un colis 📦\n2️⃣ pour devenir transporteur 🚚\n3️⃣ pour voir les transporteurs disponibles\n\nPosez une question ou dites bonjour !")
    elif incoming_msg.strip() == '1':
        msg.body("📝 Cliquez ici pour remplir le formulaire d'envoi de colis : https://askelyexpressbon.onrender.com/envoi_colis")
    elif incoming_msg.strip() == '2':
        msg.body("📝 Cliquez ici pour devenir transporteur : https://askelyexpressbon.onrender.com/inscription_transporteur")
    elif incoming_msg.strip() == '3':
        today = datetime.today().strftime('%Y-%m-%d')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT nom, whatsapp, ville_depart, ville_arrivee FROM transporteurs
            WHERE date_depart = %s
        """, (today,))
        transporteurs = cur.fetchall()
        cur.close()
        conn.close()
        if transporteurs:
            msg.body("📋 Transporteurs disponibles aujourd'hui :")
            for t in transporteurs:
                msg.body(f"- {t[0]} ({t[2]} ➡ {t[3]}) 📱 {t[1]}")
        else:
            msg.body("Aucun transporteur disponible aujourd'hui.")
    else:
        msg.body("Désolé, je n'ai pas compris. Envoyez 'bonjour' pour voir les options.")

    return str(resp)

if __name__ == '__main__':
    app.run(debug=True)
