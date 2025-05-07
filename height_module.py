import streamlit as st
import cv2
import numpy as np
from streamlit_drawable_canvas import st_canvas
import mediapipe as mp
from PIL import Image

# ⚠️ Removed st.set_page_config from here

SCALE_LENGTH_CM = 32  # Manual steel scale length
mp_pose = mp.solutions.pose


def estimate_height_with_manual_scale(image, scale_pts):
    orig = image.copy()
    h_img, w_img, _ = image.shape

    pt1, pt2 = scale_pts
    scale_pixel_length = np.linalg.norm(np.array(pt1) - np.array(pt2))
    if scale_pixel_length == 0:
        return None, None, "❌ Scale points are too close or identical."

    pixels_per_cm = scale_pixel_length / SCALE_LENGTH_CM

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(orig, cv2.COLOR_BGR2RGB))
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
        cv2.circle(image, (center_x, foot_y), 5, (0, 0, 255), -1)
        cv2.line(image, pt1, pt2, (0, 255, 0), 2)

        return image, height_cm, None


def run_height_estimator():
    st.title("📏 Height Estimator (Using Steel Scale)")
    st.markdown("📷 **Upload a full-body image with a visible 30–32 cm steel scale beside the person.**")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)

        st.markdown("🟢 **Mark two points on the image representing the top and bottom of the steel scale.**")

        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=3,
            stroke_color="#00FF00",
            background_image=Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)),
            height=img.shape[0],
            width=img.shape[1],
            drawing_mode="point",
            point_display_radius=5,
            key="canvas",
        )

        if canvas_result.json_data and len(canvas_result.json_data["objects"]) == 2:
            points = [(int(obj["left"]), int(obj["top"])) for obj in canvas_result.json_data["objects"]]

            with st.spinner("Estimating height..."):
                annotated_img, height_cm, error = estimate_height_with_manual_scale(img.copy(), points)

            if error:
                st.error(error)
            else:
                st.image(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB),
                         caption="Processed Image", use_column_width=True)
                st.success(f"✅ Estimated Height: **{height_cm:.2f} cm**")
                return height_cm
        else:
            st.info("Please mark **exactly two points** on the steel scale.")

    return None
