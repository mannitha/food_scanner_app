import streamlit as st
st.set_page_config(page_title="Malnutrition App", layout="wide")

# ✅ Mobile-Friendly Styling
st.markdown("""
    <style>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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

import json, os
import pandas as pd
import streamlit.components.v1 as components
from food_module import run_food_scanner
from arm_module import run_muac
from height_module import run_height_estimator

# Meta and favicon
components.html("""
    <link rel="apple-touch-icon" sizes="180x180" href="https://raw.githubusercontent.com/mannitha/food_scanner_app/main/favicon.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="apple-mobile-web-app-title" content="My App">
""", height=0)

USER_DATA_FILE = "users.json"
def get_nutrition_file(): return f"nutrition_data_{st.session_state.username}.json"
def get_food_file(): return f"food_data_{st.session_state.username}.json"
def load_users(): return json.load(open(USER_DATA_FILE)) if os.path.exists(USER_DATA_FILE) else {}
def save_users(users): json.dump(users, open(USER_DATA_FILE, "w"))

def load_nutrition_data():
    file = get_nutrition_file()
    try:
        data = json.load(open(file)) if os.path.exists(file) else []
        return data if isinstance(data, list) else []
    except:
        return []

def save_nutrition_data(data): json.dump(data, open(get_nutrition_file(), "w"), indent=2)
def load_food_data(): return json.load(open(get_food_file())) if os.path.exists(get_food_file()) else []
def save_food_data(data): json.dump(data, open(get_food_file(), "w"), indent=2)

# Auth
def signup():
    st.title("🔐 Sign Up")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    e = st.text_input("Email")
    if st.button("Create Account"):
        users = load_users()
        if u in users: st.error("Username already exists.")
        else:
            users[u] = {"password": p, "email": e}
            save_users(users)
            st.success("Account created!")

def login():
    st.title("🔑 Login")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_users()
        if u not in users: st.error("Username doesn't exist.")
        elif users[u]["password"] != p: st.error("Incorrect password.")
        else:
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.page = "select_flow"

def logout(): st.session_state.clear()

def back_button():
    if st.button("⬅️ Back"):
        nav = {
            "nutrition_choices": "select_flow",
            "nutrimann_choices": "select_flow",
            "child_info": "nutrition_choices",
            "height": "child_info",
            "arm": "height",
            "done": "arm",
            "nutrimann_info": "nutrimann_choices",
            "food_only": "nutrimann_info",
            "food_summary": "food_only",
            "view_old_data": "nutrition_choices",
            "view_old_food": "nutrimann_choices",
            "edit_food_entry": "view_old_food"
        }
        st.session_state.page = nav.get(st.session_state.page, "select_flow")
        st.rerun()

def calculate_bmi(w, h): return round(w / ((h / 100) ** 2), 2) if w and h else None
def calculate_malnutrition_status(bmi, arm):
    if bmi is None or arm is None: return "Unknown"
    if bmi < 13 or arm < 11.5: return "Severe Acute Malnutrition"
    elif bmi < 14 or arm < 12.5: return "Moderate Acute Malnutrition"
    return "Normal"

# Flow pages
def select_flow_step():
    st.title("📋 Choose Flow")
    col1, col2 = st.columns(2)
    with col1: 
        if st.button("👶 Nutrition Detection"): st.session_state.page = "nutrition_choices"
    with col2: 
        if st.button("🍽 NutriMann (Food Scanner Only)"): st.session_state.page = "nutrimann_choices"

def nutrition_choices_step():
    st.title("🧒 Nutrition Menu")
    back_button()
    col1, col2 = st.columns(2)
    with col1: 
        if st.button("➕ New Entry"): st.session_state.page = "child_info"
::contentReference[oaicite:0]{index=0}
 
