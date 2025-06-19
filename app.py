from flask import Flask, render_template, request, redirect, url_for
from twilio.twiml.messaging_response import MessagingResponse
import psycopg2
import os

app = Flask(__name__)

# Connexion à la base PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Page d'accueil
@app.route('/')
def accueil():
    return render_template('index.html')

# Formulaire : envoi colis
@app.route('/envoi_colis', methods=['GET', 'POST'])
def envoi_colis():
    if request.method == 'POST':
        nom = request.form['nom']
        ville_depart = request.form['ville_depart']
        ville_arrivee = request.form['ville_arrivee']
        date = request.form['date']
        whatsapp = request.form['whatsapp']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO colis (nom, ville_depart, ville_arrivee, date, whatsapp) VALUES (%s, %s, %s, %s, %s)",
                    (nom, ville_depart, ville_arrivee, date, whatsapp))

        # Cherche les transporteurs disponibles à cette date
        cur.execute("SELECT nom, whatsapp FROM transporteurs WHERE date_disponible = %s", (date,))
        transporteurs = cur.fetchall()

        # Envoie une notification WhatsApp aux transporteurs disponibles
        for t in transporteurs:
            print(f"[INFO] Notification au transporteur {t[0]} au numéro {t[1]}")

        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('confirmation'))
    return render_template('envoi_colis.html')

# Formulaire : inscription transporteur
@app.route('/inscription_transporteur', methods=['GET', 'POST'])
def inscription_transporteur():
    if request.method == 'POST':
        nom = request.form['nom']
        whatsapp = request.form['whatsapp']
        date_disponible = request.form['date_disponible']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO transporteurs (nom, whatsapp, date_disponible) VALUES (%s, %s, %s)",
                    (nom, whatsapp, date_disponible))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('confirmation'))
    return render_template('inscription_transporteur.html')

# Déclaration des départs par transporteur
@app.route('/declaration_depart', methods=['GET', 'POST'])
def declaration_depart():
    if request.method == 'POST':
        nom = request.form['nom']
        whatsapp = request.form['whatsapp']
        date_disponible = request.form['date_disponible']

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO transporteurs (nom, whatsapp, date_disponible) VALUES (%s, %s, %s)",
                    (nom, whatsapp, date_disponible))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('confirmation'))
    return render_template('declaration_depart.html')

# Page de confirmation
@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

# Webhook Twilio WhatsApp
@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').lower()
    response = MessagingResponse()
    msg = response.message()

    if 'bonjour' in incoming_msg:
        msg.body("👋 Bonjour et bienvenue chez *Askely Express* !\n\n📦 Envoyez *1* pour envoyer un colis\n🚗 Envoyez *2* pour devenir transporteur\n📅 Envoyez *3* pour publier votre prochain départ")
    elif incoming_msg.strip() == '1':
        msg.body("📝 Remplissez le formulaire ici :\nhttps://askelyexpressbon.onrender.com/envoi_colis")
    elif incoming_msg.strip() == '2':
        msg.body("🚗 Inscription transporteur :\nhttps://askelyexpressbon.onrender.com/inscription_transporteur")
    elif incoming_msg.strip() == '3':
        msg.body("📅 Publier un départ :\nhttps://askelyexpressbon.onrender.com/declaration_depart")
    else:
        msg.body("❓ Commande inconnue. Envoyez *1*, *2* ou *3* pour commencer.")
    return str(response)

# Lancement de l'app
if __name__ == '__main__':
    app.run(debug=True)
