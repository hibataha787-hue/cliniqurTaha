"""
Script de migration SQLite - Ajoute les nouvelles colonnes à patient_profile.
Lancer SANS le serveur Flask en cours.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'clinic.db')
if not os.path.exists(DB_PATH):
    # Essayer à la racine
    DB_PATH = os.path.join(os.path.dirname(__file__), 'clinic.db')
    if not os.path.exists(DB_PATH):
        # Chercher automatiquement
        for root, dirs, files in os.walk(os.path.dirname(__file__)):
            for f in files:
                if f.endswith('.db'):
                    DB_PATH = os.path.join(root, f)
                    break

print(f"Base de données trouvée : {DB_PATH}")

new_columns = [
    ("profession",      "VARCHAR(100)"),
    ("ville",           "VARCHAR(100)"),
    ("mode_de_vie",     "VARCHAR(100)"),
    ("preference",      "VARCHAR(255)"),
    ("liked_recipes",   "TEXT"),
    ("disliked_recipes","TEXT"),
    ("meals_per_day",   "INTEGER"),
    ("waist_size",      "REAL"),
    ("allergies",       "TEXT"),
    ("remarks",         "TEXT"),
]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Récupérer les colonnes existantes
cursor.execute("PRAGMA table_info(patient_profile)")
existing = {row[1] for row in cursor.fetchall()}
print(f"Colonnes existantes : {existing}")

for col_name, col_type in new_columns:
    if col_name not in existing:
        try:
            cursor.execute(f"ALTER TABLE patient_profile ADD COLUMN {col_name} {col_type}")
            print(f"  ✅ Colonne ajoutée : {col_name}")
        except Exception as e:
            print(f"  ❌ Erreur pour {col_name}: {e}")
    else:
        print(f"  ⚠️  Déjà existante : {col_name}")

conn.commit()
conn.close()
print("\nMigration terminée!")
