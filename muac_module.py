import streamlit as st 
import cv2
import numpy as np
from PIL import Image
import mediapipe as mp

def muac():

    mp_pose = mp.solutions.pose

    def load_image(uploaded_file):
        img = Image.open(uploaded_file)
        return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    def detect_arm_keypoints(image):
        with mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5) as pose:
            results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            if results.pose_landmarks:
                h, w, _ = image.shape
                landmarks = results.pose_landmarks.landmark
                
                left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
                left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
                right_shoulder = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
                right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]
                
                left_shoulder_point = (int(left_shoulder.x * w), int(left_shoulder.y * h))
                left_elbow_point = (int(left_elbow.x * w), int(left_elbow.y * h))
                right_shoulder_point = (int(right_shoulder.x * w), int(right_shoulder.y * h))
                right_elbow_point = (int(right_elbow.x * w), int(right_elbow.y * h))
                
                return left_shoulder_point, left_elbow_point, right_shoulder_point, right_elbow_point
        return None, None, None, None

    def draw_landmarks(image, points):
        annotated = image.copy()
        for i, (x, y) in enumerate(points):
            cv2.circle(annotated, (x, y), 8, (0, 0, 255), -1)
            cv2.putText(annotated, f"P{i+1}", (x+10, y-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        if len(points) == 2:
            cv2.line(annotated, points[0], points[1], (0, 255, 0), 2)
        return annotated

    def get_pixel_distance(p1, p2):
        return np.linalg.norm(np.array(p1) - np.array(p2))

    def classify_muac(muac_cm):
        # Standard MUAC classification thresholds (in cm)
        if muac_cm < 12.5:
            return "Severe Acute Malnutrition", "red"
        elif muac_cm < 13.5:
            return "Moderate Acute Malnutrition", "orange"
        else:
            return "Normal Nutrition Status", "green"

    # --- UI Starts Here ---
    st.title("MUAC Measurement")
    st.write("Upload an image containing both the arm and a reference object of known length")

    # Initialize session state
    if "points" not in st.session_state:
        st.session_state.points = []
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    if "ref_length" not in st.session_state:
        st.session_state.ref_length = None

    # File uploader
    uploaded_file = st.file_uploader("Upload image with arm and reference object", type=["jpg", "jpeg", "png"])
    
    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        image = load_image(uploaded_file)
        img_np = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_copy = img_np.copy()

        # Display image with points if any
        if st.session_state.points:
            image_copy = draw_landmarks(image_copy, st.session_state.points)
        st.image(image_copy, caption="Uploaded Image", use_column_width=True)

        # Reference object measurement
        st.session_state.ref_length = st.number_input(
            "Enter the real-world length of the reference object (in cm)", 
            min_value=1.0, 
            step=0.5,
            key="ref_length"
        )

        # Point selection instructions
        st.markdown("*Click two points on the reference object to measure its pixel length*")
        
        # Get coordinates from image click
        coords = st.image_coordinates(image_copy, key="click_img")
        
        if coords and len(st.session_state.points) < 2:
            st.session_state.points.append((int(coords['x']), int(coords['y'])))
            st.experimental_rerun()

        if st.button("Reset Points"):
            st.session_state.points = []
            st.experimental_rerun()

        # Calculate calibration when ready
        if len(st.session_state.points) == 2 and st.session_state.ref_length:
            # Calculate pixel distance and calibration factor
            ref_pixel_dist = get_pixel_distance(st.session_state.points[0], st.session_state.points[1])
            calibration_factor = st.session_state.ref_length / ref_pixel_dist
            st.success(f"Calibration: {calibration_factor:.4f} cm/pixel")

            # Detect arm keypoints
            left_shoulder, left_elbow, right_shoulder, right_elbow = detect_arm_keypoints(image)
            
            # Use whichever arm is more visible
            shoulder_point, elbow_point = None, None
            if left_shoulder and left_elbow:
                shoulder_point, elbow_point = left_shoulder, left_elbow
            elif right_shoulder and right_elbow:
                shoulder_point, elbow_point = right_shoulder, right_elbow

            if shoulder_point and elbow_point:
                # Calculate MUAC
                pixel_distance = np.linalg.norm(np.array(shoulder_point) - np.array(elbow_point))
                estimated_muac = calibration_factor * pixel_distance
                
                # Draw arm landmarks
                annotated_image = draw_arm_landmarks(image, shoulder_point, elbow_point)
                st.image(annotated_image, caption="Detected Shoulder and Elbow Points", use_column_width=True)
                
                # Display results
                st.success(f"""
                *Measurement Results:*
                - Estimated MUAC: {estimated_muac:.2f} cm
                """)

                status, color = classify_muac(estimated_muac)
                st.markdown(f'<div class="nutrition-header"> Nutrition Status: 'f'<span style="color: {color};">{status}</span></div>', unsafe_allow_html=True)
                
                # Interpretation guide
                st.info("""
                *Interpretation Guide:*
                - <12.5 cm: Severe Acute Malnutrition
                - 12.5-13.5 cm: Moderate Acute Malnutrition
                - >13.5 cm: Normal Nutrition Status
                """)
            else:
                st.error("""
                Arm keypoints not detected. Please ensure:
                1. The child's upper arm is clearly visible from shoulder to elbow
                2. The arm is not obstructed by clothing
                3. The photo is taken from a front/side angle with good lighting
                """)


if __name__ == "__main__":
    muac()
