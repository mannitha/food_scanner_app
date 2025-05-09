import streamlit as st 
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp

def run_muac():
        
    # --- Custom CSS ---
    st.markdown("""
    <style>
        /* Green upload button */
        div.stButton > button:first-child {
            background-color: #69AE43;
            color: white;
            border: none;
            padding: 10px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 4px 2px;
            cursor: pointer;
            border-radius: 8px;
        }

        div.stButton > button:first-child:hover {
            background-color: #45a049;
        }

        .nutrition-header {
            font-size: 18px !important;
            margin-bottom: 10px !important;
        }

        /* Extra button styles */
        .green-button {
            background-color: #69ae43 !important;
        }

        .blue-button {
            background-color: #1889cb !important;
        }

    </style>
    """, unsafe_allow_html=True)

    # --- Calibration Factors ---
    CALIBRATION_FACTORS = {
        '4-6': 0.085,   # Calibration for 4-6 years old
        '7-9': 0.088,   # Calibration for 7-9 years old
        '10-12': 0.092, # Calibration for 10-12 years old
        '13-15': 0.096  # Calibration for 13-15 years old
    }

    mp_pose = mp.solutions.pose

    def load_image(uploaded_file):
        img = Image.open(uploaded_file)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def detect_arm_keypoints(image):
        with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
            results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if results.pose_landmarks:
                h, w, _ = image.shape
                landmarks = results.pose_landmarks.landmark
                
                # Get both left and right arm points for better reliability
                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
                left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
                right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
                
                # Convert to pixel coordinates
                left_shoulder_point = (int(left_shoulder.x * w), int(left_shoulder.y * h))
                left_elbow_point = (int(left_elbow.x * w), int(left_elbow.y * h))
                right_shoulder_point = (int(right_shoulder.x * w), int(right_shoulder.y * h))
                right_elbow_point = (int(right_elbow.x * w), int(right_elbow.y * h))
                
                return left_shoulder_point, left_elbow_point, right_shoulder_point, right_elbow_point
        return None, None, None, None

    def draw_arm_landmarks(image, shoulder_point, elbow_point):
        annotated = image.copy()
        cv2.line(annotated, shoulder_point, elbow_point, (0, 255, 0), 3)
        cv2.circle(annotated, shoulder_point, 8, (255, 0, 0), -1)
        cv2.circle(annotated, elbow_point, 8, (0, 0, 255), -1)
        return annotated

    def classify_muac(muac_cm, age_group):
        # Age-specific MUAC classification thresholds (in cm)
        if age_group in ['4-6', '7-9']:
            if muac_cm < 12.5:
                return "Acute Malnutrition", "red"
            elif muac_cm < 13.5:
                return "Risk of Malnutrition", "orange"
            else:
                return "Normal Nutrition Status", "green"
        else:  # 10-15 years
            if muac_cm < 13.5:
                return "Acute Malnutrition", "red"
            elif muac_cm < 14.5:
                return "Risk of Malnutrition", "orange"
            else:
                return "Normal Nutrition Status", "green"

    # --- UI Starts Here ---
    age_group = st.selectbox(
        "Select the child's age group:",
        options=list(CALIBRATION_FACTORS.keys()),
        index=2
    )

    upload_button = st.button("Upload Image", use_container_width=True)

    image = None
    uploaded_file = None

    if "input_mode" not in st.session_state:
        st.session_state.input_mode = None

    if upload_button:
        st.session_state.input_mode = "upload"

    if st.session_state.input_mode == "upload":
        uploaded_file = st.file_uploader("Upload an image of the child's arm", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = load_image(uploaded_file)

    # --- Estimation and Classification ---
    if image is not None:
        left_shoulder, left_elbow, right_shoulder, right_elbow = detect_arm_keypoints(image)
        
        # Use whichever arm is more visible
        shoulder_point, elbow_point = None, None
        if left_shoulder and left_elbow:
            shoulder_point, elbow_point = left_shoulder, left_elbow
        elif right_shoulder and right_elbow:
            shoulder_point, elbow_point = right_shoulder, right_elbow

        if shoulder_point and elbow_point:
            pixel_distance = np.linalg.norm(np.array(shoulder_point) - np.array(elbow_point))
            annotated_image = draw_arm_landmarks(image, shoulder_point, elbow_point)
            st.image(annotated_image, caption="Detected Shoulder and Elbow Points", use_column_width=True)

            # Get the appropriate calibration factor for the age group
            cal_factor = CALIBRATION_FACTORS[age_group]
            estimated_muac = cal_factor * pixel_distance
            
            st.success(f"""
            **Measurement Results:**
            - Estimated MUAC: {estimated_muac:.2f} cm
            """)

            status, color = classify_muac(estimated_muac, age_group)
            st.markdown(f'<div class="nutrition-header"> Nutrition Status: 'f'<span style="color: {color};">{status}</span></div>',unsafe_allow_html=True)
    
            # Add interpretation guidance
            st.info("""
            **Interpretation Guide:**
            - For children 4-9 years: <12.5cm = Acute Malnutrition, 12.5-13.5cm = Risk, >13.5cm = Normal
            - For children 10-15 years: <13.5cm = Acute Malnutrition, 13.5-14.5cm = Risk, >14.5cm = Normal
            """)
        else:
            st.error("""
            Keypoints not detected. Please ensure:
            1. The child's upper arm is clearly visible from shoulder to elbow
            2. The arm is not obstructed by clothing
            3. The photo is taken from a front/side angle with good lighting
            """)

if __name__ == "__main__":
    run_muac()
