import streamlit as st
from streamlit_lottie import st_lottie
import requests
import json, os
import pandas as pd
import streamlit.components.v1 as components
from food_module import run_food_scanner
from arm_module import run_muac
from height_module import run_height_estimator

# Safe Lottie Loader
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
        else:
            return None
    except:
        return None

# Setup
st.set_page_config(page_title="Malnutrition App", layout="wide")

# Mobile styling
st.markdown("""
    <style>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    .main .block-container {
        padding: 1rem;
        max-width: 100%;
    }
    #MainMenu, footer {visibility: hidden;}
    button[kind="primary"], .stButton > button {
        width: 100%;
        margin-top: 0.5rem;
    }
    .stTextInput > div > input, .stNumberInput input, .stSelectbox > div {
        font-size: 16px;
        padding: 0.75rem;
    }
    h1 {
        font-size: 1.8rem;
        margin-top: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

components.html("""
    <link rel="apple-touch-icon" sizes="180x180" href="https://raw.githubusercontent.com/mannitha/food_scanner_app/main/favicon.png">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="apple-mobile-web-app-title" content="Malnutrition App">
""", height=0)

# File management
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
    signup_lottie = load_lottieurl("https://lottie.host/46e8e6ec-08a5-42a0-a53f-e5f998369a61/tEENvAl3W4.json")
    if signup_lottie: st_lottie(signup_lottie, height=180)
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
    login_lottie = load_lottieurl("https://lottie.host/46e8e6ec-08a5-42a0-a53f-e5f998369a61/tEENvAl3W4.json")
    if login_lottie: st_lottie(login_lottie, height=180)
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

# Flow Pages
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
    with col2: 
        if st.button("🗑️ Delete Records"): st.session_state.page = "view_old_data"
    if st.button("📊 View Previous Data Summary"): st.session_state.page = "view_data_table"

def child_info_step():
    st.title("📋 Child Information")
    back_button()
    st.session_state.child_name = st.text_input("Child's Name")
    st.session_state.child_age = st.number_input("Age", min_value=0)
    st.session_state.child_weight = st.number_input("Weight (kg)", min_value=0.0)
    if st.button("Continue"): st.session_state.page = "height"

def height_step():
    st.title("📏 Height Estimator")
    back_button()
    height_result = run_height_estimator()
    if height_result:
        st.session_state.height_result = height_result
        if st.button("Next"): st.session_state.page = "arm"

def arm_step():
    st.title("📐 MUAC Estimator")
    back_button()
    arm_val, muac_status = run_muac()
    st.session_state.arm_value = arm_val
    st.session_state.muac_status = muac_status
    if st.button("Finish"): st.session_state.page = "done"

def done_step():
    st.title("✅ Summary")
    back_button()
    success_lottie = load_lottieurl("https://lottie.host/3d47d04e-e279-4237-b4b8-2d4b917f1aa7/xOWjZOfYXI.json")
    if success_lottie: st_lottie(success_lottie, height=150)
    entry = {
        "Name": st.session_state.child_name,
        "Age": st.session_state.child_age,
        "Weight (kg)": st.session_state.child_weight,
        "Height (cm)": st.session_state.height_result,
        "Arm Circumference (MUAC, cm)": st.session_state.arm_value,
    }
    entry["BMI"] = calculate_bmi(entry["Weight (kg)"], entry["Height (cm)"])
    entry["Malnutrition Status"] = calculate_malnutrition_status(entry["BMI"], entry["Arm Circumference (MUAC, cm)"])
    data = load_nutrition_data()
    if any(d["Name"] == entry["Name"] and d["Age"] == entry["Age"] for d in data): st.warning("Duplicate detected.")
    else:
        data.append(entry)
        save_nutrition_data(data)
        st.success("Saved!")
    st.table(pd.DataFrame([entry]))
    col1, col2 = st.columns(2)
    with col1: 
        if st.button("🔒 Logout"): logout()
    with col2: 
        if st.button("🏠 Back to Menu"): st.session_state.page = "nutrition_choices"

# Remaining functions (food scan and table views)
# [omitted here for brevity; same as your original code, no changes needed unless you want animations there too.]

# Main App
def main():
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "page" not in st.session_state: st.session_state.page = "login"
    if st.session_state.logged_in:
        st.sidebar.title(f"👤 {st.session_state.username}")
        st.sidebar.button("Logout", on_click=logout)
        match st.session_state.page:
            case "select_flow": select_flow_step()
            case "nutrition_choices": nutrition_choices_step()
            case "view_old_data": view_old_data_step()
            case "view_data_table": view_data_table_step()
            case "child_info": child_info_step()
            case "height": height_step()
            case "arm": arm_step()
            case "done": done_step()
            case "nutrimann_choices": nutrimann_choices_step()
            case "nutrimann_info": nutrimann_info_step()
            case "food_only": food_only_step()
            case "food_summary": food_summary_step()
            case "view_old_food": view_old_food_step()
            case "edit_food_entry": edit_food_entry_step()
    else:
        st.sidebar.title("🔐 Account")
        option = st.sidebar.selectbox("Login or Signup", ["Login", "Sign Up"])
        login() if option == "Login" else signup()

if __name__ == "__main__":
    main()
