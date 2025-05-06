# ✅ Full Streamlit App Code with Nutrition & Food Scanner Modules
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
            "modify_old_data": "nutrition_choices",
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
    col1, col2, col3 = st.columns(3)
    with col1: 
        if st.button("➕ New Entry"): st.session_state.page = "child_info"
    with col2: 
        if st.button("📄 View Previous Data"): st.session_state.page = "view_old_data"
    with col3: 
        if st.button("✏️ Modify Old Data"): st.session_state.page = "modify_old_data"

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
    st.session_state.height_result = run_height_estimator()
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

def view_old_data_step():
    st.title("📄 Previous Entries")
    back_button()
    df = pd.DataFrame(load_nutrition_data())
    if df.empty: st.info("No records.")
    else: st.dataframe(df)

def modify_old_data_step():
    st.title("✏️ Modify Old Data")

    if "child_data" not in st.session_state or not st.session_state["child_data"]:
        st.warning("No previous data found.")
        return

    df = pd.DataFrame(st.session_state["child_data"])
    
    if df.empty:
        st.warning("No records available to modify.")
        return

    selected_name = st.selectbox("Select a child to modify:", df["Name"])

    selected_idx = df[df["Name"] == selected_name].index

    if selected_idx.empty:
        st.error("Selected name not found.")
        return

    idx = selected_idx[0]  # Get the index of the selected row

    # Pre-fill values
    name = st.text_input("Name", value=df.at[idx, "Name"])
    age = st.number_input("Age (years)", min_value=0, max_value=18, value=int(df.at[idx, "Age"]))
    height = st.number_input("Height (cm)", min_value=0.0, max_value=200.0, value=float(df.at[idx, "Height"]))
    arm = st.number_input("Arm Circumference (cm)", min_value=0.0, max_value=50.0, value=float(df.at[idx, "Arm"]))
    food = st.text_input("Food Taken (Optional)", value=df.at[idx, "Food"])
    status = st.selectbox("Malnutrition Status", ["Normal", "Moderate", "Severe"], index=["Normal", "Moderate", "Severe"].index(df.at[idx, "Status"]))

    if st.button("Update Record"):
        updated_data = {
            "Name": name,
            "Age": age,
            "Height": height,
            "Arm": arm,
            "Food": food,
            "Status": status
        }

        # Safely update only if the index exists
        if idx in df.index:
            for key, value in updated_data.items():
                df.at[idx, key] = value

            # Save back to session state
            st.session_state["child_data"] = df.to_dict(orient="records")
            st.success("Record updated successfully.")
        else:
            st.error("Failed to update: index not found.")


def nutrimann_choices_step():
    st.title("🍴 NutriMann")
    back_button()
    col1, col2 = st.columns(2)
    with col1: 
        if st.button("➕ New Food Scan"): st.session_state.page = "nutrimann_info"
    with col2: 
        if st.button("📂 View Old Scans"): st.session_state.page = "view_old_food"

def nutrimann_info_step():
    st.title("🍛 Enter Meal Details")
    back_button()
    st.session_state.food_name = st.text_input("Name")
    st.session_state.food_time = st.selectbox("Meal Time", ["Breakfast", "Lunch", "Dinner", "Snack", "Other"])
    if st.button("Continue"): st.session_state.page = "food_only"

def food_only_step():
    st.title("📸 Scan Food")
    back_button()
    run_food_scanner()
    if st.button("Show Summary"):
        if "food_result" in st.session_state:
            st.session_state.page = "food_summary"
        else: st.error("Please scan the food first.")

def food_summary_step():
    st.title("🥗 Food Summary")
    back_button()
    name = st.session_state.food_name
    time = st.session_state.food_time
    result = st.session_state.get("food_result", pd.DataFrame())
    st.subheader(f"{name} — {time}")
    st.table(result)
    data = load_food_data()
    if any(d["Name"] == name and d["Meal Timing"] == time for d in data): st.warning("Duplicate scan exists!")
    else:
        data.append({"Name": name, "Meal Timing": time, "Nutrition Table": result.to_dict()})
        save_food_data(data)
        st.success("Saved!")
    if st.button("🏠 Back to Menu"): st.session_state.page = "nutrimann_choices"

def view_old_food_step():
    st.title("📂 Old Food Scans")
    back_button()
    data = load_food_data()
    if not data:
        st.info("No records")
        return
    idx = st.selectbox("Select", range(len(data)), format_func=lambda i: f"{data[i]['Name']} - {data[i]['Meal Timing']}")
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
    st.title("📝 Edit Food Entry")
    back_button()
    idx = st.session_state.edit_index
    data = load_food_data()
    entry = data[idx]
    name = st.text_input("Name", entry["Name"])
    time = st.selectbox("Meal Timing", ["Breakfast", "Lunch", "Dinner", "Snack", "Other"],
                        index=["Breakfast", "Lunch", "Dinner", "Snack", "Other"].index(entry["Meal Timing"]))
    df = pd.DataFrame(entry["Nutrition Table"])
    st.table(df)
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
            case "view_old_data": view_old_data_step()
            case "modify_old_data": modify_old_data_step()
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
