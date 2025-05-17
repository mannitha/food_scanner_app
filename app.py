import streamlit as st
import json, os
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components
from food_module import run_food_scanner
from muac_module import run_muac_estimator, classify_muac
from height_module import run_height_estimator

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

# Meta and favicon
components.html("""
    <link rel="apple-touch-icon" sizes="180x180" href="https://raw.githubusercontent.com/mannitha/food_scanner_app/main/favicon.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="apple-mobile-web-app-title" content="My App">
""", height=0)

user_data_file = os.path.join(os.getcwd(), "users.json")

def get_nutrition_file(): return f"nutrition_data_{st.session_state.username}.json"
def get_food_file(): return f"food_data_{st.session_state.username}.json"

def load_users():
    try:
        if os.path.exists(user_data_file):
            with open(user_data_file, "r") as f:
                return json.load(f)
    except json.JSONDecodeError:
        st.error("User data file is corrupted.")
        return {}
    return {}

def save_users(users):
    existing = load_users()
    existing.update(users)
    with open(user_data_file, "w") as f:
        json.dump(existing, f, indent=2)

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
            "view_data_table": "nutrition_choices",
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
    st.title("MalnoCare")
    st.write("Scan Track Grow")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👶 Physical Attributes"): st.session_state.page = "nutrition_choices"
    with col2:
        if st.button("🍽 Food Nutrients Scan"): st.session_state.page = "nutrimann_choices"

# --- [Repeat all other flow functions here as you already have them in your original script] ---
# Due to length limits, assume everything below here stays the same and is working:
# nutrition_choices_step(), child_info_step(), height_step(), arm_step(), done_step(),
# view_old_data_step(), view_data_table_step(), nutrimann_choices_step(),
# nutrimann_info_step(), food_only_step(), food_summary_step(), view_old_food_step(), edit_food_entry_step()

def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "page" not in st.session_state: st.session_state.page = "login"
    if st.session_state.logged_in:
        st.sidebar.title(f"👤 {st.session_state.username}")
        st.sidebar.button("Logout", on_click=logout)
        match st.session_state.page:
            case "select_flow": select_flow_step()
            case "nutrition_choices": nutrition_choices_step()
            case "child_info": child_info_step()
            case "height": height_step()
            case "arm": arm_step()
            case "done": done_step()
            case "view_old_data": view_old_data_step()
            case "view_data_table": view_data_table_step()
            case "nutrimann_choices": nutrimann_choices_step()
            case "nutrimann_info": nutrimann_info_step()
            case "food_only": food_only_step()
            case "food_summary": food_summary_step()
            case "view_old_food": view_old_food_step()
            case "edit_food_entry": edit_food_entry_step()
    else:
        option = st.radio("Login or Sign Up", ["Login", "Sign Up"])
        login() if option == "Login" else signup()

if __name__ == "__main__":
    main()
