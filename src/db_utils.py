# db_utils.py
import mysql.connector
from datetime import datetime

# Connect to database
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",        
        password="",        
        database="face_security"  
    )

# Insert log with optional image path
def insert_log(name, status, img_path=None):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO access_log (name, status, image_path, time)
        VALUES (%s, %s, %s, NOW())
    """
    cursor.execute(query, (name, status, img_path))
    conn.commit()
    conn.close()
