
from flask import Flask, request, render_template, redirect
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "dbname=askely_express_db user=postgres password=postgres host=localhost")

def insert_data(query, data):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute(query, data)
    conn.commit()
    cur.close()
    conn.close()

@app.route("/")
def home():
    return "Bienvenue chez Askely Express!"

@app.route("/envoi_colis", methods=["GET", "POST"])
def envoi_colis():
    if request.method == "POST":
        nom = request.form["nom"]
        telephone = request.form["telephone"]
        ville_depart = request.form["ville_depart"]
        ville_arrivee = request.form["ville_arrivee"]
        date = request.form["date"]
        description = request.form["description"]
        insert_data("INSERT INTO colis (nom, telephone, ville_depart, ville_arrivee, date, description) VALUES (%s, %s, %s, %s, %s, %s)",
                    (nom, telephone, ville_depart, ville_arrivee, date, description))
        return redirect("/confirmation")
    return render_template("envoi_colis.html")

@app.route("/inscription_transporteur", methods=["GET", "POST"])
def inscription_transporteur():
    if request.method == "POST":
        nom = request.form["nom"]
        telephone = request.form["telephone"]
        ville = request.form["ville"]
        destinations = request.form["destinations"]
        jours = request.form["jours"]
        insert_data("INSERT INTO transporteurs (nom, telephone, ville, destinations, jours) VALUES (%s, %s, %s, %s, %s)",
                    (nom, telephone, ville, destinations, jours))
        return redirect("/confirmation")
    return render_template("inscription_transporteur.html")

@app.route("/confirmation")
def confirmation():
    return render_template("confirmation.html")

if __name__ == "__main__":
    app.run(debug=True)
