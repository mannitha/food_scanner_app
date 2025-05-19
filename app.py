import streamlit as st
import pandas as pd
from supabase import create_client
import uuid

# --- Supabase Config ---
SUPABASE_URL = "https://qtpjctlrxoeeqchifyiz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF0cGpjdGxyeG9lZXFjaGlmeWl6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc2MzU1MDYsImV4cCI6MjA2MzIxMTUwNn0.jaVyzrfo88VQZoSdHj0yGWtMxJdhRuUX5I_RqO5Y8CU"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Malnutrition Detection App", layout="centered")

# --- User Session ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""

# --- Supabase Functions ---
def save_nutrition_data(entry):
    entry["id"] = str(uuid.uuid4())
    entry["username"] = st.session_state.username
    supabase.table("nutrition_data").insert(entry).execute()

def load_nutrition_data():
    result = supabase.table("nutrition_data").select("*").eq("username", st.session_state.username).execute()
    return result.data or []

def delete_nutrition_entry(entry_id):
    supabase.table("nutrition_data").delete().eq("id", entry_id).execute()

def save_food_data_entry(entry):
    entry["id"] = str(uuid.uuid4())
    entry["username"] = st.session_state.username
    entry["nutrition_table"] = entry["nutrition_table"] if isinstance(entry["nutrition_table"], dict) else entry["nutrition_table"].to_dict()
    supabase.table("food_data").insert(entry).execute()

def load_food_data():
    result = supabase.table("food_data").select("*").eq("username", st.session_state.username).execute()
    return result.data or []

def update_food_data_entry(entry_id, new_data):
    supabase.table("food_data").update(new_data).eq("id", entry_id).execute()

def delete_food_entry(entry_id):
    supabase.table("food_data").delete().eq("id", entry_id).execute()

# --- Login ---
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username and password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Logged in successfully!")
        else:
            st.error("Please enter both username and password.")

# --- Nutrition Entry ---
def done_step():
    st.title("Child Nutrition Entry")
    name = st.text_input("Child's Name")
    age = st.number_input("Age", min_value=0)
    weight = st.number_input("Weight (kg)", min_value=0.0)
    height = st.number_input("Height (cm)", min_value=0.0)
    muac = st.number_input("Arm Circumference (MUAC, cm)", min_value=0.0)

    if st.button("Calculate and Save"):
        if height > 0:
            bmi = weight / ((height / 100) ** 2)
        else:
            bmi = 0

        status = "Normal"
        if muac < 11.5:
            status = "Severe Acute Malnutrition"
        elif muac < 12.5:
            status = "Moderate Acute Malnutrition"

        entry = {
            "name": name,
            "age": age,
            "weight_kg": weight,
            "height_cm": height,
            "muac_cm": muac,
            "bmi": round(bmi, 2),
            "status": status
        }

        data = load_nutrition_data()
        if any(d["name"] == entry["name"] and d["age"] == entry["age"] for d in data):
            st.warning("Duplicate detected. Entry was not saved.")
        else:
            save_nutrition_data(entry)
            st.success("Saved!")

# --- Food Scan Summary ---
def food_summary_step():
    st.title("Food Scan Entry")
    name = st.text_input("Child's Name")
    time = st.selectbox("Meal Time", ["Breakfast", "Lunch", "Dinner", "Snack"])

    # Dummy food scan result
    result = pd.DataFrame({
        "Food Item": ["Rice", "Dal"],
        "Calories": [200, 150],
        "Protein (g)": [4, 8],
        "Fat (g)": [0.5, 1]
    })
    st.dataframe(result)

    if st.button("Save Scan"):
        data = load_food_data()
        if any(d["name"] == name and d["meal_timing"] == time for d in data):
            st.warning("Duplicate scan exists!")
        else:
            save_food_data_entry({
                "name": name,
                "meal_timing": time,
                "nutrition_table": result.to_dict()
            })
            st.success("Saved!")

# --- Navigation ---
def main():
    if not st.session_state.logged_in:
        login()
        return

    st.sidebar.title("Navigation")
    choice = st.sidebar.radio("Go to", ["Child Nutrition", "Food Scan", "Logout"])

    if choice == "Child Nutrition":
        done_step()
    elif choice == "Food Scan":
        food_summary_step()
    elif choice == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()

if __name__ == "__main__":
    main()
