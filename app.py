from flask import Flask, render_template, request, redirect, url_for
from twilio.twiml.messaging_response import MessagingResponse
import psycopg2, os

app = Flask(__name__)
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route('/')
def accueil():
    return render_template("index.html")

@app.route('/envoi_colis', methods=['GET', 'POST'])
def envoi_colis():
    if request.method == 'POST':
        nom = request.form['nom']
        ville_depart = request.form['ville_depart']
        ville_arrivee = request.form['ville_arrivee']
        poids = request.form['poids']
        description = request.form['description']
        whatsapp = request.form['whatsapp']
        date = request.form['date']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO colis (nom, ville_depart, ville_arrivee, poids, description, whatsapp, date) VALUES (%s, %s, %s, %s, %s, %s, %s)", (nom, ville_depart, ville_arrivee, poids, description, whatsapp, date))
        conn.commit(); cur.close(); conn.close()
        return redirect(url_for('confirmation'))
    return render_template('envoi_colis.html')

@app.route('/inscription_transporteur', methods=['GET', 'POST'])
def inscription_transporteur():
    if request.method == 'POST':
        nom = request.form['nom']
        whatsapp = request.form['whatsapp']
        ville_depart = request.form['ville_depart']
        ville_arrivee = request.form['ville_arrivee']
        date = request.form['date']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO transporteurs (nom, whatsapp, ville_depart, ville_arrivee, date) VALUES (%s, %s, %s, %s, %s)", (nom, whatsapp, ville_depart, ville_arrivee, date))
        conn.commit(); cur.close(); conn.close()
        return redirect(url_for('confirmation'))
    return render_template('inscription_transporteur.html')

@app.route('/publier_depart', methods=['GET', 'POST'])
def publier_depart():
    if request.method == 'POST':
        whatsapp = request.form['whatsapp']
        ville_depart = request.form['ville_depart']
        ville_arrivee = request.form['ville_arrivee']
        date = request.form['date']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO departs (whatsapp, ville_depart, ville_arrivee, date) VALUES (%s, %s, %s, %s)", (whatsapp, ville_depart, ville_arrivee, date))
        conn.commit(); cur.close(); conn.close()
        return redirect(url_for('confirmation'))
    return render_template('publier_depart.html')

@app.route('/confirmation')
def confirmation():
    return render_template("confirmation.html")

@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.values.get("Body", "").strip().lower()
    response = MessagingResponse()
    msg = response.message()
    if incoming_msg in ["bonjour", "salut", "hello"]:
        msg.body("👋 Bienvenue chez *Askely Express* !\n\n📦 *1* : Envoyer un colis\n🚗 *2* : Devenir transporteur\n📅 *3* : Voir les départs\n🔍 *4* : Suivre mon colis")
    elif incoming_msg == "1":
        msg.body("📦 Envoyer un colis : https://askelyexpressbon.onrender.com/envoi_colis")
    elif incoming_msg == "2":
        msg.body("🚗 Devenir transporteur : https://askelyexpressbon.onrender.com/inscription_transporteur")
    elif incoming_msg == "3":
        msg.body("📅 Départs à venir : https://askelyexpressbon.onrender.com/publier_depart")
    elif incoming_msg == "4":
        msg.body("🔍 Suivi bientôt disponible.")
    else:
        msg.body("❓ Je n’ai pas compris. Envoyez 1, 2, 3 ou 4.")
    return str(response)

if __name__ == '__main__':
    app.run(debug=True)
