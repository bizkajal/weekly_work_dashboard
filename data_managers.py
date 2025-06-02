import pandas as pd
import os
from config import CSV_FILE
import sqlite3



# data_managers.py

os.makedirs(".streamlit", exist_ok=True)

DB_FILE = ".streamlit/team_status.db"


# DB_FILE = "team_status.db"
TABLE_NAME = "updates"

def init_db():
    """Initialize the SQLite database and table if it doesn't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        # cursor = conn.cursor()
        # cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        # conn.commit()


         
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                task TEXT ,
                status TEXT ,
                start_date TEXT ,
                eta TEXT ,
                remarks TEXT
            )
        """)
        conn.commit()


def load_data():
    """Load data from SQLite database into a DataFrame."""
    with sqlite3.connect(DB_FILE) as conn:
        df = pd.read_sql_query(f"SELECT * FROM {TABLE_NAME}", conn)
    return df
def save_data(df):
    """Append new updates to the SQLite database safely."""
    with sqlite3.connect(DB_FILE) as conn:
        # Drop rows with missing required fields
        df = df.dropna(subset=["Name", "Task", "Status"])

        # Ensure columns are in correct order to match DB schema
        expected_columns = ["Name", "Task", "Status", "start_date", "ETA", "Remarks"]
        df = df[expected_columns]

        # Convert date columns to string if necessary
        df["start_date"] = df["start_date"].astype(str)
        df["ETA"] = df["ETA"].astype(str)

        # Now safely insert into SQLite
        df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)


        # df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

# def load_data():
#     if os.path.exists(CSV_FILE):
#         return pd.read_csv(CSV_FILE)
#     else:
#         columns = ["Name", "Task", "Status", "Start Date", "ETA", "Remarks"]
#         return pd.DataFrame(columns=columns)

# def save_data(df):
#     df.to_csv(CSV_FILE, index=False)
