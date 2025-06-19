from flask import Flask, request, render_template, redirect
import psycopg2
import os

app = Flask(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

@app.route("/")
def home():
    return "✅ Askely Express est en ligne."

@app.route("/envoi-colis")
def envoi_colis():
    return render_template("envoi_colis.html")

@app.route("/inscription-transporteur")
def inscription_transporteur():
    return render_template("inscription_transporteur.html")

@app.route("/submit_colis", methods=["POST"])
def submit_colis():
    try:
        data = (
            request.form["nom"],
            request.form["telephone"],
            request.form["ville_depart"],
            request.form["ville_arrivee"],
            request.form["date_envoi"],
            request.form["description"]
        )
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("INSERT INTO colis (nom, telephone, ville_depart, ville_arrivee, date_envoi, description) VALUES (%s, %s, %s, %s, %s, %s)", data)
        conn.commit()
        cur.close()
        conn.close()
        return "✅ Colis enregistré avec succès."
    except Exception as e:
        return f"Erreur : {e}"

@app.route("/submit_transporteur", methods=["POST"])
def submit_transporteur():
    try:
        data = (
            request.form["nom"],
            request.form["telephone"],
            request.form["ville_depart"],
            request.form["ville_arrivee"],
            request.form["jours_disponibles"]
        )
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("INSERT INTO transporteurs (nom, telephone, ville_depart, ville_arrivee, jours_disponibles) VALUES (%s, %s, %s, %s, %s)", data)
        conn.commit()
        cur.close()
        conn.close()
        return "✅ Transporteur inscrit avec succès."
    except Exception as e:
        return f"Erreur : {e}"
