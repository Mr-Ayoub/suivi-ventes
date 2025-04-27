from flask import Flask, render_template, request, redirect, flash, send_from_directory
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'ma_cle_ultra_secrete'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    ventes = conn.execute('SELECT * FROM ventes ORDER BY date_vente DESC').fetchall()
    conn.close()
    return render_template('index.html', ventes=ventes)

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
        photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
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

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)