import streamlit as st 
import json
import os
import pandas as pd
import numpy as np
from food_module import run_food_scanner
from arm_module import run_muac
from height_module import run_height_estimator

USER_DATA_FILE = "users.json"
NUTRITION_DATA_FILE = "nutrition_data.json"
FOOD_DATA_FILE = "food_data.json"

# -------- Helper Functions --------
def load_users():
    return json.load(open(USER_DATA_FILE)) if os.path.exists(USER_DATA_FILE) else {}

def save_users(users):
    json.dump(users, open(USER_DATA_FILE, "w"))

def load_nutrition_data():
    if os.path.exists(NUTRITION_DATA_FILE):
        try:
            data = json.load(open(NUTRITION_DATA_FILE))
            return data if isinstance(data, list) else []
        except:
            return []
    return []

def save_nutrition_data(data):
    json.dump(data, open(NUTRITION_DATA_FILE, "w"), indent=2)

def load_food_data():
    return json.load(open(FOOD_DATA_FILE)) if os.path.exists(FOOD_DATA_FILE) else []

def save_food_data(data):
    json.dump(data, open(FOOD_DATA_FILE, "w"), indent=2)

# -------- Auth --------
def signup():
    st.title("Sign Up")
    u, p, e = st.text_input("Username"), st.text_input("Password", type="password"), st.text_input("Email")
    if st.button("Create Account"):
        users = load_users()
        if u in users: st.error("Username already exists.")
        else:
            users[u] = {"password": p, "email": e}
            save_users(users)
            st.success("Account created!")

def login():
    st.title("Login")
    u, p = st.text_input("Username"), st.text_input("Password", type="password")
    if st.button("Login"):
        users = load_users()
        if u not in users: st.error("Username doesn't exist.")
        elif users[u]["password"] != p: st.error("Incorrect password.")
        else:
            st.session_state.logged_in = True
            st.session_state.username = u
            st.session_state.page = "select_flow"

def logout():
    st.session_state.clear()

# -------- Navigation --------
def back_button():
    if st.button("\u2b05 Back"):
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
            "modify_old_data": "nutrition_choices",
            "view_old_food": "nutrimann_choices",
            "edit_food_entry": "view_old_food"
        }
        st.session_state.page = nav.get(st.session_state.page, "select_flow")
        st.rerun()

# -------- BMI & Status --------
def calculate_bmi(w, h):
    if not w or not h: return None
    return round(w / ((h / 100) ** 2), 2)

def calculate_malnutrition_status(bmi, arm):
    if bmi is None or arm is None: return "Unknown"
    if bmi < 13 or arm < 11.5: return "Severe Acute Malnutrition"
    elif bmi < 14 or arm < 12.5: return "Moderate Acute Malnutrition"
    return "Normal"

# -------- Nutrition Flow --------
def select_flow_step():
    st.title("Choose Flow")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("👶 Nutrition Detection"):
            st.session_state.page = "nutrition_choices"
    with col2:
        if st.button("🍽 NutriMann (Food Scanner Only)"):
            st.session_state.page = "nutrimann_choices"

def nutrition_choices_step():
    st.title("Nutrition Detection")
    back_button()
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ New Entry"): st.session_state.page = "child_info"
    with col2:
        if st.button("📄 View Previous Data"): st.session_state.page = "view_old_data"
    with col3:
        if st.button("✏️ Modify Old Data"): st.session_state.page = "modify_old_data"

def child_info_step():
    st.title("Child Info")
    back_button()
    st.session_state.child_name = st.text_input("Child's Name")
    st.session_state.child_age = st.number_input("Age", min_value=0)
    st.session_state.child_weight = st.number_input("Weight (kg)", min_value=0.0)
    if st.button("Continue"): st.session_state.page = "height"

def height_step():
    st.title("Height Estimator")
    back_button()
    st.session_state.height_result = run_height_estimator()
    if st.button("Next"): st.session_state.page = "arm"

def arm_step():
    st.title("MUAC Estimator")
    back_button()
    arm_val, muac_status = run_muac()
    st.session_state.arm_value, st.session_state.muac_status = arm_val, muac_status
    if st.button("Finish"): st.session_state.page = "done"

def done_step():
    st.title("Summary ✅")
    back_button()
    name = st.session_state.child_name
    age = st.session_state.child_age
    weight = st.session_state.child_weight
    height = st.session_state.height_result
    arm = st.session_state.arm_value
    bmi = calculate_bmi(weight, height)
    status = calculate_malnutrition_status(bmi, arm)
    data = load_nutrition_data()
    if any(d["Name"] == name and d["Age"] == age for d in data):
        st.warning("Duplicate detected.")
    else:
        entry = {
            "Name": name, "Age": age, "Weight (kg)": weight,
            "Height (cm)": height, "Arm Circumference (MUAC, cm)": arm,
            "BMI": bmi, "Malnutrition Status": status
        }
        data.append(entry)
        save_nutrition_data(data)
        st.success("Saved!")

    st.table(pd.DataFrame([entry]))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔒 Logout"): logout()
    with col2:
        if st.button("🏠 Back to Menu"): st.session_state.page = "nutrition_choices"

def view_old_data_step():
    st.title("Previous Entries")
    back_button()
    df = pd.DataFrame(load_nutrition_data())
    st.dataframe(df if not df.empty else "No records.")

