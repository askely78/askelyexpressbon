
from flask import Flask, request, render_template, redirect
import psycopg2
import os
from twilio.rest import Client

app = Flask(__name__)

# Connexion à la base PostgreSQL
conn = psycopg2.connect(os.environ["DATABASE_URL"])
cursor = conn.cursor()

# Clés Twilio
TWILIO_ACCOUNT_SID = os.environ["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = os.environ["TWILIO_AUTH_TOKEN"]
TWILIO_WHATSAPP_FROM = os.environ["TWILIO_WHATSAPP_FROM"]
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/colis", methods=["GET", "POST"])
def colis():
    if request.method == "POST":
        expediteur = request.form["expediteur"]
        destinataire = request.form["destinataire"]
        ville_depart = request.form["ville_depart"]
        ville_arrivee = request.form["ville_arrivee"]
        date = request.form["date"]
        transporteur_id = request.form["transporteur_id"]

        cursor.execute(
            "INSERT INTO colis (expediteur, destinataire, ville_depart, ville_arrivee, date, transporteur_id) VALUES (%s, %s, %s, %s, %s, %s)",
            (expediteur, destinataire, ville_depart, ville_arrivee, date, transporteur_id),
        )
        conn.commit()

        # Récupération du numéro WhatsApp du transporteur
        cursor.execute("SELECT nom, telephone FROM transporteurs WHERE id = %s", (transporteur_id,))
        result = cursor.fetchone()
        if result:
            nom_transporteur, telephone = result
            message = f"""
📦 Nouvelle demande d’envoi de colis !
✅ Expéditeur : {expediteur}
✅ Destinataire : {destinataire}
🛫 De : {ville_depart}
🛬 À : {ville_arrivee}
📅 Date : {date}
👉 Contacte l’expéditeur pour convenir de la remise.
"""
            client.messages.create(
                body=message,
                from_=f"whatsapp:{TWILIO_WHATSAPP_FROM}",
                to=f"whatsapp:{telephone}"
            )

        return redirect("/colis")

    cursor.execute("SELECT id, nom FROM transporteurs")
    transporteurs = cursor.fetchall()
    return render_template("liste_colis.html", transporteurs=transporteurs)

@app.route("/transporteurs")
def transporteurs():
    cursor.execute("SELECT * FROM transporteurs")
    rows = cursor.fetchall()
    return render_template("liste_transporteurs.html", transporteurs=rows)

if __name__ == "__main__":
    app.run()
