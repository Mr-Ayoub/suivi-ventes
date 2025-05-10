from flask import Flask, render_template, request, redirect, flash, make_response, send_from_directory
import sqlite3
import os
from io import BytesIO
from werkzeug.utils import secure_filename
from xhtml2pdf import pisa

app = Flask(__name__)
app.secret_key = 'ma_cle_ultra_secrete'

# 📦 Base de données et dossier upload
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, 'database.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Créer la base si elle n'existe pas
def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS ventes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client TEXT NOT NULL,
                produit TEXT NOT NULL,
                quantite REAL,
                prix_unitaire REAL,
                montant_paye REAL,
                photo TEXT,
                date_vente TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    init_db()
    conn = get_db_connection()
    ventes = conn.execute('SELECT * FROM ventes ORDER BY client ASC, date_vente DESC').fetchall()
    conn.close()

    ventes_par_client = {}
    for v in ventes:
        client = v['client']
        if client not in ventes_par_client:
            ventes_par_client[client] = []
        ventes_par_client[client].append(v)

    return render_template('index.html', ventes_par_client=ventes_par_client)

@app.route('/add', methods=['POST'])
def add():
    client = request.form['client']
    produit = request.form['produit']
    quantite = float(request.form['quantite'])
    prix_unitaire = float(request.form['prix_unitaire'])
    montant_paye = float(request.form['montant_paye'])

    # Gestion du fichier reçu
    photo_file = request.files['photo']
    filename = None
    if photo_file and photo_file.filename != '':
        filename = secure_filename(photo_file.filename)
        photo_path = os.path.join(UPLOAD_FOLDER, filename)
        photo_file.save(photo_path)

    conn = get_db_connection()
    conn.execute('''
        INSERT INTO ventes (client, produit, quantite, prix_unitaire, montant_paye, photo)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (client, produit, quantite, prix_unitaire, montant_paye, filename))
    conn.commit()
    conn.close()

    flash('✅ Vente ajoutée avec succès !')
    return redirect('/')

@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM ventes WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    flash("❌ Vente supprimée avec succès.")
    return redirect('/')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/facture/<client>')
def facture(client):
    init_db()
    conn = get_db_connection()
    ventes = conn.execute('''
        SELECT * FROM ventes WHERE client = ? ORDER BY date_vente DESC
    ''', (client,)).fetchall()
    conn.close()

    total = sum(v['montant_paye'] for v in ventes)
    rendered = render_template('facture.html', client=client, ventes=ventes, total=total)

    pdf = BytesIO()
    pisa.CreatePDF(BytesIO(rendered.encode("utf-8")), dest=pdf)

    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=facture_{client}.pdf'
    return response

if __name__ == '__main__':
    app.run(debug=True)
