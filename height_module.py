import streamlit as st
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
from streamlit_drawable_canvas import st_canvas

# Constants
SCALE_LENGTH_CM = 32  # length of the physical steel scale in cm
mp_pose = mp.solutions.pose

# --- Utility Functions ---
def load_image(uploaded_file):
    img = Image.open(uploaded_file)
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

def draw_landmarks(image, head_y, foot_y, pt1=None, pt2=None):
    annotated = image.copy()
    center_x = image.shape[1] // 2
    cv2.line(annotated, (center_x, head_y), (center_x, foot_y), (0,255,0), 2)
    cv2.circle(annotated, (center_x, head_y), 5, (255,0,0), -1)
    cv2.circle(annotated, (center_x, foot_y), 5, (0,0,255), -1)
    if pt1 and pt2:
        cv2.line(annotated, pt1, pt2, (0, 255, 255), 2)
    return annotated

# --- Main App ---
def run_height_estimator():
    st.title("📏 Height Estimator (Manual Scale Points)")

    image = None
    uploaded_file = st.file_uploader("📷 Upload full-body image with a 32 cm steel scale", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = load_image(uploaded_file)
        st.markdown("🟡 **Mark exactly two points on the steel scale (top and bottom).**")

        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=3,
            stroke_color="#FF0000",
            background_image=Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)),
            update_streamlit=True,
            height=image.shape[0],
            width=image.shape[1],
            drawing_mode="point",
            point_display_radius=5,
            key="canvas"
        )

        if canvas_result.json_data and len(canvas_result.json_data["objects"]) == 2:
            points = [(int(obj["left"]), int(obj["top"])) for obj in canvas_result.json_data["objects"]]

            # Calculate pixels per cm
            pt1, pt2 = points
            pixel_dist = np.linalg.norm(np.array(pt1) - np.array(pt2))
            pixels_per_cm = pixel_dist / SCALE_LENGTH_CM

            head_y, foot_y = detect_keypoints(image)

            if head_y is not None and foot_y is not None:
                pixel_height = abs(foot_y - head_y)
                estimated_height = pixel_height / pixels_per_cm

                annotated = draw_landmarks(image, head_y, foot_y, pt1, pt2)
                st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), caption="Detected head, foot and scale", use_column_width=True)

                st.success(f"✅ Estimated Height: **{estimated_height:.2f} cm**")
            else:
                st.error("❌ Could not detect keypoints. Please try a clearer image.")

        else:
            st.info("Please mark **exactly two points** on the steel scale.")
