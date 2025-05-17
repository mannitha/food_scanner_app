import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import streamlit.components.v1 as components
from food_module import run_food_scanner
from muac_module import run_muac_estimator, classify_muac
from height_module import run_height_estimator

st.set_page_config(page_title="Malnutrition App", layout="wide")

# --- Google Sheets setup ---
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

@st.cache_resource
def get_gs_client():
    creds_dict = st.secrets["google"]
    creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
    client = gspread.authorize(creds)
    return client

@st.cache_resource
def get_sheets():
    client = get_gs_client()
    spreadsheet = client.open("MalnoCareData")  # <--- Change this!
    return {
        "users": spreadsheet.worksheet("Users"),
        "nutrition": spreadsheet.worksheet("Nutrition"),
        "foodscans": spreadsheet.worksheet("FoodScans"),
    }

sheets = get_sheets()

# --- Helper functions for Google Sheets ---

def load_users():
    try:
        records = sheets["users"].get_all_records()
        users = {r["username"]: r for r in records}
        return users
    except Exception as e:
        st.error(f"Error loading users: {e}")
        return {}

def save_user(username, password, email):
    # Append new user row [username, password, email, created_at]
    sheets["users"].append_row([username, password, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

def user_exists(username):
    return username in load_users()

def check_login(username, password):
    users = load_users()
    return username in users and users[username]["password"] == password

def log_nutrition(username, height, weight, muac):
    sheets["nutrition"].append_row([
        username, height, weight, muac,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

def log_foodscan(username, food_name, calories):
    sheets["foodscans"].append_row([
        username, food_name, calories,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ])

# --- UI & Flow code ---

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

# --- Auth functions ---

def signup():
    st.title("🔐 Sign Up")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    email = st.text_input("Email")
    if st.button("Create Account"):
        if user_exists(username):
            st.error("Username already exists.")
        else:
            save_user(username, password, email)
            st.success("Account created! Please login.")

def login():
    st.title("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if not user_exists(username):
            st.error("Username doesn't exist.")
        elif not check_login(username, password):
            st.error("Incorrect password.")
        else:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.page = "select_flow"

def logout():
    st.session_state.clear()

def back_button():
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
    if st.button("⬅️ Back"):
        st.session_state.page = nav.get(st.session_state.page, "select_flow")
        st.experimental_rerun()

def calculate_bmi(w, h): 
    return round(w / ((h / 100) ** 2), 2) if w and h else None

def calculate_malnutrition_status(bmi, arm):
    if bmi is None or arm is None: return "Unknown"
    if bmi < 13 or arm < 11.5: return "Severe Acute Malnutrition"
    elif bmi < 14 or arm < 12.5: return "Moderate Acute Malnutrition"
    return "Normal"

# --- Your flow step functions ---
# (You already have these implemented, keep them unchanged)
# e.g. select_flow_step(), nutrition_choices_step(), child_info_step(), height_step(), arm_step(), done_step(), etc.

# Just placeholders for now so code runs
def select_flow_step():
    st.title("MalnoCare")
    st.write("Scan Track Grow")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👶 Physical Attributes"):
            st.session_state.page = "nutrition_choices"
            st.experimental_rerun()
    with col2:
        if st.button("🍽 Food Nutrients Scan"):
            st.session_state.page = "nutrimann_choices"
            st.experimental_rerun()

# --- Main app ---

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "page" not in st.session_state:
        st.session_state.page = "login"

    if st.session_state.logged_in:
        st.sidebar.title(f"👤 {st.session_state.username}")
        if st.sidebar.button("Logout"):
            logout()
            st.experimental_rerun()

        # Route pages according to your session state page variable
        page = st.session_state.page
        if page == "select_flow":
            select_flow_step()
        # Add your other flow page calls here (nutrition_choices_step, child_info_step, etc.)
        else:
            st.write(f"Page `{page}` not implemented in this snippet.")
    else:
        option = st.radio("Login or Sign Up", ["Login", "Sign Up"])
        if option == "Login":
            login()
        else:
            signup()

if __name__ == "__main__":
    main()
