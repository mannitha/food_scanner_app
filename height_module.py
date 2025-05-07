import streamlit as st
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp

# Use an estimated cm per pixel (from any known sample image)
CM_PER_PIXEL = 0.45  # Adjust based on your initial test subject

mp_pose = mp.solutions.pose

def load_image(uploaded_file):
    img = Image.open(uploaded_file)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def get_height_from_head_to_toes(image):
    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if results.pose_landmarks:
            h, w, _ = image.shape
            landmarks = results.pose_landmarks.landmark

            nose_y = int(landmarks[mp_pose.PoseLandmark.NOSE].y * h)
            left_ankle_y = int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y * h)
            right_ankle_y = int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y * h)
            foot_y = max(left_ankle_y, right_ankle_y)

            pixel_height = abs(foot_y - nose_y)
            return pixel_height, nose_y, foot_y
    return None, None, None

def run_head_to_toe_estimator():
    st.title("Head-to-Toe Height Estimation (Camera Aligned to Head)")

    uploaded_file = st.file_uploader("Upload image (head at top, full body visible)", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = load_image(uploaded_file)
        pixel_height, head_y, foot_y = get_height_from_head_to_toes(image)

        if pixel_height:
            estimated_height_cm = pixel_height * CM_PER_PIXEL

            center_x = image.shape[1] // 2
            annotated = image.copy()
            cv2.line(annotated, (center_x, head_y), (center_x, foot_y), (0, 255, 0), 2)

            st.image(annotated, caption=f"Pixel Height: {pixel_height}px", use_column_width=True)
            st.success(f"Estimated Height: *{estimated_height_cm:.2f} cm*")
            return round(estimated_height_cm, 2)
        else:
            st.error("Could not detect full body. Make sure head is at top and feet are visible.")

    return None
