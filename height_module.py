import streamlit as st
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp
from streamlit_drawable_canvas import st_canvas
from io import BytesIO
import base64
import math

SCALE_REAL_CM = 32  # Real-world length of the reference steel scale in cm
mp_pose = mp.solutions.pose

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

def calculate_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

def draw_landmarks(image, head_y, foot_y):
    annotated = image.copy()
    center_x = image.shape[1] // 2
    cv2.line(annotated, (center_x, head_y), (center_x, foot_y), (0, 255, 0), 2)
    cv2.circle(annotated, (center_x, head_y), 5, (255, 0, 0), -1)
    cv2.circle(annotated, (center_x, foot_y), 5, (0, 0, 255), -1)
    return annotated

def pil_to_url(pil_image):
    buf = BytesIO()
    pil_image.save(buf, format="PNG")
    byte_im = buf.getvalue()
    base64_str = base64.b64encode(byte_im).decode()
    return f"data:image/png;base64,{base64_str}"

def run_height_estimator():
    st.title("Height Estimation with Reference Scale")

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
        st.subheader("Step 1: Mark two points on the 32 cm scale (placed beside the person)")

        rgb_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
       canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=2,
    stroke_color="#000",
    background_image=rgb_pil,  # Direct PIL image here
    update_streamlit=True,
    height=image.shape[0],
    width=image.shape[1],
    drawing_mode="point",
    point_display_radius=5,
    key="scale_canvas"
)


        if canvas_result.json_data and len(canvas_result.json_data["objects"]) == 2:
            p1 = canvas_result.json_data["objects"][0]["left"], canvas_result.json_data["objects"][0]["top"]
            p2 = canvas_result.json_data["objects"][1]["left"], canvas_result.json_data["objects"][1]["top"]
            pixel_distance = calculate_distance(p1, p2)
            pixels_per_cm = pixel_distance / SCALE_REAL_CM

            head_y, foot_y = detect_keypoints(image)
            if head_y is not None and foot_y is not None:
                pixel_height = abs(foot_y - head_y)
                estimated_height = pixel_height / pixels_per_cm
                annotated_image = draw_landmarks(image, head_y, foot_y)
                st.image(annotated_image, caption="Detected head and foot", use_column_width=True)
                st.success(f"Estimated Height: *{estimated_height:.2f} cm*")
                return round(estimated_height, 2)
            else:
                st.error("Keypoints not detected. Try a clearer full-body photo.")
        else:
            st.info("Please mark exactly 2 points on the reference scale.")

    return None
