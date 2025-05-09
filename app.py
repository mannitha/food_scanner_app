import streamlit as st
import gspread
import pandas as pd
from gspread_dataframe import set_with_dataframe, get_as_dataframe
from datetime import datetime
import streamlit.components.v1 as components
from food_module import run_food_scanner
from muac_module import run_muac_estimator, classify_muac
from height_module import run_height_estimator

# --- Google Sheets Setup ---
gc = gspread.service_account(filename="malnocare-459318-ac7c47067c82.json")
nutrition_sheet = gc.open("MalnutritionAppData").worksheet("Nutrition")
food_sheet = gc.open("MalnutritionAppData").worksheet("FoodScans")
users_sheet = gc.open("MalnutritionAppData").worksheet("malnocare_users")

# --- Page Setup ---
st.set_page_config(page_title="Malnutrition App", layout="wide")
st.markdown("""
    <style>
    .main .block-container { padding: 1rem; max-width: 100%; }
    #MainMenu, footer {visibility: hidden;}
    button[kind="primary"], .stButton > button { width: 100%; margin-top: 0.5rem; }
    .stTextInput > div > input, .stNumberInput input { font-size: 16px; padding: 0.75rem; }
    .stSelectbox > div { font-size: 16px; }
    .stDataFrame, .stTable { overflow-x: auto; }
    h1 { font-size: 1.8rem; margin-top: 0.5rem; }
    </style>
""", unsafe_allow_html=True)

# --- Data Functions ---
def load_users():
    df = get_as_dataframe(users_sheet).dropna()
    return {row["username"]: {"password": row["password"], "email": row["email"]} for _, row in df.iterrows()}

def save_users(users_dict):
    df = pd.DataFrame([
        {"username": u, "password": d["password"], "email": d["email"]}
        for u, d in users_dict.items()
    ])
    users_sheet.clear()
    set_with_dataframe(users_sheet, df)

def load_nutrition_data():
    df = get_as_dataframe(nutrition_sheet).dropna(how="all")
    return df.to_dict(orient="records")

def save_nutrition_data(data):
    df = pd.DataFrame(data)
    nutrition_sheet.clear()
    set_with_dataframe(nutrition_sheet, df)

def load_food_data():
    df = get_as_dataframe(food_sheet).dropna(how="all")
    for i in df.index:
        if isinstance(df.at[i, "Nutrition Table"], str):
            df.at[i, "Nutrition Table"] = eval(df.at[i, "Nutrition Table"])
    return df.to_dict(orient="records")

def save_food_data(data):
    df = pd.DataFrame(data)
    food_sheet.clear()
    set_with_dataframe(food_sheet, df)

# --- Auth ---
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
            "nutrition_choices": "select_flow", "nutrimann_choices": "select_flow",
            "child_info": "nutrition_choices", "height": "child_info", "arm": "height",
            "done": "arm", "nutrimann_info": "nutrimann_choices", "food_only": "nutrimann_info",
            "food_summary": "food_only", "view_old_data": "nutrition_choices",
            "view_data_table": "nutrition_choices", "view_old_food": "nutrimann_choices",
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

# --- Flow Functions ---
# [All the step functions and main() go here, identical to your structure]
# Replace only the Google Sheet worksheet names above, which we did.

# --- Main App ---
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
