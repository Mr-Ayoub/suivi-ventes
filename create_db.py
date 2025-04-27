import sqlite3

conn = sqlite3.connect('database.db')
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

print("✅ Base de données créée avec succès !")