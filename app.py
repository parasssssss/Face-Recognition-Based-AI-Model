import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# Auto-refresh every 10 seconds
st_autorefresh(interval=10 * 1000, key="datarefresh")

# Database connection
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   
        database="face_security"   
    )

# Fetch data
def fetch_logs(start_date=None, end_date=None):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT id, name, time, status, image_path FROM access_log"
    params = ()

    if start_date and end_date:
        query += " WHERE time BETWEEN %s AND %s"
        params = (start_date, end_date)

    cursor.execute(query, params)
    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows

# Streamlit UI
st.title("Intruder Detection Dashboard")

# Date filter
st.sidebar.header("Filter by Date")
start_date = st.sidebar.date_input("Start Date", None)
end_date = st.sidebar.date_input("End Date", None)

# Fetch logs with filters
if start_date and end_date:
    logs = fetch_logs(str(start_date) + " 00:00:00", str(end_date) + " 23:59:59")
else:
    logs = fetch_logs()

# Convert to DataFrame
if logs:
    df = pd.DataFrame(logs)

    st.subheader("Access Logs")
    st.dataframe(df.drop(columns=["image_path"]))  

    st.subheader("Intruder Images")
    intruder_logs = df[df["image_path"].notnull()]

    if not intruder_logs.empty:
        for _, row in intruder_logs.iterrows():
            st.write(f"**ID:** {row['id']} | **Name:** {row['name']} | **Time:** {row['time']} | **Status:** {row['status']}")
            st.image(row["image_path"], width=300)
    else:
        st.info("No intruder images in the selected range.")
else:
    st.warning("No records found in the database.")
