import os
import psycopg2
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI                    # ✅ nouveau

# Initialisation client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

def repondre_avec_ia(msg_user: str) -> str:
    try:
        completion = client.chat.completions.create(   # ✅ nouvelle syntaxe
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Tu es Askely Express, assistant de livraison."},
                {"role": "user", "content": msg_user}
            ]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Erreur IA : {e}"

@app.route("/webhook/whatsapp", methods=["POST"])
def webhook():
    incoming = request.values.get("Body", "").strip()
    resp = MessagingResponse()
    resp.message(repondre_avec_ia(incoming))
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
