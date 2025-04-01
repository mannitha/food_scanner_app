import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the latest Gemini model (gemini-1.5-flash')
model = genai.GenerativeModel('gemini-1.5-flash')

def get_nutrition_response(image, prompt):
    """Generates a nutrition analysis response using Gemini AI."""
    response = model.generate_content([image, prompt])
    return response.text

# Streamlit UI setup
st.set_page_config(page_title="NutriMann Scanner", layout="centered")  # Centered layout for mobile

# Custom CSS for mobile-friendly UI
st.markdown("""
    <style>
        .reportview-container {
            max-width: 800px;  /* Limit width for mobile */
            margin: 0 auto;
        }
        .sidebar .sidebar-content {
            padding: 0;
        }
        .css-1d391kg {
            width: 100%;
        }
    </style>
""", unsafe_allow_html=True)

st.header('🥗 NutriMann: Food Nutrition Scanner')

# File uploader
uploaded_file = st.file_uploader("Upload an image of food", type=["jpg", "jpeg", "png"])

# Display uploaded image
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

# Submit button
submit = st.button("🔍 Get Nutrition Levels")

# Nutrition extraction prompt
nutrition_prompt = """
Analyze the uploaded image and extract detailed nutritional information for each food item detected.
Provide a structured output with the following format:

Food Item | Calories (kcal) | Protein (g) | Carbs (g) | Fats (g) | Vitamins & Minerals
-----------|----------------|-------------|-----------|---------|---------------------
"""

# Process when the submit button is clicked
if submit:
    if uploaded_file is not None:
        try:
            response = get_nutrition_response(image, nutrition_prompt)
            
            # Convert response into table format
            lines = response.strip().split("\n")
            data = [line.split('|') for line in lines if '|' in line and not line.startswith(('Food Item', '-----------'))]
            
            # Ensure only required columns are selected
            expected_columns = ["Food Item", "Calories (kcal)", "Protein (g)", "Carbs (g)", "Fats (g)", "Vitamins & Minerals"]
            
            # Filter and clean data
            cleaned_data = []
            for row in data:
                if len(row) >= len(expected_columns):
                    cleaned_data.append(row[:len(expected_columns)])  # Trim extra columns if any
                elif len(row) == len(expected_columns) - 1:
                    cleaned_data.append(row + [""])  # Add empty string for missing values
            
            # Create DataFrame and reset index to start from 1
            df = pd.DataFrame(cleaned_data, columns=expected_columns)
            df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            df.index = df.index + 1  # Start index from 1
            
            # Split vitamins and minerals into separate lines for better readability
            df["Vitamins & Minerals"] = df["Vitamins & Minerals"].apply(lambda x: "\n".join(x.split(", ")) if isinstance(x, str) else x)
            
            # Display table in a non-editable format
            st.subheader("📊 Nutrition Analysis:")
            st.table(df)  # Use st.table to make it non-editable
            
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
    else:
        st.error("⚠️ Please upload an image before analyzing.")