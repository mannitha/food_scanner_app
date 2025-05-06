import streamlit as st
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp

mp_pose = mp.solutions.pose

# Constants
AVERAGE_SHOULDER_WIDTH_CM = 26  # average for child/female, adjust as needed

def load_image(uploaded_file):
    img = Image.open(uploaded_file)
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def detect_keypoints(image):
    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if results.pose_landmarks:
            h, w, _ = image.shape
            landmarks = results.pose_landmarks.landmark
            nose_y = int(landmarks[mp_pose.PoseLandmark.NOSE].y * h)
            foot_left_y = int(landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX].y * h)
            foot_right_y = int(landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX].y * h)
            toe_y = max(foot_left_y, foot_right_y)

            shoulder_left = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            shoulder_right = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

            shoulder_width_px = abs((shoulder_right.x - shoulder_left.x) * w)
            return nose_y, toe_y, shoulder_width_px
    return None, None, None

def draw_landmarks(image, head_y, toe_y):
    annotated = image.copy()
    center_x = image.shape[1] // 2
    cv2.line(annotated, (center_x, head_y), (center_x, toe_y), (0,255,0), 2)
    cv2.circle(annotated, (center_x, head_y), 5, (255,0,0), -1)
    cv2.circle(annotated, (center_x, toe_y), 5, (0,0,255), -1)
    return annotated

def run_height_estimator():
    st.title("📏 Automatic Height Estimation")

    col1, col2 = st.columns([1, 1])
    with col1:
        camera_button = st.button("📷 Camera", use_container_width=True)
    with col2:
        upload_button = st.button("🖼 Upload", use_container_width=True)

    image = None

    if "input_mode" not in st.session_state:
        st.session_state.input_mode = None

    if camera_button:
        st.session_state.input_mode = "camera"
    elif upload_button:
        st.session_state.input_mode = "upload"

    if st.session_state.input_mode == "camera":
        image_data = st.camera_input("Take a picture")
        if image_data:
            image = load_image(image_data)
    elif st.session_state.input_mode == "upload":
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = load_image(uploaded_file)

    if image is not None:
        head_y, toe_y, shoulder_width_px = detect_keypoints(image)

        if head_y is not None and toe_y is not None and shoulder_width_px > 0:
            pixel_height = abs(toe_y - head_y)
            calibration_factor = AVERAGE_SHOULDER_WIDTH_CM / shoulder_width_px
            estimated_height = pixel_height * calibration_factor

            annotated_image = draw_landmarks(image, head_y, toe_y)
            st.image(annotated_image, caption="Detected head and toes", use_column_width=True)

            st.write(f"🧮 Pixel height: `{pixel_height}` px")
            st.write(f"📐 Shoulder width: `{shoulder_width_px:.1f}` px")
            st.write(f"🔧 Calibration factor: `{calibration_factor:.4f} cm/pixel`")
            st.success(f"🎯 Estimated Height: **{estimated_height:.2f} cm**")

            return round(estimated_height, 2)
        else:
            st.error("❌ Keypoints not fully detected. Try a clearer full-body photo.")

    return None