def modify_old_data_step():
    st.title("Modify Entry")
    back_button()
    data = load_nutrition_data()
    if not data: st.info("No data"); return
    df = pd.DataFrame(data)
    idx = st.selectbox("Select", range(len(df)), format_func=lambda i: f"{df.iloc[i]['Name']} (Age {df.iloc[i]['Age']})")
    r = df.iloc[idx]
    n = st.text_input("Name", r["Name"])
    a = st.number_input("Age", value=int(r["Age"]))
    w = st.number_input("Weight", value=float(r["Weight (kg)"]))
    h = st.number_input("Height", value=float(r["Height (cm)"]))
    arm = st.number_input("MUAC", value=float(r["Arm Circumference (MUAC, cm)"]))

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Update"):
            bmi = calculate_bmi(w, h)
            s = calculate_malnutrition_status(bmi, arm)
            df.at[idx, "Name"] = n
            df.at[idx, "Age"] = a
            df.at[idx, "Weight (kg)"] = w
            df.at[idx, "Height (cm)"] = h
            df.at[idx, "Arm Circumference (MUAC, cm)"] = arm
            df.at[idx, "BMI"] = bmi
            df.at[idx, "Malnutrition Status"] = s
            save_nutrition_data(df.to_dict("records"))
            st.success("Updated!")
    with col2:
        if st.button("Delete"):
            data.pop(idx)
            save_nutrition_data(data)
            st.success("Entry deleted!")
            st.rerun()

# -------- NutriMann Flow --------
def nutrimann_choices_step():
    st.title("NutriMann")
    back_button()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ New Food Scan"): st.session_state.page = "nutrimann_info"
    with col2:
        if st.button("📄 View Old Food Scans"): st.session_state.page = "view_old_food"

def nutrimann_info_step():
    st.title("Enter Details")
    back_button()
    st.session_state.food_name = st.text_input("Name")
    st.session_state.food_time = st.selectbox("Meal Time", ["Breakfast", "Lunch", "Dinner", "Snack", "Other"])
    if st.button("Continue"): st.session_state.page = "food_only"

def food_only_step():
    st.title("Scan Food")
    back_button()
    run_food_scanner()
    if st.button("Show Summary"):
        if "food_result" in st.session_state:
            st.session_state.page = "food_summary"
        else:
            st.error("Please scan first.")

def food_summary_step():
    st.title("Food Summary")
    back_button()
    name = st.session_state.food_name
    time = st.session_state.food_time
    result = st.session_state.get("food_result", pd.DataFrame())
    st.subheader(f"{name} — {time}")
    st.table(result)

    data = load_food_data()
    if any(d["Name"] == name and d["Meal Timing"] == time for d in data):
        st.warning("Duplicate scan exists!")
    else:
        data.append({"Name": name, "Meal Timing": time, "Nutrition Table": result.to_dict()})
        save_food_data(data)
        st.success("Saved!")

    if st.button("🏠 Back to Menu"): st.session_state.page = "nutrimann_choices"

def view_old_food_step():
    st.title("Old Food Scans")
    back_button()
    data = load_food_data()
    if not data:
        st.info("No records"); return
    idx = st.selectbox("Select Entry", range(len(data)), format_func=lambda i: f"{data[i]['Name']} - {data[i]['Meal Timing']}")
    entry = data[idx]
    st.table(pd.DataFrame(entry["Nutrition Table"]))
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✏️ Edit"):
            st.session_state.edit_index = idx
            st.session_state.page = "edit_food_entry"
    with col2:
        if st.button("🗑 Delete"):
            del data[idx]
            save_food_data(data)
            st.success("Deleted!")
            st.rerun()

def edit_food_entry_step():
    st.title("Edit Food Entry")
    back_button()
    idx = st.session_state.edit_index
    data = load_food_data()
    entry = data[idx]
    name = st.text_input("Name", entry["Name"])
    time = st.selectbox("Meal Timing", ["Breakfast", "Lunch", "Dinner", "Snack", "Other"], index=["Breakfast", "Lunch", "Dinner", "Snack", "Other"].index(entry["Meal Timing"]))
    df = pd.DataFrame(entry["Nutrition Table"])
    st.table(df)
    if st.button("Save Changes"):
        data[idx]["Name"] = name
        data[idx]["Meal Timing"] = time
        save_food_data(data)
        st.success("Updated!")
        st.session_state.page = "view_old_food"

# -------- Main --------
def main():
    st.set_page_config("Malnutrition App", layout="wide")
    if "logged_in" not in st.session_state: st.session_state.logged_in = False
    if "page" not in st.session_state: st.session_state.page = "login"

    if st.session_state.logged_in:
        st.sidebar.title(f"👋 {st.session_state.username}")
        st.sidebar.button("Logout", on_click=logout)

        page = st.session_state.page
        if page == "select_flow": select_flow_step()
        elif page == "nutrition_choices": nutrition_choices_step()
        elif page == "view_old_data": view_old_data_step()
        elif page == "modify_old_data": modify_old_data_step()
        elif page == "child_info": child_info_step()
        elif page == "height": height_step()
        elif page == "arm": arm_step()
        elif page == "done": done_step()
        elif page == "nutrimann_choices": nutrimann_choices_step()
        elif page == "nutrimann_info": nutrimann_info_step()
        elif page == "food_only": food_only_step()
        elif page == "food_summary": food_summary_step()
        elif page == "view_old_food": view_old_food_step()
        elif page == "edit_food_entry": edit_food_entry_step()
    else:
        st.sidebar.title("Account")
        option = st.sidebar.selectbox("Login / Signup", ["Login", "Sign Up"])
        if option == "Login": login()
        else: signup()

if __name__ == "__main__":
    main()
