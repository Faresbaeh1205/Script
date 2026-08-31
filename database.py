import sqlite3
import pandas as pd
from typing import Dict, Any

class DatabaseManager:
    def __init__(self, db_name: str = "scraped_data.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        """Initialise la table SQLite pour stocker les produits."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    price TEXT,
                    status TEXT,
                    url TEXT UNIQUE,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_product(self, prod: Dict[str, Any]):
        """Enregistre un produit extrait en temps réel."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO products (title, price, status, url)
                VALUES (?, ?, ?, ?)
            """, (
                prod.get("title", "N/A"),
                prod.get("price", "N/A"),
                prod.get("status", "N/A"),
                prod.get("url", "")
            ))
            conn.commit()

    def export_to_excel(self, output_path: str = "export_produits.xlsx"):
        """Exporte la BDD vers un fichier Excel."""
        with sqlite3.connect(self.db_name) as conn:
            df = pd.read_sql_query("SELECT title, price, status, url, scraped_at FROM products", conn)
            df.to_excel(output_path, index=False, engine="openpyxl")
