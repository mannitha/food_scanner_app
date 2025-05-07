# height_with_scale.py

import cv2
import numpy as np
import mediapipe as mp

SCALE_LENGTH_CM = 32
mp_pose = mp.solutions.pose

def estimate_height_with_manual_scale(image, scale_pts):
    orig = image.copy()
    h_img, w_img, _ = image.shape

    pt1, pt2 = scale_pts
    scale_pixel_length = np.linalg.norm(np.array(pt1) - np.array(pt2))
    pixels_per_cm = scale_pixel_length / SCALE_LENGTH_CM

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(orig, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            return None, None, "❌ Body landmarks not detected."

        landmarks = results.pose_landmarks.landmark
        head_y = int(landmarks[mp_pose.PoseLandmark.NOSE].y * h_img)
        foot_l = int(landmarks[mp_pose.PoseLandmark.LEFT_ANKLE].y * h_img)
        foot_r = int(landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE].y * h_img)
        foot_y = max(foot_l, foot_r)

        pixel_height = foot_y - head_y
        height_cm = pixel_height / pixels_per_cm

        center_x = w_img // 2
        cv2.line(image, (center_x, head_y), (center_x, foot_y), (255, 255, 0), 2)
        cv2.circle(image, (center_x, head_y), 5, (255, 0, 0), -1)
        cv2.circle(image, (center_x, foot_y), 5, (0, 0, 255), -1)
        cv2.line(image, pt1, pt2, (0, 255, 0), 2)

        return image, height_cm, None
