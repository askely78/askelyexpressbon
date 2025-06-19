from flask import Flask, request, render_template, redirect
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

@app.route("/")
def index():
    return "👋 Bienvenue chez Askely Express ! Utilisez WhatsApp pour interagir."

# Formulaire envoi colis (HTML)
@app.route("/formulaire_colis")
def formulaire_colis():
    return render_template("envoi_colis.html")

@app.route("/submit_colis", methods=["POST"])
def submit_colis():
    nom = request.form["nom"]
    telephone = request.form["telephone"]
    ville_depart = request.form["ville_depart"]
    ville_arrivee = request.form["ville_arrivee"]
    date = request.form["date"]
    poids = request.form["poids"]

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("INSERT INTO colis (nom, telephone, ville_depart, ville_arrivee, date, poids) VALUES (%s, %s, %s, %s, %s, %s)", 
                (nom, telephone, ville_depart, ville_arrivee, date, poids))
    conn.commit()
    cur.close()
    conn.close()

    return "✅ Colis enregistré avec succès !"

# Formulaire inscription transporteur (HTML)
@app.route("/formulaire_transporteur")
def formulaire_transporteur():
    return render_template("inscription_transporteur.html")

@app.route("/submit_transporteur", methods=["POST"])
def submit_transporteur():
    nom = request.form["nom"]
    telephone = request.form["telephone"]
    ville = request.form["ville"]
    jours_dispo = request.form["jours_dispo"]

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("INSERT INTO transporteurs (nom, telephone, ville, jours_dispo) VALUES (%s, %s, %s, %s)", 
                (nom, telephone, ville, jours_dispo))
    conn.commit()
    cur.close()
    conn.close()

    return "✅ Transporteur enregistré avec succès !"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
