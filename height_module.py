import streamlit as st
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
import cv2
from PIL import Image
from streamlit_image_coordinates import streamlit_image_coordinates

# Load MoveNet model from TF Hub
movenet = hub.load("https://tfhub.dev/google/movenet/singlepose/lightning/4")
input_size = 192  # Model expects 192x192

KEYPOINT_DICT = {
    "nose": 0,
    "left_ankle": 15,
    "right_ankle": 16
}

def detect_keypoints_movenet(image):
    img_resized = tf.image.resize_with_pad(tf.convert_to_tensor(image), input_size, input_size)
    input_tensor = tf.expand_dims(img_resized, axis=0)
    input_tensor = tf.cast(input_tensor, dtype=tf.int32)
    
    outputs = movenet.signatures['serving_default'](input_tensor)
    keypoints = outputs['output_0'][0, 0, :, :]  # (17, 3)

    h, w, _ = image.shape
    nose_y = int(keypoints[KEYPOINT_DICT["nose"]][1] * h)
    left_ankle_y = int(keypoints[KEYPOINT_DICT["left_ankle"]][1] * h)
    right_ankle_y = int(keypoints[KEYPOINT_DICT["right_ankle"]][1] * h)
    foot_y = max(left_ankle_y, right_ankle_y)

    return nose_y, foot_y

def draw_landmarks(image, head_y, foot_y):
    annotated = image.copy()
    center_x = image.shape[1] // 2
    cv2.line(annotated, (center_x, head_y), (center_x, foot_y), (0, 255, 0), 2)
    cv2.circle(annotated, (center_x, head_y), 5, (255, 0, 0), -1)
    cv2.circle(annotated, (center_x, foot_y), 5, (0, 0, 255), -1)
    return annotated

def get_pixel_distance(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))

def run_height_estimator():
    st.markdown("Upload a full-body image **with a visible reference object**, and specify its real-world length.")
    img_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])

    if img_file:
        image = Image.open(img_file).convert("RGB")
        img_np = np.array(image)
        image_copy = img_np.copy()

        reference_length = st.number_input("Enter the real-world length of the reference object (in cm)", min_value=1.0, step=0.5)

        st.subheader("Step 1: Click two points on the reference object")

        if "points" not in st.session_state:
            st.session_state.points = []

        for i, (x, y) in enumerate(st.session_state.points):
            cv2.circle(image_copy, (x, y), 8, (0, 0, 255), -1)
            cv2.putText(image_copy, f"P{i+1}", (x+10, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        coords = streamlit_image_coordinates(Image.fromarray(image_copy), key="click_img")

        if coords and len(st.session_state.points) < 2:
            st.session_state.points.append((int(coords['x']), int(coords['y'])))

        if st.button("🔄 Reset Points"):
            st.session_state.points = []

        if len(st.session_state.points) == 2:
            x1, y1 = st.session_state.points[0]
            x2, y2 = st.session_state.points[1]
            pixel_dist = get_pixel_distance((x1, y1), (x2, y2))
            calibration_factor = reference_length / pixel_dist
            st.success(f"Calibration: {calibration_factor:.4f} cm/pixel")

            st.subheader("Step 2: Estimating height from landmarks")
            head_y, foot_y = detect_keypoints_movenet(img_np)

            if head_y is not None and foot_y is not None:
                pixel_height = abs(foot_y - head_y)
                estimated_height = calibration_factor * pixel_height
                annotated_img = draw_landmarks(img_np, head_y, foot_y)
                st.image(annotated_img, caption="Estimated Height", channels="RGB")
                st.success(f"Estimated Height: **{estimated_height:.2f} cm**")
                return round(estimated_height, 2)
            else:
                st.error("❌ Could not detect landmarks. Try another image.")
    return None
