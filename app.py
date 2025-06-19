
from flask import Flask, request, render_template, redirect, url_for
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

def connect_db():
    return psycopg2.connect(DATABASE_URL)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/envoi_colis', methods=['GET', 'POST'])
def envoi_colis():
    if request.method == 'POST':
        data = (
            request.form['nom'],
            request.form['ville_depart'],
            request.form['ville_arrivee'],
            request.form['poids'],
            request.form['date_envoi'],
            request.form['whatsapp']
        )
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO colis (nom, ville_depart, ville_arrivee, poids, date_envoi, whatsapp) VALUES (%s, %s, %s, %s, %s, %s)", data)
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('confirmation'))
    return render_template("envoi_colis.html")

@app.route('/inscription_transporteur', methods=['GET', 'POST'])
def inscription_transporteur():
    if request.method == 'POST':
        data = (
            request.form['nom'],
            request.form['ville'],
            request.form['whatsapp'],
            request.form['date_dispo']
        )
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO transporteurs (nom, ville, whatsapp, date_dispo) VALUES (%s, %s, %s, %s)", data)
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('confirmation'))
    return render_template("inscription_transporteur.html")

@app.route('/confirmation')
def confirmation():
    return render_template("confirmation.html")

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.form.get('Body', '').lower()
    if "bonjour" in incoming_msg:
        return "👋 Bonjour ! Bienvenue chez Askely Express. Tapez '1' pour envoyer un colis ou '2' pour devenir transporteur."
    return "Merci pour votre message."

if __name__ == '__main__':
    app.run(debug=True)
