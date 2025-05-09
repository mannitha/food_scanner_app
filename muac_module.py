import streamlit as st
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp

def muac():

    # Average real-world shoulder widths (cm) by age group
    SHOULDER_WIDTHS = {
        '4-6': 26,
        '7-9': 28,
        '10-12': 31,
        '13-15': 34
    }

    mp_pose = mp.solutions.pose

    def load_image(uploaded_file):
        img = Image.open(uploaded_file)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def detect_keypoints(image):
        with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
            results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if results.pose_landmarks:
                h, w, _ = image.shape
                landmarks = results.pose_landmarks.landmark

                def point(landmark):
                    return (int(landmark.x * w), int(landmark.y * h))

                return {
                    "left_shoulder": point(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]),
                    "right_shoulder": point(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]),
                    "left_elbow": point(landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]),
                    "right_elbow": point(landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]),
                }
        return {}

    def draw_landmarks(image, p1, p2):
        annotated = image.copy()
        cv2.line(annotated, p1, p2, (0, 255, 0), 3)
        cv2.circle(annotated, p1, 8, (255, 0, 0), -1)
        cv2.circle(annotated, p2, 8, (0, 0, 255), -1)
        return annotated

    def classify_muac(muac_cm, age_group):
        if age_group in ['4-6', '7-9']:
            if muac_cm < 12.5:
                return "Acute Malnutrition", "red"
            elif muac_cm < 13.5:
                return "Risk of Malnutrition", "orange"
            else:
                return "Normal", "green"
        else:
            if muac_cm < 13.5:
                return "Acute Malnutrition", "red"
            elif muac_cm < 14.5:
                return "Risk of Malnutrition", "orange"
            else:
                return "Normal", "green"

    st.title("MUAC Estimation using Image")

    age_group = st.selectbox("Select Age Group:", options=list(SHOULDER_WIDTHS.keys()))
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = load_image(uploaded_file)
        keypoints = detect_keypoints(image)

        if "left_shoulder" in keypoints and "right_shoulder" in keypoints:
            shoulder_pixel_width = np.linalg.norm(np.array(keypoints["left_shoulder"]) - np.array(keypoints["right_shoulder"]))
            real_shoulder_width_cm = SHOULDER_WIDTHS[age_group]
            scale = real_shoulder_width_cm / shoulder_pixel_width  # cm per pixel

            # Pick better visible arm
            if "left_elbow" in keypoints:
                arm_pixel_len = np.linalg.norm(np.array(keypoints["left_shoulder"]) - np.array(keypoints["left_elbow"]))
                annotated = draw_landmarks(image, keypoints["left_shoulder"], keypoints["left_elbow"])
            elif "right_elbow" in keypoints:
                arm_pixel_len = np.linalg.norm(np.array(keypoints["right_shoulder"]) - np.array(keypoints["right_elbow"]))
                annotated = draw_landmarks(image, keypoints["right_shoulder"], keypoints["right_elbow"])
            else:
                st.error("Elbow not visible. Try another image.")
                return

            muac_cm = scale * arm_pixel_len

            st.image(annotated, caption="Detected Shoulder-Elbow", use_column_width=True)
            st.success(f"Estimated MUAC: {muac_cm:.2f} cm")

            status, color = classify_muac(muac_cm, age_group)
            st.markdown(f'<h4 style="color:{color};">Nutrition Status: {status}</h4>', unsafe_allow_html=True)

        else:
            st.error("Could not detect shoulders clearly. Try a clearer side image.")

if __name__ == "__main__":
    muac()
