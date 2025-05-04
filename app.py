import streamlit as st

# Simulated session state for step tracking (ensure you use your own logic)
if "step" not in st.session_state:
    st.session_state.step = "nutrition_menu"

# === STYLING FOR MOBILE UI ===
st.markdown("""
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .stButton>button {
            width: 100%;
            border-radius: 12px;
            margin-bottom: 12px;
            font-size: 1.05rem;
            padding: 0.75rem 1rem;
            background-color: #2e8b57;
            color: white;
            border: none;
        }
        .stButton>button:hover {
            background-color: #246b45;
        }
        h1 {
            text-align: center;
            font-size: 2.2rem;
            margin-bottom: 2rem;
        }
        .back-btn>button {
            background-color: #444;
            width: auto;
            margin-bottom: 2rem;
            border-radius: 10px;
        }
        .st-emotion-cache-1xw8zd0 {
            padding: 1rem 1rem 3rem 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# === NUTRITION MENU SCREEN ===
if st.session_state.step == "nutrition_menu":
    st.markdown("## 👩‍⚕️ Nutrition Menu")

    col1, col2, _ = st.columns([1.2, 4, 1])
    with col1:
        st.markdown('<div class="back-btn">', unsafe_allow_html=True)
        if st.button("⬅️ Back"):
            st.session_state.step = "main_menu"
        st.markdown('</div>', unsafe_allow_html=True)

    # Menu buttons
    if st.button("➕ New Entry"):
        st.session_state.step = "new_entry"

    if st.button("📄 View Previous Data"):
        st.session_state.step = "view_old_data"

    if st.button("✏️ Modify Old Data"):
        st.session_state.step = "modify_old_data"

# === SIMULATED OTHER SCREENS ===
elif st.session_state.step == "new_entry":
    st.write("📝 New Entry Form Goes Here")
    if st.button("⬅️ Back to Menu"):
        st.session_state.step = "nutrition_menu"

elif st.session_state.step == "view_old_data":
    st.write("📋 Showing previous data...")
    if st.button("⬅️ Back to Menu"):
        st.session_state.step = "nutrition_menu"

elif st.session_state.step == "modify_old_data":
    st.write("🔧 Modify your old data here.")
    if st.button("⬅️ Back to Menu"):
        st.session_state.step = "nutrition_menu"

elif st.session_state.step == "main_menu":
    st.write("🏠 Main Menu (replace with your logic)")
