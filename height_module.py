# height_module.py
import streamlit as st
import cv2
import numpy as np
from streamlit_drawable_canvas import st_canvas
import mediapipe as mp
from PIL import Image

SCALE_LENGTH_CM = 32
mp_pose = mp.solutions.pose

def run_height_estimator():
    st.markdown("### Upload an Image with a Steel Scale")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    if uploaded_file is None:
        return None

    image = Image.open(uploaded_file).convert("RGB")
    image_np = np.array(image)

    st.image(image, caption="Uploaded Image", use_column_width=True)

    st.markdown("### Draw Two Points on the Steel Scale (Top and Bottom)")
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=3,
        stroke_color="#000000",
        background_image=image,
        update_streamlit_image_coordinates=True,
        height=image_np.shape[0],
        width=image_np.shape[1],
        drawing_mode="point",
        key="canvas",
    )

    if canvas_result.json_data and len(canvas_result.json_data["objects"]) >= 2:
        scale_pts = []
        for obj in canvas_result.json_data["objects"][:2]:
            x, y = obj["left"], obj["top"]
            scale_pts.append((x, y))

        height_cm, annotated_img, error = estimate_height_with_manual_scale(image_np, scale_pts)
        if error:
            st.error(error)
            return None
        st.image(annotated_img, caption=f"Estimated Height: {height_cm:.1f} cm", use_column_width=True)
        return round(height_cm, 1)
    else:
        st.info("Please mark two points on the scale.")
        return None

def estimate_height_with_manual_scale(image, scale_pts):
    orig = image.copy()
    h_img, w_img, _ = image.shape

    pt1, pt2 = scale_pts
    scale_pixel_length = np.linalg.norm(np.array(pt1) - np.array(pt2))
    pixels_per_cm = scale_pixel_length / SCALE_LENGTH_CM

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(orig, cv2.COLOR_RGB2BGR))
        if not results.pose_landmarks:
            return None, None, "❌ Body landmarks not detected."

        landmarks = results.pose_landmarks.landmark
        head_y = int(landmarks[mp_pose.PoseLandmark.NOSE].y * h_img)
        foot_l = int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y * h_img)
        foot_r = int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y * h_img)
        foot_y = max(foot_l, foot_r)

        pixel_height = foot_y - head_y
        height_cm = pixel_height / pixels_per_cm

        center_x = w_img // 2
        cv2.line(image, (center_x, head_y), (center_x, foot_y), (255, 255, 0), 2)
        cv2.circle(image, (center_x, head_y), 5, (255, 0, 0), -1)
        cv2.circle(image, (center_x, foot_y), 5, (0, 255, 0), -1)

        return height_cm, image, None
