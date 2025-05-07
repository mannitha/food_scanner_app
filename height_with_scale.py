# height_with_scale.py
import streamlit as st
from PIL import Image
import math
import numpy as np
from streamlit_drawable_canvas import st_canvas

def estimate_height():
    st.subheader("📏 Upload Image with Scale")
    uploaded_file = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
    
    if not uploaded_file:
        return None

    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    st.write("Mark two points on the scale and two points on the child (top of head to bottom of feet)")

    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",  # Transparent fill
        stroke_width=3,
        stroke_color="#000",
        background_image=image,
        update_streamlit=True,
        height=image.height,
        width=image.width,
        drawing_mode="point",
        key="height_canvas"
    )

    if not canvas_result.json_data:
        return None

    points = canvas_result.json_data["objects"]
    if len(points) < 4:
        st.warning("Please mark at least 4 points (2 for scale, 2 for child).")
        return None

    # Sort points vertically
    coords = [(p["top"], p["left"]) for p in points]
    coords.sort()
    
    scale_top, scale_bottom = coords[0], coords[1]
    child_top, child_bottom = coords[2], coords[3]

    def euclidean(p1, p2):
        return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

    scale_px = euclidean(scale_top, scale_bottom)
    child_px = euclidean(child_top, child_bottom)

    scale_cm = st.number_input("Scale real height (cm)", min_value=1.0, value=30.0)

    if scale_px == 0:
        st.error("Invalid scale points")
        return None

    px_per_cm = scale_px / scale_cm
    child_height_cm = child_px / px_per_cm

    st.success(f"Estimated Child Height: {child_height_cm:.2f} cm")
    return round(child_height_cm, 2)
