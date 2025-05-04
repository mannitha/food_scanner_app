import streamlit as st 
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp

def run_muac():
    CALIBRATION_FACTOR_MUAC = 0.09166
    mp_pose = mp.solutions.pose

    def load_image(uploaded_file):
        img = Image.open(uploaded_file)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def detect_arm_keypoints(image):
        with mp_pose.Pose(static_image_mode=True) as pose:
            results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if results.pose_landmarks:
                h, w, _ = image.shape
                landmarks = results.pose_landmarks.landmark
                shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
                elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
                shoulder_point = (int(shoulder.x * w), int(shoulder.y * h))
                elbow_point = (int(elbow.x * w), int(elbow.y * h))
                return shoulder_point, elbow_point
        return None, None

    def draw_arm_landmarks(image, shoulder_point, elbow_point):
        annotated = image.copy()
        cv2.line(annotated, shoulder_point, elbow_point, (0,255,0), 2)
        cv2.circle(annotated, shoulder_point, 5, (255,0,0), -1)
        cv2.circle(annotated, elbow_point, 5, (0,0,255), -1)
        return annotated

    def classify_muac(muac_cm):
        if muac_cm < 11.5:
            return "Severe Acute Malnutrition (SAM)", "❗", "red"
        elif muac_cm < 12.5:
            return "Moderate Acute Malnutrition (MAM)", "⚠", "orange"
        else:
            return "Normal", "✅", "green"

    st.title("MUAC Measurement")

    col1, col2 = st.columns([1, 1])
    with col1:
        camera_button = st.button("📷 Camera", use_container_width=True)
    with col2:
        upload_button = st.button("🖼 Upload", use_container_width=True)

    image = None

    if "muac_input_mode" not in st.session_state:
        st.session_state.muac_input_mode = None

    if camera_button:
        st.session_state.muac_input_mode = "camera"
    elif upload_button:
        st.session_state.muac_input_mode = "upload"

    if st.session_state.muac_input_mode == "camera":
        image_data = st.camera_input("Take a picture")
        if image_data:
            image = load_image(image_data)

    elif st.session_state.muac_input_mode == "upload":
        uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            image = load_image(uploaded_file)

    if image is not None:
        shoulder_point, elbow_point = detect_arm_keypoints(image)

        if shoulder_point and elbow_point:
            pixel_distance = np.linalg.norm(np.array(shoulder_point) - np.array(elbow_point))
            annotated_image = draw_arm_landmarks(image, shoulder_point, elbow_point)
            st.image(annotated_image, caption="Detected Shoulder and Elbow", use_column_width=True)

            estimated_muac = CALIBRATION_FACTOR_MUAC * pixel_distance
            st.success(f"Estimated MUAC: *{estimated_muac:.2f} cm*")

            status, icon, color = classify_muac(estimated_muac)
            st.markdown(f"### {icon} MUAC Status: *:{color}[{status}]*")

            return round(estimated_muac, 2), status  # ✅ Properly return both MUAC value and status
        else:
            st.error("Keypoints not detected. Try a clearer upper-body photo.")
            return None, None

    return None, None
