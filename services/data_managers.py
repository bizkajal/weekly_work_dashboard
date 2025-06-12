import pandas as pd
import os
import sqlite3
from config import CSV_FILE

os.makedirs(".streamlit", exist_ok=True)
DB_FILE = ".streamlit/team_status.db"
TABLE_NAME = "updates"
CERT_TABLE = "certifications"
ADMIN_TABLE = "admin_creds"

def init_db():
    """Initialize the SQLite database and create necessary tables."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Create main updates table
        cursor.execute(f"""
                       
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                rowId INTEGER PRIMARY KEY AUTOINCREMENT, 
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
                rowId INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT NOT NULL
            )
        """)

        # Create certifications table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {CERT_TABLE} (
                rowId INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                certification TEXT,
                status TEXT,
                cert_file TEXT,
                exam_date TEXT
            )
        """)

        # Create tables only for admin users
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {ADMIN_TABLE} (
                rowId INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                password TEXT NOT NULL
            )
        """)

        conn.commit()


def add_user(username, password):
    """Add a new user to the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False


def get_users():
    """Retrieve all users from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users;")
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
        expected_columns = [
            "name",
            "task",
            "category",
            "status",
            "weightage",
            "start_date",
            "eta",
            "remarks",
        ]
        df = df[expected_columns]
        df["start_date"] = df["start_date"].astype(str)
        df["eta"] = df["eta"].astype(str)

        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {TABLE_NAME}")
        df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)


def run_sqlite_query(query, params=None):
    """
    Execute any SQL query on a SQLite DB.

    Args:
        db_path (str): Path to the SQLite database file.
        query (str): The SQL query string.
        params (tuple or list, optional): Parameters to bind to the SQL query.

    Returns:
        pd.DataFrame for SELECT queries, None for others.
    """
    try:
        with sqlite3.connect(DB_FILE) as conn:
            if query.strip().lower().startswith("select"):
                return pd.read_sql_query(query, conn, params=params)
            else:
                cursor = conn.cursor()
                cursor.execute(query, params or ())
                conn.commit()
                return None
    except sqlite3.Error as e:
        print(f"[SQLite Error] {e}")
        return None
    finally:
        conn.close()


def check_if_admin_login(user):
    check_admin_query = f"SELECT * FROM admin_creds where username='{user}'"
    df = run_sqlite_query(query=check_admin_query)
    if df.shape[0] > 0:
        return True
    return False