import streamlit as st
import cv2
import numpy as np
from PIL import Image
from height_with_scale import estimate_height_with_manual_scale  # Make sure this function exists
from streamlit_drawable_canvas import st_canvas

def run_height_estimator():
    st.subheader("Upload Image for Height Estimation")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        # Open and display the image
        image = Image.open(uploaded_file)
        image = image.convert("RGB")
        image_np = np.array(image)
        h, w = image_np.shape[:2]

        # Create the canvas
        canvas_result = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",  # Transparent red color for the drawing
            stroke_width=2,
            stroke_color="#00FF00",  # Green color for drawing the line
            background_image=image,
            update_streamlit=True,
            height=h,
            width=w,
            drawing_mode="line",  # Allowing drawing lines
            key="canvas"
        )

        # Check if canvas has data
        if canvas_result.json_data and "objects" in canvas_result.json_data:
            objs = canvas_result.json_data["objects"]
            if len(objs) >= 1 and objs[0]["type"] == "line":
                pt1 = (int(objs[0]["x1"]), int(objs[0]["y1"]))  # Start point of the line
                pt2 = (int(objs[0]["x2"]), int(objs[0]["y2"]))  # End point of the line
                
                # Debug output to check line coordinates
                st.write(f"Line points: {pt1} to {pt2}")
                
                # Call the height estimation function with the image and line coordinates
                output_image, height_cm, error = estimate_height_with_manual_scale(image_np.copy(), [pt1, pt2])
                
                if error:
                    st.error(error)  # Show error if something went wrong
                    return None
                
                # Display the result image and estimated height
                st.image(output_image, caption=f"Estimated Height: {height_cm:.2f} cm", use_column_width=True)
                return round(height_cm, 2)

    return None
