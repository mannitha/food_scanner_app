import streamlit as st
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp

# Hardcoded calibration factor (in cm/pixel)
CALIBRATION_FACTOR = 0.2031

mp_pose = mp.solutions.pose

def load_image(uploaded_file):
    img = Image.open(uploaded_file)

    # Handle EXIF orientation (common with phone images)
    try:
        exif = img._getexif()
        if exif:
            orientation = exif.get(0x112, 1)
            rotate_values = {
                3: 180,
                6: 270,
                8: 90
            }
            if orientation in rotate_values:
                img = img.rotate(rotate_values[orientation], expand=True)
    except (AttributeError, KeyError, IndexError):
        # If image has no EXIF or orientation info
        pass

    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

def detect_keypoints(image):
    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if results.pose_landmarks:
            h, w, _ = image.shape
            landmarks = results.pose_landmarks.landmark
            head_y = int(landmarks[mp_pose.PoseLandmark.NOSE].y * h)
            foot_left_y = int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y * h)
            foot_right_y = int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y * h)
            foot_y = max(foot_left_y, foot_right_y)
            return head_y, foot_y
    return None, None

def draw_landmarks(image, head_y, foot_y):
    annotated = image.copy()
    center_x = image.shape[1] // 2
    cv2.line(annotated, (center_x, head_y), (center_x, foot_y), (0, 255, 0), 2)
    cv2.circle(annotated, (center_x, head_y), 5, (255, 0, 0), -1)
    cv2.circle(annotated, (center_x, foot_y), 5, (0, 0, 255), -1)
    return annotated

def run_height_estimator():
    """Height estimation wrapped in a function."""
    st.title("Height Measurement")

    col1, col2 = st.columns([1, 1])
    with col1:
        camera_button = st.button("📷 Camera", use_container_width=True)
    with col2:
        upload_button = st.button("🖼 Upload", use_container_width=True)

    image = None
    uploaded_file = None

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
        head_y, foot_y = detect_keypoints(image)

        if head_y is not None and foot_y is not None:
            pixel_height = abs(foot_y - head_y)
            annotated_image = draw_landmarks(image, head_y, foot_y)
            st.image(annotated_image, caption="Detected head and foot", use_column_width=True)

            estimated_height = CALIBRATION_FACTOR * pixel_height
            st.success(f"Estimated Height: *{estimated_height:.2f} cm*")
            return round(estimated_height, 2)
        else:
            st.error("Keypoints not detected. Try a clearer full-body photo.")
            return None

    return None

# Run the height estimator
run_height_estimator()
