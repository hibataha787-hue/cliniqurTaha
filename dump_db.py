import sqlite3
import pandas as pd
import os

db_path = os.path.join('instance', 'clinic.db')

if not os.path.exists(db_path):
    print(f"Error: {db_path} not found.")
else:
    conn = sqlite3.connect(db_path)
    # Get all tables
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
    
    print("--- CONTENT OF clinic.db ---")
    for table in tables['name']:
        if table.startswith('sqlite_'): continue
        print(f"\nTable: {table}")
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table};", conn)
            if df.empty:
                print(" (Table is empty)")
            else:
                print(df.to_string(index=False))
        except Exception as e:
            print(f" Error reading table {table}: {e}")
    conn.close()
