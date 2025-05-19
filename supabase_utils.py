from supabase_client import supabase
import pandas as pd
import streamlit as st

def load_users():
    response = supabase.table("users").select("*").execute()
    return {u["username"]: u for u in response.data}

def save_user(username, password, email):
    supabase.table("users").upsert({
        "username": username,
        "password": password,
        "email": email
    }).execute()

def load_nutrition_data():
    username = st.session_state.username
    response = supabase.table("nutrition_data").select("*").eq("username", username).execute()
    return response.data or []

def save_nutrition_data(entry):
    supabase.table("nutrition_data").insert(entry).execute()

def load_food_data():
    username = st.session_state.username
    response = supabase.table("food_data").select("*").eq("username", username).execute()
    return response.data or []

def save_food_data(entry):
    supabase.table("food_data").insert(entry).execute()
