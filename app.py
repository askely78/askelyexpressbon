from flask import Flask, request, render_template
from twilio.twiml.messaging_response import MessagingResponse
import psycopg2
import os

app = Flask(__name__)

# Connexion à PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# === ROUTE PRINCIPALE WEBHOOK ===
@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.values.get('Body', '').strip().lower()
    response = MessagingResponse()
    msg = response.message()

    if "colis" in incoming_msg:
        msg.body("📝 Pour envoyer un colis, veuillez remplir ce formulaire sécurisé :\n👉 https://askelyexpressbon.onrender.com/envoi_colis")
    elif "transporteur" in incoming_msg or "devenir" in incoming_msg:
        msg.body("🚗 Pour devenir transporteur, merci de remplir ce formulaire :\n👉 https://askelyexpressbon.onrender.com/inscription_transporteur")
    elif "suivi" in incoming_msg:
        msg.body("📦 Pour suivre un colis, entrez votre numéro de suivi ou contactez Askely.")
    else:
        msg.body("""👋 *Bienvenue chez Askely Express !*
Voici ce que je peux faire pour vous :

1️⃣ *Envoyer un colis*  
2️⃣ *Devenir transporteur*  
3️⃣ *Suivre un colis*

✍️ Répondez simplement avec un mot-clé : `colis`, `transporteur` ou `suivi`""")

    return str(response)

# === FORMULAIRES HTML ===
@app.route('/envoi_colis', methods=['GET', 'POST'])
def envoi_colis():
    if request.method == 'POST':
        nom = request.form['nom']
        tel = request.form['tel']
        ville_depart = request.form['ville_depart']
        ville_arrivee = request.form['ville_arrivee']
        date_envoi = request.form['date_envoi']
        contenu = request.form['contenu']

        cursor.execute(
            "INSERT INTO colis (nom, tel, ville_depart, ville_arrivee, date_envoi, contenu) VALUES (%s, %s, %s, %s, %s, %s)",
            (nom, tel, ville_depart, ville_arrivee, date_envoi, contenu)
        )
        conn.commit()

        return "✅ Votre demande d'envoi a été enregistrée. Vous serez bientôt contacté."
    return render_template('envoi_colis.html')

@app.route('/inscription_transporteur', methods=['GET', 'POST'])
def inscription_transporteur():
    if request.method == 'POST':
        nom = request.form['nom']
        tel = request.form['tel']
        ville = request.form['ville']
        vehicule = request.form['vehicule']
        jours_disponibles = request.form['jours_disponibles']

        cursor.execute(
            "INSERT INTO transporteurs (nom, tel, ville, vehicule, jours_disponibles) VALUES (%s, %s, %s, %s, %s)",
            (nom, tel, ville, vehicule, jours_disponibles)
        )
        conn.commit()

        return "✅ Merci pour votre inscription. Nous vous contacterons pour les envois."
    return render_template('inscription_transporteur.html')

# === PAGE D’ACCUEIL TEST ===
@app.route('/')
def home():
    return "Bienvenue sur Askely Express – API WhatsApp opérationnelle."

if __name__ == '__main__':
    app.run()
