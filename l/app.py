
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def accueil():
    return "Bienvenue sur Askely Express"

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
