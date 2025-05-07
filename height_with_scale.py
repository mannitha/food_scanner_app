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

    # Open and display the image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    # Instructions for the user
    st.write("Please mark two points for the scale (e.g., a ruler) and two points on the child (top of the head and bottom of the feet).")

    # Canvas for marking points
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",  # Transparent fill
        stroke_width=3,
        stroke_color="#000",  # Black color for marking points
        background_image=image,
        update_streamlit=True,
        height=image.height,
        width=image.width,
        drawing_mode="point",  # User will draw points on the image
        key="height_canvas"
    )

    if not canvas_result.json_data:
        return None

    points = canvas_result.json_data["objects"]
    
    # Check if we have at least 4 points marked
    if len(points) < 4:
        st.warning("Please mark at least 4 points (2 for scale, 2 for child).")
        return None

    # Sort points by their vertical position (top attribute)
    coords = [(p["top"], p["left"]) for p in points]
    coords.sort()

    # Assign points to scale and child (top and bottom points)
    scale_top, scale_bottom = coords[0], coords[1]
    child_top, child_bottom = coords[2], coords[3]

    def euclidean(p1, p2):
        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    # Calculate pixel distances
    scale_px = euclidean(scale_top, scale_bottom)
    child_px = euclidean(child_top, child_bottom)

    # Input for real scale height (cm)
    scale_cm = st.number_input("Enter real scale height (cm)", min_value=1.0, value=30.0)

    if scale_px == 0:
        st.error("Invalid scale points. The two scale points should not be the same.")
        return None

    # Calculate pixel per centimeter ratio and then child height
    px_per_cm = scale_px / scale_cm
    child_height_cm = child_px / px_per_cm

    # Display the result
    st.success(f"Estimated Child Height: {child_height_cm:.2f} cm")
    return round(child_height_cm, 2)
