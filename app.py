import os
import openai
import psycopg2
from flask import Flask, request, render_template
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

# Configuration OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Configuration PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = conn.cursor()

# Créer les tables si elles n'existent pas
cursor.execute('''
    CREATE TABLE IF NOT EXISTS colis (
        id SERIAL PRIMARY KEY,
        expediteur TEXT,
        destinataire TEXT,
        date_envoi DATE
    );
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS transporteurs (
        id SERIAL PRIMARY KEY,
        nom TEXT,
        ville TEXT,
        whatsapp TEXT
    );
''')
conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/colis')
def liste_colis():
    cursor.execute("SELECT * FROM colis ORDER BY date_envoi DESC LIMIT 10;")
    colis = cursor.fetchall()
    return render_template('liste_colis.html', colis=colis)

@app.route('/transporteurs')
def liste_transporteurs():
    cursor.execute("SELECT * FROM transporteurs ORDER BY ville ASC;")
    transporteurs = cursor.fetchall()
    return render_template('liste_transporteurs.html', transporteurs=transporteurs)

@app.route('/webhook/whatsapp', methods=['POST'])
def webhook_whatsapp():
    incoming_msg = request.values.get('Body', '').strip()
    user_number = request.values.get('From', '')

    # Appel OpenAI
    try:
        response_ai = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Tu es un assistant pour un service de livraison de colis appelé Askely Express."},
                {"role": "user", "content": incoming_msg}
            ]
        )
        reply = response_ai.choices[0].message['content'].strip()
    except Exception as e:
        reply = "❌ Désolé, une erreur est survenue avec l'IA."

    twilio_response = MessagingResponse()
    twilio_response.message(reply)
    return str(twilio_response)

if __name__ == '__main__':
    app.run(debug=True)
