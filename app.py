# main.py (updated with Supabase)

import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Supabase config
SUPABASE_URL = "https://qtpjctlrxoeeqchifyiz.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF0cGpjdGxyeG9lZXFjaGlmeWl6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDc2MzU1MDYsImV4cCI6MjA2MzIxMTUwNn0.jaVyzrfo88VQZoSdHj0yGWtMxJdhRuUX5I_RqO5Y8CU"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def load_users():
    res = supabase.table("users").select("*").execute()
    users = {r["username"]: {"password": r["password"], "email": r["email"]} for r in res.data}
    return users

def save_users(users):
    for username, info in users.items():
        supabase.table("users").insert({
            "username": username,
            "password": info["password"],
            "email": info["email"]
        }).execute()

def load_nutrition_data():
    res = supabase.table("nutrition_data").select("*").eq("username", st.session_state.username).execute()
    return res.data

def save_nutrition_data(entry):
    supabase.table("nutrition_data").insert(entry).execute()

def load_food_data():
    res = supabase.table("food_data").select("*").eq("username", st.session_state.username).execute()
    return res.data

def save_food_data(entry):
    supabase.table("food_data").insert(entry).execute()

def delete_nutrition_entry(username, name, age):
    supabase.table("nutrition_data").delete().eq("username", username).eq("name", name).eq("age", age).execute()

def update_food_entry(username, old_name, old_time, new_name, new_time):
    supabase.table("food_data").update({
        "name": new_name,
        "meal_timing": new_time
    }).eq("username", username).eq("name", old_name).eq("meal_timing", old_time).execute()

# The rest of your existing Streamlit UI code remains unchanged
# Replace each call to the old JSON file functions with the above

# In done_step()
entry = {
    "Name": name,
    "Age": age,
    "Weight (kg)": weight,
    "Height (cm)": height,
    "Arm Circumference (MUAC, cm)": muac,
    "BMI": bmi,
    "Malnutrition Status": status
}
data = load_nutrition_data()
if any(d["name"] == entry["Name"] and d["age"] == entry["Age"] for d in data):
    st.warning("Duplicate detected. Entry was not saved.")
else:
    entry["username"] = st.session_state.username
    entry["name"] = entry.pop("Name")
    entry["age"] = entry.pop("Age")
    entry["weight"] = entry.pop("Weight (kg)")
    entry["height"] = entry.pop("Height (cm)")
    entry["muac"] = entry.pop("Arm Circumference (MUAC, cm)")
    entry["bmi"] = entry.pop("BMI")
    entry["status"] = entry.pop("Malnutrition Status")
    save_nutrition_data(entry)
    st.success("Saved!")

# In food_summary_step()
if any(d["name"] == name and d["meal_timing"] == time for d in data):
    st.warning("Duplicate scan exists!")
else:
    new_entry = {
        "username": st.session_state.username,
        "name": name,
        "meal_timing": time,
        "nutrition_table": result.to_dict()
    }
    save_food_data(new_entry)
    st.success("Saved!")

# Make sure to use the new delete_nutrition_entry and update_food_entry where needed

# Replace `<your-supabase-url>` and `<your-anon-key>` with actual values from your Supabase project.
