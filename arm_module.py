import streamlit as st
import cv2
import mediapipe as mp
import numpy as np

def run_muac():
    st.write("📸 Upload an image with arm visible for MUAC estimation.")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        st.image(image_rgb, caption="Uploaded Image", use_column_width=True)

        mp_pose = mp.solutions.pose
        with mp_pose.Pose(static_image_mode=True) as pose:
            results = pose.process(image_rgb)
            if not results.pose_landmarks:
                st.warning("⚠️ No human pose landmarks detected. Please upload a clearer image.")
                return None, None

            landmarks = results.pose_landmarks.landmark

            # Left arm keypoints
            shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
            elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]

            # Convert to pixel coords
            h, w, _ = image.shape
            shoulder_coords = np.array([shoulder.x * w, shoulder.y * h])
            elbow_coords = np.array([elbow.x * w, elbow.y * h])
            arm_length_px = np.linalg.norm(elbow_coords - shoulder_coords)

            # Convert pixels to cm using heuristic (this is rough!)
            pixels_per_cm = 15  # ← You can calibrate this value
            muac_cm = round(arm_length_px / pixels_per_cm, 2)

            # Classify MUAC status
            if muac_cm < 11.5:
                status = "Severely Malnourished"
            elif muac_cm < 12.5:
                status = "Moderately Malnourished"
            else:
                status = "Normal"

            st.success(f"MUAC: {muac_cm} cm → {status}")
            return muac_cm, status

    return None, None
