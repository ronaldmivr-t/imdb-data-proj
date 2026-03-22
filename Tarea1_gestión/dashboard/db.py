import mysql.connector
import pandas as pd
import streamlit as st

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Srg270604*",
    "database": "peliculas"
}

@st.cache_resource
def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

def query_to_df(query: str) -> pd.DataFrame:
    conn = get_connection()
    try:
        conn.ping(reconnect=True, attempts=3, delay=2)
    except:
        pass

    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return pd.DataFrame(rows)