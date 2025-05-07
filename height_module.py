import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import numpy as np
import cv2
import base64
from io import BytesIO

def pil_to_data_url(pil_image):
    """Convert PIL image to base64-encoded data URL (PNG)."""
    buffered = BytesIO()
    pil_image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()
    img_b64 = base64.b64encode(img_bytes).decode()
    return f"data:image/png;base64,{img_b64}"

def estimate_height_with_manual_scale(image, points):
    """Estimate height using two points on a 30 cm reference object."""
    if len(points) != 2:
        return image, None, "Please mark exactly two points on the scale."

    p1, p2 = points
    pixel_distance = np.linalg.norm(np.array(p1) - np.array(p2))

    if pixel_distance < 10:
        return image, None, "Scale is too short or points are too close."

    cm_per_pixel = 30 / pixel_distance
    person_height_pixels = image.shape[0]
    estimated_height_cm = person_height_pixels * cm_per_pixel

    # Draw annotations
    cv2.line(image, p1, p2, (0, 255, 0), 2)
    cv2.putText(image, f"{estimated_height_cm:.2f} cm",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    return image, estimated_height_cm, None

def run_height_estimator():
    st.markdown("📷 **Upload a full-body image with a 30 cm steel scale beside the person.**")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        img_data_url = pil_to_data_url(img_pil)

        st.markdown("🟢 **Click exactly two points marking the ends of the steel scale (top and bottom).**")

        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=3,
            stroke_color="#00FF00",
            background_image=img_data_url,
            update_streamlit=True,
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
                return None
            else:
                st.image(cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB), caption="Processed Image", use_column_width=True)
                st.success(f"✅ Estimated Height: **{height_cm:.2f} cm**")
                return round(height_cm, 2)
        else:
            st.info("Please mark **exactly two points** on the steel scale.")
