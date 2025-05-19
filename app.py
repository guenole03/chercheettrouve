from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'votreclefifiquesecurisee'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chercheettrouve.db'
db = SQLAlchemy(app)

class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pseudo = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    contact = db.Column(db.String(100), nullable=False)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'))

@app.route('/')
def index():
    produits = Produit.query.all()
    return render_template('index.html', produits=produits)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if Utilisateur.query.filter_by(pseudo=pseudo).first():
            return "Pseudo déjà pris"
        utilisateur = Utilisateur(pseudo=pseudo, email=email, password=password)
        db.session.add(utilisateur)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        password = request.form['password']
        utilisateur = Utilisateur.query.filter_by(pseudo=pseudo).first()
        if utilisateur and check_password_hash(utilisateur.password, password):
            session['pseudo'] = pseudo
            session['user_id'] = utilisateur.id
            return redirect('/dashboard')
        else:
            return "Identifiants invalides"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    produits = Produit.query.filter_by(utilisateur_id=session['user_id']).all()
    return render_template('dashboard.html', produits=produits)

@app.route('/ajouter', methods=['GET', 'POST'])
def ajouter():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        titre = request.form['titre']
        description = request.form['description']
        contact = request.form['contact']
        produit = Produit(titre=titre, description=description, contact=contact, utilisateur_id=session['user_id'])
        db.session.add(produit)
        db.session.commit()
        return redirect('/dashboard')
    return render_template('ajouter.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    import os

port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)
Fix port for Render
