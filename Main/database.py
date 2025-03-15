import sqlite3
import logging
import traceback
from datetime import datetime
from config import DATABASE_PATH

def setup_database():
    """Set up the SQLite database and create necessary tables."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users
                              (id TEXT PRIMARY KEY, password TEXT, is_admin INTEGER DEFAULT 0)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS footprints
                              (id INTEGER PRIMARY KEY AUTOINCREMENT,
                               user_id TEXT, electricity REAL, gas REAL, fuel REAL,
                               waste REAL, recycling REAL, travel REAL,
                               efficiency REAL, footprint REAL, date TEXT)''')
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_id ON footprints (user_id)")
            conn.commit()
    except sqlite3.Error as error:
        logging.error(f"Database setup error: {error}\n{traceback.format_exc()}")
        raise

def save_to_db(user_id: str, electricity: float, gas: float, fuel: float, waste: float,
               recycling: float, travel: float, efficiency: float, footprint: float):
    """Save user inputs and calculated footprint to the database."""
    try:
        with sqlite3.connect(DATABASE_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO footprints
                              (user_id, electricity, gas, fuel, waste, recycling, travel, efficiency, footprint, date)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                           (user_id, electricity, gas, fuel, waste, recycling, travel, efficiency, footprint,
                            datetime.now().strftime('%Y-%m-%d')))
            conn.commit()
    except sqlite3.Error as error:
        logging.error(f"Database save error for user {user_id}: {error}\n{traceback.format_exc()}")
        raise