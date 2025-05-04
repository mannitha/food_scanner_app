import streamlit as st
import json
import os
import pandas as pd
import streamlit.components.v1 as components
from food_module import run_food_scanner
from arm_module import run_muac
from height_module import run_height_estimator

# Meta and icon for mobile
components.html("""
    <link rel="apple-touch-icon" sizes="180x180" href="https://raw.githubusercontent.com/mannitha/food_scanner_app/main/favicon.png">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black">
    <meta name="apple-mobile-web-app-title" content="Malnutrition App">
""", height=0)

# Inject CSS for mobile layout
st.markdown("""
    <style>
    body {
        margin: 0 auto;
        padding: 0;
        font-family: 'Arial', sans-serif;
        background-color: #fafafa;
    }
    .main {
        max-width: 100%;
        padding: 0 1rem;
    }
    .stButton > button {
        width: 100%;
        height: 3rem;
        font-size: 1.1rem;
        margin-top: 10px;
    }
    .stTextInput > div > input, .stNumberInput > div input {
        font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

# File functions
USER_DATA_FILE = "users.json"
def get_nutrition_file(): return f"nutrition_data_{st.session_state.username}.json"
def get_food_file(): return f"food_data_{st.session_state.username}.json"
def load_users(): return json.load(open(USER_DATA_FILE)) if os.path.exists(USER_DATA_FILE) else {}
def save_users(users): json.dump(users, open(USER_DATA_FILE, "w"))
def load_nutrition_data(): return json.load(open(get_nutrition_file())) if os.path.exists(get_nutrition_file()) else []
def save_nutrition_data(data): json.dump(data, open(get_nutrition_file(), "w"), indent=2)
def load_food_data(): return json.load(open(get_food_file())) if os.path.exists(get_food_file()) else []
def save_food_data(data): json.dump(data, open(get_food_file(), "w"), indent=2)

# Utility functions
def logout(): st.session_state.clear()
def calculate_bmi(w, h): return round(w / ((h / 100) ** 2), 2) if w and h else None
def calculate_malnutrition_status(bmi, arm):
    if bmi is None or arm is None:
        return "Unknown"
    if bmi < 13 or arm < 11.5:
        return "Severe Acute Malnutrition"
    elif bmi < 14 or arm < 12.5:
        return "Moderate Acute Malnutrition"
    return "Normal"

# Navigation
def back_button():
    if st.button("⬅️ Back"):
        nav = {
            "nutrition_choices": "select_flow", "nutrimann_choices": "select_flow",
            "child_info": "nutrition_choices", "height": "child_info",
            "arm": "height", "done": "arm", "nutrimann_info": "nutrimann_choices",
            "food_only": "nutrimann_info", "food_summary": "food_only",
            "view_old_data": "nutrition_choices", "modify_old_data": "nutrition_choices",
            "view_old_food": "nutrimann_choices", "edit_food_entry": "view_old_food"
        }
        st.session_state.page = nav.get(st.session_state.page, "select_flow")
        st.rerun()

# Pages
def login():
    st.title("🔐 Login")
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

def signup():
    st.title("📝 Sign Up")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    e = st.text_input("Email")
    if st.button("Create Account"):
        users = load_users()
        if u in users:
            st.error("Username already exists.")
        else:
            users[u] = {"password": p, "email": e}
            save_users(users)
            st.success("Account created!")

def select_flow_step():
    st.title("📋 Choose Flow")
    if st.button("👶 Nutrition Detection"):
        st.session_state.page = "nutrition_choices"
    if st.button("🍽 NutriMann (Food Scanner Only)"):
        st.session_state.page = "nutrimann_choices"

def nutrition_choices_step():
    st.title("🧒 Nutrition Menu")
    back_button()
    if st.button("➕ New Entry"):
        st.session_state.page = "child_info"
    if st.button("📄 View Previous Data"):
        st.session_state.page = "view_old_data"
    if st.button("✏️ Modify Old Data"):
        st.session_state.page = "modify_old_data"

def child_info_step():
    st.title("📋 Child Information")
    back_button()
    st.session_state.child_name = st.text_input("Child's Name")
    st.session_state.child_age = st.number_input("Age", min_value=0)
    st.session_state.child_weight = st.number_input("Weight (kg)", min_value=0.0)
    if st.button("Continue"):
        st.session_state.page = "height"

def height_step():
    st.title("📏 Height Estimator")
    back_button()
    st.session_state.height_result = run_height_estimator()
    if st.button("Next"):
        st.session_state.page = "arm"

def arm_step():
    st.title("📐 MUAC Estimator")
    back_button()
    arm_val, muac_status = run_muac()
    st.session_state.arm_value = arm_val
    st.session_state.muac_status = muac_status
    if st.button("Finish"):
        st.session_state.page = "done"

def done_step():
    st.title("✅ Summary")
    back_button()
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
    if any(d["Name"] == entry["Name"] and d["Age"] == entry["Age"] for d in data):
        st.warning("Duplicate detected.")
    else:
        data.append(entry)
        save_nutrition_data(data)
        st.success("Saved!")
    st.table(pd.DataFrame([entry]))
    if st.button("🏠 Back to Menu"):
        st.session_state.page = "nutrition_choices"
    if st.button("🔒 Logout"):
        logout()

def view_old_data_step():
    st.title("📄 Previous Entries")
    back_button()
    df = pd.DataFrame(load_nutrition_data())
    st.dataframe(df) if not df.empty else st.info("No records.")

def modify_old_data_step():
    st.title("✏️ Modify Entry")
    back_button()
    data = load_nutrition_data()
    if not data: return st.info("No data available")
    df = pd.DataFrame(data)
    idx = st.selectbox("Select Entry", range(len(df)), format_func=lambda i: f"{df.iloc[i]['Name']} (Age {df.iloc[i]['Age']})")
    r = df.iloc[idx]
    n = st.text_input("Name", r["Name"])
    a = st.number_input("Age", value=int(r["Age"]))
    w = st.number_input("Weight", value=float(r["Weight (kg)"]))
    h = st.number_input("Height", value=float(r["Height (cm)"]))
    arm = st.number_input("MUAC", value=float(r["Arm Circumference (MUAC, cm)"]))
    if st.button("Update"):
        bmi = calculate_bmi(w, h)
        s = calculate_malnutrition_status(bmi, arm)
        df.at[idx] = {
            "Name": n, "Age": a, "Weight (kg)": w, "Height (cm)": h,
            "Arm Circumference (MUAC, cm)": arm, "BMI": bmi, "Malnutrition Status": s
        }
        save_nutrition_data(df.to_dict("records"))
        st.success("Updated!")
    if st.button("Delete"):
        data.pop(idx)
        save_nutrition_data(data)
        st.success("Deleted!")
        st.rerun()

def nutrimann_choices_step():
    st.title("🍴 NutriMann")
    back_button()
    if st.button("➕ New Food Scan"):
        st.session_state.page = "nutrimann_info"
    if st.button("📂 View Old Scans"):
        st.session_state.page = "view_old_food"

def nutrimann_info_step():
    st.title("🍛 Enter Meal Details")
    back_button()
    st.session_state.food_name = st.text_input("Name")
    st.session_state.food_time = st.selectbox("Meal Time", ["Breakfast", "Lunch", "Dinner", "Snack", "Other"])
    if st.button("Continue"):
        st.session_state.page = "food_only"

def food_only_step():
    st.title("📸 Scan Food")
    back_button()
    run_food_scanner()
    if st.button("Show Summary"):
        if "food_result" in st.session_state:
            st.session_state.page = "food_summary"
        else:
            st.error("Please scan the food first.")

def food_summary_step():
    st.title("🥗 Food Summary")
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
    if st.button("🏠 Back to Menu"):
        st.session_state.page = "nutrimann_choices"

def view_old_food_step():
    st.title("📂 Old Food Scans")
    back_button()
    data = load_food_data()
    if not data: return st.info("No records")
    idx = st.selectbox("Select", range(len(data)), format_func=lambda i: f"{data[i]['Name']} - {data[i]['Meal Timing']}")
    entry = data[idx]
    st.table(pd.DataFrame(entry["Nutrition Table"]))
    if st.button("✏️ Edit"):
        st.session_state.edit_index = idx
        st.session_state.page = "edit_food_entry"
    if st.button("🗑 Delete"):
        del data[idx]
        save_food_data(data)
        st.success("Deleted!")
        st.rerun()

def edit_food_entry_step():
    st.title("📝 Edit Food Entry")
    back_button()
    idx = st.session_state.edit_index
    data = load_food_data()
    entry = data[idx]
    name = st.text_input("Name", entry["Name"])
    time = st.selectbox("Meal Timing", ["Breakfast", "Lunch", "Dinner", "Snack", "Other"],
                        index=["Breakfast", "Lunch", "Dinner", "Snack", "Other"].index(entry["Meal Timing"]))
    st.table(pd.DataFrame(entry["Nutrition Table"]))
    if st.button("Save Changes"):
        data[idx]["Name"] = name
        data[idx]["Meal Timing"] = time
        save_food_data(data)
        st.success("Updated!")
        st.session_state.page = "view_old_food"

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
            case "modify_old_data": modify_old_data_step()
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
