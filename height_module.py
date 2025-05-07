import streamlit as st
import cv2
import numpy as np
from PIL import Image
from streamlit_drawable_canvas import st_canvas

# Define the function directly here if height_with_scale is merged
def estimate_height_with_manual_scale(image, points):
    # Your height estimation logic here
    # Return: annotated_img, height_cm, error (None if no error)
    pass  # Replace with actual logic

def run_height_estimator():
    st.markdown("📷 **Upload a full-body image with a 32 cm steel scale beside the person.**")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], key="height_image_upload")

    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)

        st.markdown("🟢 **Click two points: top and bottom of the steel scale.**")

        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=3,
            stroke_color="#00FF00",
            background_image=Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)),
            update_streamlit=True,
            height=img.shape[0],
            width=img.shape[1],
            drawing_mode="point",
            point_display_radius=5,
            key="canvas_height",
        )

        if canvas_result.json_data and len(canvas_result.json_data["objects"]) == 2:
            points = [(int(obj["left"]), int(obj["top"])) for obj in canvas_result.json_data["objects"]]

            with st.spinner("Estimating height..."):
                annotated_img, height_cm, error = estimate_height_with_manual_scale(img.copy(), points)

            if error:
                st.error(error)
            else:
                st.image(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB), caption="Processed Image", use_column_width=True)
                st.success(f"✅ Estimated Height: **{height_cm:.2f} cm**")
