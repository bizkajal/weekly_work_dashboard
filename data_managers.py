import pandas as pd
import os
from config import CSV_FILE
import sqlite3



# data_managers.py

os.makedirs(".streamlit", exist_ok=True)

DB_FILE = ".streamlit/team_status.db"

TABLE_NAME = "updates"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        
        # Create main updates table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                task TEXT,
                status TEXT,
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
        conn.commit()

def add_user(username, password):
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists

def get_users():
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users")
        return dict(cursor.fetchall())



def load_data():
    """Load data from SQLite database into a DataFrame."""
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
        print("Data loaded from SQLite database:")
        print(df.head())
    return df

def save_data(df):
    """Overwrite all records in the SQLite database."""
    with sqlite3.connect(DB_FILE) as conn:
        df = df.dropna(subset=["name", "task", "status"])
        expected_columns = ["name", "task", "status", "start_date", "eta", "remarks"]
        df = df[expected_columns]
        df["start_date"] = df["start_date"].astype(str)
        df["eta"] = df["eta"].astype(str)

        # Clear and rewrite the table
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {TABLE_NAME}")
        df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)


        # df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

# def load_data():
#     if os.path.exists(CSV_FILE):
#         return pd.read_csv(CSV_FILE)
#     else:
#         columns = ["Name", "Task", "Status", "Start Date", "eta", "remarks"]
#         return pd.DataFrame(columns=columns)

# def save_data(df):
#     df.to_csv(CSV_FILE, index=False)
