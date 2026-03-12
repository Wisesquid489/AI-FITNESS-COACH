"""
Advanced Pose Analysis System
Professional-grade movement tracking for fitness applications
"""

import numpy as np
from collections import deque
import time


class MovementTracker:
    """
    Tracks movement patterns, velocity, and form quality over time
    """
    def __init__(self, exercise_name, buffer_size=30):
        self.exercise_name = exercise_name
        self.buffer_size = buffer_size
        
        # Movement history buffers
        self.angle_history = deque(maxlen=buffer_size)
        self.velocity_history = deque(maxlen=buffer_size)
        self.position_history = deque(maxlen=buffer_size)
        self.timestamp_history = deque(maxlen=buffer_size)
        
        # Rep tracking
        self.current_phase = "NEUTRAL"  # NEUTRAL, ECCENTRIC, CONCENTRIC
        self.rep_count = 0
        self.rep_quality_scores = []
        
        # Form tracking
        self.form_violations = []
        self.peak_angles = []
        self.rom_scores = []  # Range of Motion scores
        
    def add_frame(self, landmarks, timestamp):
        """Add new frame data for analysis"""
        if not landmarks:
            return
        
        # Calculate key metrics
        angles = self._calculate_exercise_angles(landmarks)
        velocity = self._calculate_velocity(angles)
        
        # Store in history
        self.angle_history.append(angles)
        self.velocity_history.append(velocity)
        self.position_history.append(landmarks)
        self.timestamp_history.append(timestamp)
        
        # Analyze movement phase
        self._detect_movement_phase(angles, velocity)
        
    def _calculate_exercise_angles(self, landmarks):
        """Calculate all relevant angles for the exercise"""
        angles = {}
        
        try:
            # Upper body angles
            if self.exercise_name in ["Bicep Curl", "Hammer Curl", "Shoulder Press", "Lateral Raise"]:
                # Right arm
                shoulder_r = landmarks[12]
                elbow_r = landmarks[14]
                wrist_r = landmarks[16]
                angles['elbow_r'] = self._angle_between_points(shoulder_r, elbow_r, wrist_r)
                
                # Shoulder elevation
                hip_r = landmarks[24]
                angles['shoulder_elevation_r'] = self._angle_between_points(hip_r, shoulder_r, elbow_r)
                
                # Wrist position
                angles['wrist_height'] = wrist_r[1]
                angles['elbow_height'] = elbow_r[1]
                
            # Lower body angles
            elif self.exercise_name in ["Squat", "Lunges"]:
                # Right leg
                hip_r = landmarks[24]
                knee_r = landmarks[26]
                ankle_r = landmarks[28]
                angles['knee_r'] = self._angle_between_points(hip_r, knee_r, ankle_r)
                
                # Hip angle
                shoulder_r = landmarks[12]
                angles['hip_r'] = self._angle_between_points(shoulder_r, hip_r, knee_r)
                
                # Torso angle (for squat depth)
                angles['torso_angle'] = self._angle_between_points(shoulder_r, hip_r, ankle_r)
                
                # Knee tracking (should be over toes)
                angles['knee_forward'] = knee_r[0] - ankle_r[0]
                
            # Core exercises
            elif self.exercise_name == "Plank":
                shoulder = landmarks[12]
                hip = landmarks[24]
                ankle = landmarks[28]
                angles['body_line'] = self._angle_between_points(shoulder, hip, ankle)
                angles['hip_sag'] = hip[1]  # Y position (lower = sagging)
                
        except (KeyError, IndexError):
            pass
        
        return angles
    
    def _angle_between_points(self, a, b, c):
        """Calculate angle at point b"""
        a, b, c = np.array(a), np.array(b), np.array(c)
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = abs(radians * 180.0 / np.pi)
        return 360 - angle if angle > 180 else angle
    
    def _calculate_velocity(self, current_angles):
        """Calculate angular velocity"""
        if len(self.angle_history) < 2:
            return {}
        
        prev_angles = self.angle_history[-1]
        time_diff = 0.2  # 200ms between frames
        
        velocity = {}
        for key in current_angles:
            if key in prev_angles:
                velocity[key] = (current_angles[key] - prev_angles[key]) / time_diff
        
        return velocity
    
    def _detect_movement_phase(self, angles, velocity):
        """Detect which phase of movement (eccentric/concentric)"""
        if not angles or not velocity:
            return
        
        # Get primary angle for exercise
        primary_angle_key = self._get_primary_angle_key()
        if primary_angle_key not in angles or primary_angle_key not in velocity:
            return
        
        angle = angles[primary_angle_key]
        vel = velocity[primary_angle_key]
        
        # Define movement phases based on exercise
        if self.exercise_name in ["Bicep Curl", "Hammer Curl"]:
            # Concentric: elbow flexing (angle decreasing)
            # Eccentric: elbow extending (angle increasing)
            if vel < -20 and self.current_phase != "CONCENTRIC":
                self.current_phase = "CONCENTRIC"
                if self.current_phase == "ECCENTRIC":
                    self._complete_rep(angles)
            elif vel > 20 and self.current_phase != "ECCENTRIC":
                self.current_phase = "ECCENTRIC"
                
        elif self.exercise_name == "Squat":
            # Eccentric: going down (knee angle decreasing)
            # Concentric: going up (knee angle increasing)
            if vel < -15 and self.current_phase != "ECCENTRIC":
                self.current_phase = "ECCENTRIC"
            elif vel > 15 and self.current_phase != "CONCENTRIC":
                self.current_phase = "CONCENTRIC"
                if self.current_phase == "ECCENTRIC":
                    self._complete_rep(angles)

        elif self.exercise_name == "Lateral Raise":
            # Concentric: arm raising (shoulder angle increasing)
            # Eccentric: arm lowering (shoulder angle decreasing)

            if vel > 15 and self.current_phase != "CONCENTRIC":
                if self.current_phase == "ECCENTRIC":
                    self._complete_rep(angles)
                self.current_phase = "CONCENTRIC"

            elif vel < -15 and self.current_phase != "ECCENTRIC":
                self.current_phase = "ECCENTRIC"

    def _get_primary_angle_key(self):
      mapping = {
        "Bicep Curl": "elbow_r",
        "Hammer Curl": "elbow_r",
        "Shoulder Press": "elbow_r",
        "Squat": "knee_r",
        "Lunges": "knee_r",
        "Plank": "body_line",
        "Lateral Raise": "shoulder_elevation_r"  # ✅ ADDED
    }
      return mapping.get(self.exercise_name, "elbow_r")
    
    def _complete_rep(self, angles):
        """Mark rep as complete and analyze quality"""
        self.rep_count += 1
        
        # Analyze rep quality
        quality_score = self._analyze_rep_quality()
        self.rep_quality_scores.append(quality_score)
        
        # Check range of motion
        rom_score = self._check_range_of_motion(angles)
        self.rom_scores.append(rom_score)
    
    def _analyze_rep_quality(self):
        """Analyze the quality of the last rep"""
        if len(self.velocity_history) < 10:
            return 50
        
        # Check for:
        # 1. Smooth movement (no jerking)
        # 2. Controlled tempo
        # 3. Full range of motion
        
        recent_velocities = list(self.velocity_history)[-10:]
        primary_key = self._get_primary_angle_key()
        
        if not recent_velocities or primary_key not in recent_velocities[0]:
            return 50
        
        velocities = [v.get(primary_key, 0) for v in recent_velocities]
        
        # Smoothness score (lower variance = smoother)
        variance = np.var(velocities) if velocities else 0
        smoothness_score = max(0, 100 - variance / 10)
        
        # Tempo score (not too fast, not too slow)
        avg_velocity = np.mean(np.abs(velocities)) if velocities else 0
        ideal_velocity = 50  # degrees per second
        tempo_score = max(0, 100 - abs(avg_velocity - ideal_velocity))
        
        # Overall quality
        quality = (smoothness_score + tempo_score) / 2
        return min(100, max(0, quality))
    
    def _check_range_of_motion(self, angles):
        """Check if full range of motion was achieved"""
        primary_key = self._get_primary_angle_key()
        if primary_key not in angles:
            return 50
        
        # Get min and max angles from recent history
        recent_angles = [a.get(primary_key, 0) for a in list(self.angle_history)[-20:]]
        if not recent_angles:
            return 50
        
        rom = max(recent_angles) - min(recent_angles)
        
        # Expected ROM for each exercise
        expected_rom = {
            "Bicep Curl": 120,  # 30° to 150°
            "Squat": 90,        # 90° to 180°
            "Shoulder Press": 100,
            "Plank": 10,
            "Lateral Raise": 80        # Should be minimal
        }
        
        expected = expected_rom.get(self.exercise_name, 90)
        rom_score = min(100, (rom / expected) * 100)
        
        return rom_score
    
    def get_real_time_feedback(self):
        """Get real-time feedback for current movement"""
        if len(self.angle_history) < 5:
            return {
                "phase": "STARTING",
                "feedback": "Begin your movement",
                "quality": "UNKNOWN"
            }
        
        # Analyze recent movement
        recent_quality = np.mean(self.rep_quality_scores[-3:]) if self.rep_quality_scores else 70
        recent_rom = np.mean(self.rom_scores[-3:]) if self.rom_scores else 70
        
        feedback = []
        quality = "GOOD"
        
        if recent_quality < 50:
            feedback.append("⚠️ Movement too jerky - slow down")
            quality = "POOR"
        elif recent_quality < 70:
            feedback.append("⚠️ Control your movement better")
            quality = "FAIR"
        
        if recent_rom < 60:
            feedback.append("⚠️ Increase range of motion")
            quality = "POOR"
        elif recent_rom < 80:
            feedback.append("⚠️ Go deeper/higher")
            quality = "FAIR"
        
        if not feedback:
            feedback.append("✅ Excellent form!")
        
        return {
            "phase": self.current_phase,
            "feedback": " | ".join(feedback),
            "quality": quality,
            "rep_count": self.rep_count,
            "avg_quality": round(recent_quality, 1),
            "avg_rom": round(recent_rom, 1)
        }
    
    def get_workout_summary(self):
        """Get summary of entire workout"""
        if not self.rep_quality_scores:
            return {
                "total_reps": 0,
                "avg_quality": 0,
                "avg_rom": 0,
                "grade": "N/A"
            }
        
        avg_quality = np.mean(self.rep_quality_scores)
        avg_rom = np.mean(self.rom_scores) if self.rom_scores else 0
        
        # Calculate grade
        overall_score = (avg_quality + avg_rom) / 2
        if overall_score >= 90:
            grade = "A+"
        elif overall_score >= 80:
            grade = "A"
        elif overall_score >= 70:
            grade = "B"
        elif overall_score >= 60:
            grade = "C"
        else:
            grade = "D"
        
        return {
            "total_reps": self.rep_count,
            "avg_quality": round(avg_quality, 1),
            "avg_rom": round(avg_rom, 1),
            "grade": grade,
            "form_consistency": self._calculate_consistency()
        }
    
    def _calculate_consistency(self):
        """Calculate how consistent form was across reps"""
        if len(self.rep_quality_scores) < 2:
            return 100
        
        variance = np.var(self.rep_quality_scores)
        consistency = max(0, 100 - variance)
        return round(consistency, 1)
