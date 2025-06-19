from flask import Flask, render_template, request, redirect, url_for
from twilio.twiml.messaging_response import MessagingResponse

app = Flask(__name__)

@app.route('/')
def accueil():
    return "Bienvenue sur Askely Express"

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    incoming_msg = request.form.get("Body", "").strip().lower()
    resp = MessagingResponse()
    msg = resp.message()

    if incoming_msg in ["bonjour", "salut", "hello", "hi"]:
        msg.body("👋 Bonjour et bienvenue chez *Askely Express* !\n\n📦 Pour envoyer un colis, tapez *1*\n🚚 Pour devenir transporteur, tapez *2*\n📬 Pour suivre un colis, tapez *3*\n👀 Pour voir les transporteurs disponibles, tapez *4*")
    elif incoming_msg == "1":
        msg.body("👉 Veuillez remplir ce formulaire pour envoyer un colis :\nhttps://askelyexpressbon.onrender.com/envoi_colis")
    elif incoming_msg == "2":
        msg.body("🚚 Devenez transporteur ici :\nhttps://askelyexpressbon.onrender.com/inscription_transporteur")
    elif incoming_msg == "3":
        msg.body("📦 Suivi de colis : fonctionnalité bientôt disponible.")
    elif incoming_msg == "4":
        msg.body("📍 Liste des transporteurs disponibles : bientôt accessible.")
    else:
        msg.body("❓ Je n’ai pas compris votre demande. Veuillez répondre avec un numéro (1 à 4) ou 'bonjour'.")
    
    return str(resp)

@app.route('/envoi_colis', methods=['GET', 'POST'])
def envoi_colis():
    if request.method == 'POST':
        print(request.form)
        return redirect(url_for('confirmation'))
    return render_template('envoi_colis.html')

@app.route('/inscription_transporteur', methods=['GET', 'POST'])
def inscription_transporteur():
    if request.method == 'POST':
        print(request.form)
        return redirect(url_for('confirmation'))
    return render_template('inscription_transporteur.html')

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

if __name__ == '__main__':
    app.run(debug=True)
