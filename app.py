from flask import Flask, render_template, request, redirect, flash, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'ma_cle_ultra_secrete'  # Clé secrète pour le flash message
UPLOAD_FOLDER = 'uploads'
DATABASE = 'database.db'

# Créer les dossiers nécessaires si non existants
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialiser la base de données si elle n'existe pas
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ventes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client TEXT NOT NULL,
                produit TEXT NOT NULL,
                quantite REAL NOT NULL,
                prix_unitaire REAL NOT NULL,
                montant_total REAL NOT NULL,
                montant_paye REAL NOT NULL,
                reste REAL NOT NULL,
                photo TEXT,
                date_vente TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

# Fonction pour ouvrir une connexion à la base de données
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Route principale (page d'accueil)
@app.route('/')
def index():
    init_db()  # Vérifier et créer la base si nécessaire
    conn = get_db_connection()
    ventes = conn.execute('SELECT * FROM ventes ORDER BY date_vente DESC').fetchall()
    conn.close()
    return render_template('index.html', ventes=ventes)

# Route pour ajouter une vente
@app.route('/add', methods=['POST'])
def add():
    client = request.form['client']
    produit = request.form['produit']
    quantite = float(request.form['quantite'])
    prix_unitaire = float(request.form['prix_unitaire'])
    montant_paye = float(request.form['montant_paye'])

    montant_total = quantite * prix_unitaire
    reste = montant_total - montant_paye

    photo_file = request.files['photo']
    if photo_file and photo_file.filename != '':
        filename = secure_filename(photo_file.filename)
        photo_path = os.path.join(UPLOAD_FOLDER, filename)
        photo_file.save(photo_path)
    else:
        filename = None

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO ventes (client, produit, quantite, prix_unitaire, montant_total, montant_paye, reste, photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (client, produit, quantite, prix_unitaire, montant_total, montant_paye, reste, filename))
    conn.commit()
    conn.close()

    flash('✅ Vente ajoutée avec succès !')
    return redirect('/')

# Route pour servir les fichiers uploadés (photos)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Démarrer l'application
if __name__ == '__main__':
    app.run(debug=True)
