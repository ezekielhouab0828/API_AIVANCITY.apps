import mysql.connector
import streamlit as st

# ---------------------------------------------------------
# Connexion à la base MySQL
# ---------------------------------------------------------
def get_connection():
    try:
        return mysql.connector.connect(
            host=st.secrets["MYSQL_HOST"],
            user=st.secrets["MYSQL_USER"],
            password=st.secrets["MYSQL_PASSWORD"],
            database=st.secrets["MYSQL_DATABASE"],
            port=st.secrets["MYSQL_PORT"]
        )
    except mysql.connector.Error as e:
        st.error(f"Erreur de connexion MySQL : {e}")
        return None
# ---------------------------------------------------------
# SELECT MULTIPLE LIGNES
# ---------------------------------------------------------
def fetch_all(query, params=None):
    conn = get_connection()
    if conn is None:
        return []

    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# ---------------------------------------------------------
# SELECT UNE SEULE LIGNE
# ---------------------------------------------------------
def fetch_one(query, params=None):
    conn = get_connection()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute(query, params or ())
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row

# ---------------------------------------------------------
# INSERT / UPDATE / DELETE
# ---------------------------------------------------------
def execute_query(query, params=None):
    conn = get_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    cursor.execute(query, params or ())
    conn.commit()
    cursor.close()
    conn.close()
