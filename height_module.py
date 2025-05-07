# height_module.py

import streamlit as st
import cv2
import numpy as np
from PIL import Image
from height_with_scale import estimate_height_with_manual_scale
from streamlit_drawable_canvas import st_canvas

def run_height_estimator():
    st.subheader("Upload Image for Height Estimation")
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        image = image.convert("RGB")
        image_np = np.array(image)
        h, w = image_np.shape[:2]

        canvas_result = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",
            stroke_width=2,
            stroke_color="#00FF00",
            background_image=image,
            update_streamlit=True,
            height=h,
            width=w,
            drawing_mode="line",
            key="canvas"
        )

        if canvas_result.json_data and "objects" in canvas_result.json_data:
            objs = canvas_result.json_data["objects"]
            if len(objs) >= 1 and objs[0]["type"] == "line":
                pt1 = (int(objs[0]["x1"]), int(objs[0]["y1"]))
                pt2 = (int(objs[0]["x2"]), int(objs[0]["y2"]))
                output_image, height_cm, error = estimate_height_with_manual_scale(image_np.copy(), [pt1, pt2])
                if error:
                    st.error(error)
                    return None
                st.image(output_image, caption=f"Estimated Height: {height_cm:.2f} cm", use_column_width=True)
                return round(height_cm, 2)

    return None
