# food_module.py

import streamlit as st
from PIL import Image
import google.generativeai as genai
import pandas as pd
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

def run_food_scanner():
    """Food scanner functionality wrapped in a function."""
    def get_nutrition_response(image, prompt):
        try:
            response = model.generate_content([image, prompt])
            return response.text
        except Exception as e:
            st.error(f"⚠ Error: {e}")
            return None

    st.header('🥗 NutriMann: Food Nutrition Scanner')

    # Upload file
    uploaded_file = st.file_uploader("📸 Upload or take a photo of your food", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="📷 Uploaded Image", use_column_width=True)
        st.success("✅ Image uploaded successfully!")

        # Save uploaded image in session state
        st.session_state.food_uploaded_image = image

    # Button to analyze
    submit = st.button("🔍 Get Nutrition Levels")

    nutrition_prompt = """
    Analyze the uploaded image and extract detailed nutritional information for each food item detected, including the quantity of each item.
    Provide a structured output with the following format:

    Food Item | Quantity | Calories (kcal) | Protein (g) | Carbs (g) | Fats (g) | Vitamins & Minerals
    -----------|----------|----------------|-------------|-----------|---------|---------------------
    """

    if submit:
        if "food_uploaded_image" in st.session_state:
            try:
                response = get_nutrition_response(st.session_state.food_uploaded_image, nutrition_prompt)

                if response:
                    # Process the response into table
                    lines = response.strip().split("\n")
                    data = [line.split('|') for line in lines if '|' in line and not line.startswith(('Food Item', '-----------'))]

                    expected_columns = ["Food Item", "Quantity", "Calories (kcal)", "Protein (g)", "Carbs (g)", "Fats (g)", "Vitamins & Minerals"]

                    cleaned_data = []
                    for row in data:
                        if len(row) >= len(expected_columns):
                            cleaned_data.append(row[:len(expected_columns)])
                        elif len(row) == len(expected_columns) - 1:
                            cleaned_data.append(row + [""])

                    df = pd.DataFrame(cleaned_data, columns=expected_columns)
                    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
                    df.index = df.index + 1

                    # Better format vitamins & minerals
                    df["Vitamins & Minerals"] = df["Vitamins & Minerals"].apply(lambda x: "\n".join(x.split(", ")) if isinstance(x, str) else x)

                    st.subheader("📊 Nutrition Analysis:")
                    st.table(df)

                    # Save the DataFrame in session state!
                    st.session_state.food_result = df

                else:
                    st.error("⚠ Could not retrieve nutritional data. Try again or check the image quality.")
            except Exception as e:
                st.error(f"⚠ Error: {e}")
        else:
            st.error("⚠ Please upload an image before analyzing.")
