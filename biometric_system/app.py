import streamlit as st
from backend.auth import register, login
import sqlite3
import pandas as pd
import re

st.set_page_config(page_title="Quantum Secure System", layout="wide")

# ---------- STYLE ----------
st.markdown("""
<style>
body {background: linear-gradient(135deg,#141e30,#243b55);}
h1 {text-align:center;color:#00f5d4;}
.stButton>button {
background: linear-gradient(90deg,#00f5d4,#00bbf9);
color:black;border-radius:10px;font-weight:bold;
}
</style>
""", unsafe_allow_html=True)

st.title("🔐 Quantum Biometric Password System")

menu = st.radio("Menu", ["Register","Login","Database"], horizontal=True)

# ---------- PASSWORD STRENGTH ----------
def strength(p):
    score=0
    if len(p)>8: score+=1
    if re.search("[A-Z]",p): score+=1
    if re.search("[0-9]",p): score+=1
    if re.search("[!@#$%^&*]",p): score+=1
    return ["Weak","Medium","Strong","Very Strong"][score-1]

# ---------- REGISTER ----------
if menu=="Register":
    st.subheader("Create Password")

    username=st.text_input("Username")
    app=st.text_input("App Name")
    user_secret=st.text_input("PIN (Optional)",type="password")

    if st.button("Generate"):
        if username and app:
            password=register(username,app,user_secret)
            st.success("Generated")
            st.code(password)
            st.info("Strength: "+strength(password))
        else:
            st.error("Fill fields")

# ---------- LOGIN ----------
elif menu=="Login":
    st.subheader("Login")

    username=st.text_input("Username")
    app=st.text_input("App Name")
    user_secret=st.text_input("PIN (if used)",type="password")

    if st.button("Login"):
        success, res = login(username, app, user_secret)

        if success:
            st.success("Logged in")
            st.code(res)
        else:
            st.error(res)

# ---------- DATABASE ----------
else:
    st.subheader("Database")

    conn=sqlite3.connect("data/users.db")
    df=pd.read_sql_query("SELECT * FROM users",conn)
    st.dataframe(df)