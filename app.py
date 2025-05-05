import streamlit as st
st.set_page_config(page_title="Malnutrition App", layout="wide")

# ✅ Mobile-Friendly Styling + Meta Fix
st.markdown("""
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
    .main .block-container {
        padding-top: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    button[kind="primary"], .stButton > button {
        width: 100%;
        margin-top: 0.5rem;
    }

    .stTextInput > div > input, .stNumberInput input {
        font-size: 16px;
        padding: 0.75rem;
    }

    .stSelectbox > div {
        font-size: 16px;
    }

    .stDataFrame, .stTable {
        overflow-x: auto;
    }

    h1 {
        font-size: 1.8rem;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

import json
import os
import pandas as pd
import streamlit.components.v1 as components
from food_module import run_food_scanner
from arm_module import run_muac
from height_module import run_height_estimator

components.html("""
    <link rel="apple-touch-icon" sizes="180x180" href="https://raw.githubusercontent.com/mannitha/food_scanner_app/main/favicon.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="apple-mobile-web-app-title" content="My App">
""", height=0)

# Load user data
USER_DATA_FILE = "users.json"
def load_users():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DATA_FILE, "w") as f:
        json.dump(users, f)

# Load user session
def load_session():
    if "username" not in st.session_state:
        st.session_state.username = None
    if "is_logged_in" not in st.session_state:
        st.session_state.is_logged_in = False

# Auth
def login(users):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in users and users[username]["password"] == password:
            st.session_state.username = username
            st.session_state.is_logged_in = True
            st.success("Login successful!")
            st.experimental_rerun()
        else:
            st.error("Invalid credentials")

def signup(users):
    username = st.text_input("Choose a username")
    password = st.text_input("Choose a password", type="password")
    if st.button("Sign Up"):
        if username in users:
            st.error("Username already exists")
        else:
            users[username] = {"password": password}
            save_users(users)
            st.success("Signup successful! Please log in.")

# Data Storage
CHILD_DATA_FILE = "child_data.json"
FOOD_DATA_FILE = "food_data.json"

def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f)

# Main app
def main_app():
    st.title("🍎 Malnutrition Detection App")

    menu = ["👶 Child Nutrition", "🥗 NutriMann Food Scan", "🚪 Logout"]
    choice = st.sidebar.selectbox("Select Section", menu)

    if choice == "👶 Child Nutrition":
        st.subheader("👶 Enter Child Information")

        child_data = load_json(CHILD_DATA_FILE)

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Child's Name")
            age = st.number_input("Age (in years)", min_value=0.0, step=0.1)

        if name and age:
            if name not in child_data:
                child_data[name] = {"age": age}

            if st.button("Proceed to Height Estimation"):
                save_json(CHILD_DATA_FILE, child_data)
                st.session_state.child_name = name
                st.session_state.child_age = age
                st.session_state.page = "height"

        if "page" in st.session_state and st.session_state.page == "height":
            run_height_estimator(st.session_state.child_name, st.session_state.child_age, child_data)
            save_json(CHILD_DATA_FILE, child_data)
            st.session_state.page = "muac"

        if "page" in st.session_state and st.session_state.page == "muac":
            run_muac(st.session_state.child_name, st.session_state.child_age, child_data)
            save_json(CHILD_DATA_FILE, child_data)
            st.session_state.page = "summary"

        if "page" in st.session_state and st.session_state.page == "summary":
            st.subheader("📊 Summary")
            df = pd.DataFrame([child_data[st.session_state.child_name]])
            st.table(df)
            st.session_state.page = None  # Reset flow

        st.subheader("📁 View Previous Data")
        if child_data:
            selected = st.selectbox("Select Child", list(child_data.keys()))
            if selected:
                st.table(pd.DataFrame([child_data[selected]]))
        else:
            st.info("No data available.")

    elif choice == "🥗 NutriMann Food Scan":
        run_food_scanner()

    elif choice == "🚪 Logout":
        st.session_state.username = None
        st.session_state.is_logged_in = False
        st.success("Logged out successfully!")

# App Entry
def main():
    load_session()
    users = load_users()

    if not st.session_state.is_logged_in:
        st.title("🔐 Login or Signup")
        auth_mode = st.radio("Choose Option", ["Login", "Sign Up"])
        if auth_mode == "Login":
            login(users)
        else:
            signup(users)
    else:
        main_app()

if __name__ == "__main__":
    main()
