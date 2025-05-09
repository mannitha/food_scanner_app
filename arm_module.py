import streamlit as st
import cv2
import numpy as np
import mediapipe as mp
from PIL import Image

def run_muac():
    st.markdown('<h1 class="main-header">📏 Arm Circumference Estimation</h1>', unsafe_allow_html=True)
    st.markdown("#### Upload an image of the child's arm (straight, side view, with a reference object like an A4 sheet):")
    uploaded_file = st.file_uploader("Upload Arm Image", type=["jpg", "jpeg", "png"], key="muac_upload")

    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        mp_pose = mp.solutions.pose
        with mp_pose.Pose(static_image_mode=True, model_complexity=2) as pose:
            results = pose.process(image_rgb)

            if results.pose_landmarks:
                annotated_image = image_rgb.copy()
                mp.solutions.drawing_utils.draw_landmarks(
                    annotated_image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

                # Extract relevant landmarks
                shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
                elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]

                h, w, _ = image.shape
                shoulder_point = (int(shoulder.x * w), int(shoulder.y * h))
                elbow_point = (int(elbow.x * w), int(elbow.y * h))

                # Draw points and line
                cv2.circle(annotated_image, shoulder_point, 5, (0, 255, 0), -1)
                cv2.circle(annotated_image, elbow_point, 5, (0, 255, 0), -1)
                cv2.line(annotated_image, shoulder_point, elbow_point, (255, 0, 0), 2)

                st.image(annotated_image, caption="Landmarks Detected", use_column_width=True)

                # Estimate pixel distance
                pixel_distance = np.linalg.norm(np.array(shoulder_point) - np.array(elbow_point))

                # Assume actual shoulder to elbow length ≈ 18cm
                actual_length_cm = 18.0
                pixels_per_cm = pixel_distance / actual_length_cm

                # Estimate MUAC: 30% of upper arm length
                muac_pixels = pixel_distance * 0.3
                estimated_muac = muac_pixels / pixels_per_cm
                estimated_muac = round(estimated_muac, 2)

                st.success(f"Estimated MUAC: {estimated_muac} cm")

                # Classification
                if estimated_muac < 12.5:
                    status = "Acute Malnutrition"
                    color = "red"
                elif 12.5 <= estimated_muac <= 13.5:
                    status = "At Risk"
                    color = "orange"
                else:
                    status = "Normal"
                    color = "green"

                st.markdown(f'<div class="nutrition-header"> Nutrition Status: '
                            f'<span style="color: {color};">{status}</span></div>', unsafe_allow_html=True)

                st.info("""
                **Interpretation Guide:**
                - For children 4-9 years: <12.5cm = Acute Malnutrition, 12.5-13.5cm = Risk, >13.5cm = Normal
                - For children 10-15 years: <13.5cm = Acute Malnutrition, 13.5-14.5cm = Risk, >14.5cm = Normal
                """)

                return estimated_muac, status

            else:
                st.error("Could not detect landmarks. Try a clearer image with the full upper arm visible.")

    return None, None
