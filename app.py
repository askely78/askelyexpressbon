from flask import Flask, request, render_template
import psycopg2
import os

app = Flask(__name__)

# Connexion PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transporteurs')
def liste_transporteurs():
    cur.execute("SELECT nom, tel FROM transporteurs")
    data = cur.fetchall()
    return render_template('liste_transporteurs.html', transporteurs=data)

@app.route('/colis')
def liste_colis():
    cur.execute("SELECT expediteur, destinataire, statut FROM colis")
    data = cur.fetchall()
    return render_template('liste_colis.html', colis=data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)