import pandas as pd
import os
import sqlite3
from config import CSV_FILE

os.makedirs(".streamlit", exist_ok=True)
DB_FILE = ".streamlit/team_status.db"
TABLE_NAME = "updates"
CERT_TABLE = "certifications"


def init_db():
    """Initialize the SQLite database and create necessary tables."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Create main updates table
        cursor.execute(f"""
                       
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                name TEXT NOT NULL,
                task TEXT,
                category TEXT,
                status TEXT,
                weightage REAL,
                start_date TEXT,
                eta TEXT,
                remarks TEXT
            )
        """)

        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)

        # Create certifications table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {CERT_TABLE} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                certification TEXT,
                status TEXT,
                cert_file TEXT,
                exam_date TEXT
            )
        """)

        conn.commit()


def add_user(username, password):
    """Add a new user to the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def get_users():
    """Retrieve all users from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users")
        return dict(cursor.fetchall())


def load_data():
    """Load data from SQLite database into a DataFrame."""
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    return df


def save_data(df):
    """Overwrite all records in the SQLite database."""
    with sqlite3.connect(DB_FILE) as conn:
        df = df.dropna(subset=["name", "task", "status"])
        expected_columns = ["name", "task", "category", "status", "weightage", "start_date", "eta", "remarks"]
        df = df[expected_columns]
        df["start_date"] = df["start_date"].astype(str)
        df["eta"] = df["eta"].astype(str)

        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {TABLE_NAME}")
        df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)
