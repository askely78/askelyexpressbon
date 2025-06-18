
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os

app = Flask(__name__)

# Variables de session utilisateur (temporaire, à améliorer pour production)
user_sessions = {}

@app.route("/webhook/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip().lower()
    sender = request.values.get("From")
    response = MessagingResponse()
    msg = response.message()

    # Initialiser session utilisateur
    if sender not in user_sessions:
        user_sessions[sender] = {"state": "menu"}

    # Afficher menu si "menu" ou première fois
    if incoming_msg in ["menu", "bonjour", "salut", "hello"] or user_sessions[sender]["state"] == "menu":
        msg.body(
            "👋 Bienvenue chez *Askely Express* !
"
            "Que souhaitez-vous faire ?
"
            "1. 📦 Envoyer un colis
"
            "2. 🚚 Devenir transporteur
"
            "3. 📋 Voir les demandes"
        )
        user_sessions[sender]["state"] = "waiting_choice"
        return str(response)

    # Traitement du choix
    if user_sessions[sender]["state"] == "waiting_choice":
        if "1" in incoming_msg or "envoyer" in incoming_msg:
            user_sessions[sender]["state"] = "colis_nom_expediteur"
            msg.body("📦 Très bien. Pour envoyer un colis, merci de fournir le *nom de l’expéditeur* :")
        elif "2" in incoming_msg or "transporteur" in incoming_msg:
            user_sessions[sender]["state"] = "transporteur_nom"
            msg.body("🚚 Bienvenue transporteur ! Quel est votre *nom complet* ?")
        elif "3" in incoming_msg or "demande" in incoming_msg:
            msg.body("📋 Fonctionnalité des demandes à venir. Merci de patienter.")
        else:
            msg.body("❌ Option non reconnue. Répondez par 1, 2 ou 3.")
        return str(response)

    # Flux : envoi de colis
    if user_sessions[sender]["state"] == "colis_nom_expediteur":
        user_sessions[sender]["nom_expediteur"] = incoming_msg
        user_sessions[sender]["state"] = "colis_nom_destinataire"
        msg.body("🧍‍♀️ Nom du destinataire :")
        return str(response)
    if user_sessions[sender]["state"] == "colis_nom_destinataire":
        user_sessions[sender]["nom_destinataire"] = incoming_msg
        user_sessions[sender]["state"] = "colis_ville_depart"
        msg.body("📍 Ville de départ :")
        return str(response)
    if user_sessions[sender]["state"] == "colis_ville_depart":
        user_sessions[sender]["ville_depart"] = incoming_msg
        user_sessions[sender]["state"] = "colis_ville_arrivee"
        msg.body("🏁 Ville d’arrivée :")
        return str(response)
    if user_sessions[sender]["state"] == "colis_ville_arrivee":
        user_sessions[sender]["ville_arrivee"] = incoming_msg
        user_sessions[sender]["state"] = "colis_description"
        msg.body("📦 Description du colis :")
        return str(response)
    if user_sessions[sender]["state"] == "colis_description":
        user_sessions[sender]["description"] = incoming_msg
        user_sessions[sender]["state"] = "colis_date"
        msg.body("📅 Date souhaitée d’envoi :")
        return str(response)
    if user_sessions[sender]["state"] == "colis_date":
        user_sessions[sender]["date_envoi"] = incoming_msg
        user_sessions[sender]["state"] = "menu"
        msg.body("✅ Colis enregistré ! Nous vous mettons en relation avec un transporteur disponible. Tapez *menu* pour revenir au menu.")
        return str(response)

    # Flux : inscription transporteur
    if user_sessions[sender]["state"] == "transporteur_nom":
        user_sessions[sender]["transporteur_nom"] = incoming_msg
        user_sessions[sender]["state"] = "transporteur_numero"
        msg.body("📞 Numéro WhatsApp :")
        return str(response)
    if user_sessions[sender]["state"] == "transporteur_numero":
        user_sessions[sender]["transporteur_numero"] = incoming_msg
        user_sessions[sender]["state"] = "transporteur_ville"
        msg.body("📍 Ville actuelle :")
        return str(response)
    if user_sessions[sender]["state"] == "transporteur_ville":
        user_sessions[sender]["transporteur_ville"] = incoming_msg
        user_sessions[sender]["state"] = "transporteur_moyen"
        msg.body("🚚 Moyen de transport (voiture, moto, etc.) :")
        return str(response)
    if user_sessions[sender]["state"] == "transporteur_moyen":
        user_sessions[sender]["transporteur_moyen"] = incoming_msg
        user_sessions[sender]["state"] = "transporteur_dispo"
        msg.body("🗓️ Disponibilités (jours, horaires) :")
        return str(response)
    if user_sessions[sender]["state"] == "transporteur_dispo":
        user_sessions[sender]["transporteur_dispo"] = incoming_msg
        user_sessions[sender]["state"] = "menu"
        msg.body("✅ Merci ! Vous êtes inscrit comme transporteur. Tapez *menu* pour recommencer.")
        return str(response)

    # Message non compris
    msg.body("❓ Je n’ai pas compris votre message. Tapez *menu* pour recommencer.")
    return str(response)

if __name__ == "__main__":
    app.run(debug=True)
