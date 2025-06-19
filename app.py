from flask import Flask, request, render_template, redirect
from twilio.twiml.messaging_response import MessagingResponse
import psycopg2
import os

app = Flask(__name__)

# Connexion PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")

def connect_db():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def index():
    return "Askely Express est en ligne."

@app.route("/webhook/whatsapp", methods=["POST"])
def webhook_whatsapp():
    incoming_msg = request.values.get('Body', '').strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    if "bonjour" in incoming_msg or "salut" in incoming_msg:
        msg.body("👋 Bienvenue chez *Askely Express* !\n\n🚚 Pour envoyer un colis, tapez *1*\n📦 Pour devenir transporteur, tapez *2*\n📍 Pour suivre un colis, tapez *3*\n\nQue souhaitez-vous faire ?")
    elif incoming_msg == "1":
        msg.body("📦 Cliquez ici pour remplir le formulaire d’envoi :\nhttps://askelyexpressbon.onrender.com/envoi_colis")
    elif incoming_msg == "2":
        msg.body("🚚 Cliquez ici pour vous inscrire comme transporteur :\nhttps://askelyexpressbon.onrender.com/inscription_transporteur")
    elif incoming_msg == "3":
        msg.body("🔍 Veuillez entrer le *numéro de suivi* pour consulter l’état de votre colis.")
    else:
        msg.body("❓ Je n’ai pas compris. Veuillez choisir une option du menu ou tapez *bonjour* pour le menu.")

    return str(resp)

@app.route("/envoi_colis")
def envoi_colis():
    return render_template("envoi_colis.html")

@app.route("/inscription_transporteur")
def inscription_transporteur():
    return render_template("inscription_transporteur.html")

@app.route("/submit_colis", methods=["POST"])
def submit_colis():
    nom = request.form["nom"]
    telephone = request.form["telephone"]
    ville_depart = request.form["ville_depart"]
    ville_arrivee = request.form["ville_arrivee"]
    date_envoi = request.form["date_envoi"]
    contenu = request.form["contenu"]

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO colis (nom, telephone, ville_depart, ville_arrivee, date_envoi, contenu)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nom, telephone, ville_depart, ville_arrivee, date_envoi, contenu))
    conn.commit()
    cur.close()
    conn.close()

    return render_template("confirmation.html", message="✅ Colis enregistré avec succès !")

@app.route("/submit_transporteur", methods=["POST"])
def submit_transporteur():
    nom = request.form["nom"]
    telephone = request.form["telephone"]
    ville_depart = request.form["ville_depart"]
    ville_arrivee = request.form["ville_arrivee"]
    date_disponible = request.form["date_disponible"]

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transporteurs (nom, telephone, ville_depart, ville_arrivee, date_disponible)
        VALUES (%s, %s, %s, %s, %s)
    """, (nom, telephone, ville_depart, ville_arrivee, date_disponible))
    conn.commit()
    cur.close()
    conn.close()

    return render_template("confirmation.html", message="✅ Transporteur inscrit avec succès !")

if __name__ == "__main__":
    app.run(debug=True)
