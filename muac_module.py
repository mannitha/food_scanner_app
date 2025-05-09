import streamlit as st
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp


def muac():
    st.title("MUAC Estimator Using Body Proportions")

    # Average height by age (cm)
    AVERAGE_HEIGHTS = {
        4: 102,
        5: 109,
        6: 115,
        7: 120,
        8: 126,
        9: 132,
        10: 138,
        11: 143,
        12: 149,
        13: 156,
        14: 162,
        15: 167
    }

    mp_pose = mp.solutions.pose

    def load_image(uploaded_file):
        img = Image.open(uploaded_file)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def detect_landmarks(image):
        with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
            results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if results.pose_landmarks:
                h, w, _ = image.shape
                lm = results.pose_landmarks.landmark
                def pt(idx):
                    return int(lm[idx].x * w), int(lm[idx].y * h)
                return {
                    "left_shoulder": pt(mp_pose.PoseLandmark.LEFT_SHOULDER),
                    "left_elbow": pt(mp_pose.PoseLandmark.LEFT_ELBOW),
                    "right_shoulder": pt(mp_pose.PoseLandmark.RIGHT_SHOULDER),
                    "right_elbow": pt(mp_pose.PoseLandmark.RIGHT_ELBOW),
                    "head_top": pt(mp_pose.PoseLandmark.NOSE),
                    "left_foot": pt(mp_pose.PoseLandmark.LEFT_HEEL),
                    "right_foot": pt(mp_pose.PoseLandmark.RIGHT_HEEL),
                }
            return None

    def draw_keypoints(image, points):
        annotated = image.copy()
        for name, point in points.items():
            cv2.circle(annotated, point, 6, (0, 255, 0), -1)
        return annotated

    def estimate_muac(landmarks, avg_height_cm):
        shoulder = landmarks["left_shoulder"] if landmarks["left_shoulder"] else landmarks["right_shoulder"]
        elbow = landmarks["left_elbow"] if landmarks["left_elbow"] else landmarks["right_elbow"]
        foot_y = max(landmarks["left_foot"][1], landmarks["right_foot"][1])
        head_y = landmarks["head_top"][1]

        body_pixel_height = abs(foot_y - head_y)
        px_per_cm = body_pixel_height / avg_height_cm

        arm_pixel_len = np.linalg.norm(np.array(elbow) - np.array(shoulder))
        arm_length_cm = arm_pixel_len / px_per_cm
        muac_cm = 0.33 * arm_length_cm

        return muac_cm

    def classify_muac(muac_cm, age):
        if age < 10:
            if muac_cm < 12.5:
                return "Acute Malnutrition", "red"
            elif muac_cm < 13.5:
                return "Risk of Malnutrition", "orange"
            else:
                return "Normal Nutrition Status", "green"
        else:
            if muac_cm < 13.5:
                return "Acute Malnutrition", "red"
            elif muac_cm < 14.5:
                return "Risk of Malnutrition", "orange"
            else:
                return "Normal Nutrition Status", "green"

    # UI
    age = st.selectbox("Select Child's Age", options=list(AVERAGE_HEIGHTS.keys()), index=2)
    uploaded_file = st.file_uploader("Upload full body image of child", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = load_image(uploaded_file)
        landmarks = detect_landmarks(image)

        if landmarks:
            annotated = draw_keypoints(image, landmarks)
            st.image(annotated, caption="Detected Keypoints", use_column_width=True)

            muac_cm = estimate_muac(landmarks, AVERAGE_HEIGHTS[age])
            st.success(f"Estimated MUAC: {muac_cm:.2f} cm")

            status, color = classify_muac(muac_cm, age)
            st.markdown(f'<h4>Nutrition Status: <span style="color:{color}">{status}</span></h4>', unsafe_allow_html=True)

            st.info("""
            *Interpretation Guide:*
            - Age < 10: <12.5 = Acute, 12.5–13.5 = Risk, >13.5 = Normal
            - Age 10+: <13.5 = Acute, 13.5–14.5 = Risk, >14.5 = Normal
            """)
        else:
            st.error("Could not detect full body keypoints. Please ensure full body is visible in image.")


if __name__ == "__main__":
    muac()
