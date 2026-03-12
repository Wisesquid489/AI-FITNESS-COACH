import cv2
import mediapipe as mp
import numpy as np
import time

mp_pose = mp.solutions.pose

# ================================
# GLOBAL MOVEMENT TRACKING
# ================================
PREV_ELBOW_X = None
PREV_ELBOW_ANGLE = None
PREV_TIME = None

# Separate tracking for Lateral Raise (important!)
PREV_LAT_ANGLE = None
PREV_LAT_TIME = None


# ---------------- ANGLE CALCULATION ----------------
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = abs(radians * 180.0 / np.pi)
    return 360 - angle if angle > 180 else angle


# ---------------- LANDMARK EXTRACTION ----------------
def get_pose_landmarks(frame):
    with mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as pose:

        image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(image)

        if not result.pose_landmarks:
            return None

        h, w, _ = frame.shape
        return {
            i: (int(lm.x * w), int(lm.y * h))
            for i, lm in enumerate(result.pose_landmarks.landmark)
        }


# =================================================
# EXERCISE IDENTIFICATION
# =================================================
def identify_exercise(lm):
    try:
        shoulder = lm[12]
        elbow = lm[14]
        wrist = lm[16]
        hip = lm[24]
        knee = lm[26]
        ankle = lm[28]
    except KeyError:
        return "Unknown Exercise"

    elbow_angle = calculate_angle(shoulder, elbow, wrist)
    knee_angle = calculate_angle(hip, knee, ankle)

    legs_straight = knee_angle > 160

    # Shoulder Press
    if elbow_angle < 100 and wrist[1] < shoulder[1] and legs_straight:
        return "Shoulder Press"

    # Bicep Curl (DO NOT TOUCH - WORKING)
    if elbow_angle < 90 and legs_straight:
        return "Bicep Curl"

    # ✅ NEW: Lateral Raise
    arm_horizontal = abs(wrist[1] - shoulder[1]) < 40
    elbow_soft = 130 < elbow_angle < 170

    if arm_horizontal and elbow_soft:
        return "Lateral Raise"

    return "Unknown Exercise"


# =================================================
# POSTURE CHECK
# =================================================
def check_posture(lm, ex):
    global PREV_ELBOW_X, PREV_ELBOW_ANGLE, PREV_TIME
    global PREV_LAT_ANGLE, PREV_LAT_TIME

    try:
        shoulder = lm[12]
        elbow = lm[14]
        wrist = lm[16]
        hip = lm[24]
    except KeyError:
        return "CORRECT", "Posture unclear."

    elbow_angle = calculate_angle(shoulder, elbow, wrist)
    current_time = time.time()

    # ===============================================
    # BICEP CURL (UNCHANGED)
    # ===============================================
    if ex == "Bicep Curl":

        if PREV_ELBOW_X is not None:
            horizontal_movement = abs(elbow[0] - PREV_ELBOW_X)
            if horizontal_movement > 25:
                PREV_ELBOW_X = elbow[0]
                PREV_ELBOW_ANGLE = elbow_angle
                PREV_TIME = current_time
                return "INCORRECT", "Avoid swinging your arm. Keep elbow fixed."

        if PREV_ELBOW_ANGLE is not None and PREV_TIME is not None:
            time_diff = current_time - PREV_TIME
            if time_diff > 0:
                angular_speed = abs(elbow_angle - PREV_ELBOW_ANGLE) / time_diff
                if angular_speed > 300:
                    PREV_ELBOW_X = elbow[0]
                    PREV_ELBOW_ANGLE = elbow_angle
                    PREV_TIME = current_time
                    return "INCORRECT", "Slow down. Control the movement."

        if elbow_angle < 30:
            return "INCORRECT", "Do not over-bend your elbow."

        if elbow_angle > 170:
            return "INCORRECT", "Control the extension."

        elbow_forward = abs(elbow[0] - shoulder[0])
        if elbow_forward > 60:
            return "INCORRECT", "Keep elbows close to body."

        body_sway = abs(shoulder[0] - hip[0])
        if body_sway > 70:
            return "INCORRECT", "Avoid using body momentum."

        PREV_ELBOW_X = elbow[0]
        PREV_ELBOW_ANGLE = elbow_angle
        PREV_TIME = current_time

        return "CORRECT", "Good curl form."


    # ===============================================
    # SHOULDER PRESS (UNCHANGED)
    # ===============================================
    if ex == "Shoulder Press":

        if elbow_angle > 175:
            return "INCORRECT", "Do not lock your elbows."

        if elbow_angle < 50:
            return "INCORRECT", "Press fully upward."

        if wrist[1] > shoulder[1]:
            return "INCORRECT", "Raise arms fully overhead."

        body_lean = abs(shoulder[0] - hip[0])
        if body_lean > 80:
            return "INCORRECT", "Keep torso upright."

        return "CORRECT", "Good shoulder press form."


    # ===============================================
    # ✅ NEW: LATERAL RAISE (FIXED SWING DETECTION)
    # ===============================================
    if ex == "Lateral Raise":

        shoulder_angle = calculate_angle(hip, shoulder, elbow)

        # SPEED / MOMENTUM CHECK
        if PREV_LAT_ANGLE is not None and PREV_LAT_TIME is not None:
            time_diff = current_time - PREV_LAT_TIME
            if time_diff > 0:
                angular_speed = abs(shoulder_angle - PREV_LAT_ANGLE) / time_diff
                if angular_speed > 350:
                    PREV_LAT_ANGLE = shoulder_angle
                    PREV_LAT_TIME = current_time
                    return "INCORRECT", "Avoid swinging. Lift with control."

        # TORSO LEAN CHECK
        body_lean = abs(shoulder[0] - hip[0])
        if body_lean > 60:
            return "INCORRECT", "Do not lean back. Keep torso straight."

        # OVER RAISING CHECK
        if wrist[1] < shoulder[1] - 60:
            return "INCORRECT", "Do not raise above shoulder level."

        # ELBOW LOCK CHECK
        if elbow_angle > 175:
            return "INCORRECT", "Keep slight bend in elbows."

        PREV_LAT_ANGLE = shoulder_angle
        PREV_LAT_TIME = current_time

        return "CORRECT", "Good lateral raise form."


    # ===============================================
    # OTHER EXERCISES (DO NOT TOUCH PUSHUP, SQUAT ETC)
    # ===============================================
    return "CORRECT", "Posture OK."