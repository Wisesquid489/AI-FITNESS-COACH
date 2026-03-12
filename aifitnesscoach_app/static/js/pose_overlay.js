// Pose Overlay Drawing Functions

// Draw skeleton overlay on canvas
function drawPoseSkeleton(canvas, landmarks, color = '#00e5ff', lineWidth = 3) {
    const ctx = canvas.getContext('2d');
    
    if (!landmarks || landmarks.length === 0) return;
    
    // Define body connections (MediaPipe pose connections)
    const connections = [
        // Face
        [0, 1], [1, 2], [2, 3], [3, 7],
        [0, 4], [4, 5], [5, 6], [6, 8],
        
        // Torso
        [9, 10],  // Mouth
        [11, 12], // Shoulders
        [11, 23], [12, 24], // Shoulders to hips
        [23, 24], // Hips
        
        // Right arm
        [12, 14], [14, 16], [16, 18], [16, 20], [16, 22],
        
        // Left arm
        [11, 13], [13, 15], [15, 17], [15, 19], [15, 21],
        
        // Right leg
        [24, 26], [26, 28], [28, 30], [28, 32], [30, 32],
        
        // Left leg
        [23, 25], [25, 27], [27, 29], [27, 31], [29, 31]
    ];
    
    // Draw connections (lines)
    ctx.strokeStyle = color;
    ctx.lineWidth = lineWidth;
    ctx.lineCap = 'round';
    
    connections.forEach(([start, end]) => {
        if (landmarks[start] && landmarks[end]) {
            ctx.beginPath();
            ctx.moveTo(landmarks[start].x * canvas.width, landmarks[start].y * canvas.height);
            ctx.lineTo(landmarks[end].x * canvas.width, landmarks[end].y * canvas.height);
            ctx.stroke();
        }
    });
    
    // Draw landmarks (points)
    ctx.fillStyle = color;
    landmarks.forEach(landmark => {
        if (landmark) {
            ctx.beginPath();
            ctx.arc(
                landmark.x * canvas.width,
                landmark.y * canvas.height,
                5,
                0,
                2 * Math.PI
            );
            ctx.fill();
        }
    });
}

// Draw guide pose for specific exercise
function drawGuidePose(canvas, exerciseName) {
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Semi-transparent background
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
    ctx.fillRect(0, 0, width, height);
    
    // Guide text
    ctx.fillStyle = '#00e5ff';
    ctx.font = 'bold 20px Poppins';
    ctx.textAlign = 'center';
    ctx.fillText(`Align yourself for: ${exerciseName}`, width / 2, 30);
    
    ctx.font = '14px Poppins';
    ctx.fillText('Match the blue guide pose', width / 2, 55);
    
    // Draw guide skeleton based on exercise
    const guidePose = getGuidePoseForExercise(exerciseName, width, height);
    if (guidePose) {
        drawPoseSkeleton(canvas, guidePose, '#00e5ff', 4);
    }
}

// Get ideal pose landmarks for each exercise
function getGuidePoseForExercise(exerciseName, width, height) {
    const centerX = width / 2;
    const centerY = height / 2;
    
    // Simplified guide poses (key landmarks only)
    const guides = {
        "Bicep Curl": [
            null, null, null, null, null, null, null, null, null, null, null,
            { x: 0.4, y: 0.3 },  // 11: Left shoulder
            { x: 0.6, y: 0.3 },  // 12: Right shoulder
            { x: 0.35, y: 0.45 }, // 13: Left elbow
            { x: 0.65, y: 0.45 }, // 14: Right elbow
            { x: 0.35, y: 0.6 },  // 15: Left wrist
            { x: 0.65, y: 0.6 },  // 16: Right wrist
            null, null, null, null, null, null, null,
            { x: 0.4, y: 0.55 },  // 23: Left hip
            { x: 0.6, y: 0.55 },  // 24: Right hip
            { x: 0.4, y: 0.75 },  // 25: Left knee
            { x: 0.6, y: 0.75 },  // 26: Right knee
            { x: 0.4, y: 0.95 },  // 27: Left ankle
            { x: 0.6, y: 0.95 }   // 28: Right ankle
        ],
        
        "Squat": [
            null, null, null, null, null, null, null, null, null, null, null,
            { x: 0.4, y: 0.25 },  // 11: Left shoulder
            { x: 0.6, y: 0.25 },  // 12: Right shoulder
            { x: 0.35, y: 0.4 },  // 13: Left elbow
            { x: 0.65, y: 0.4 },  // 14: Right elbow
            { x: 0.3, y: 0.5 },   // 15: Left wrist
            { x: 0.7, y: 0.5 },   // 16: Right wrist
            null, null, null, null, null, null, null,
            { x: 0.4, y: 0.5 },   // 23: Left hip
            { x: 0.6, y: 0.5 },   // 24: Right hip
            { x: 0.4, y: 0.7 },   // 25: Left knee (bent)
            { x: 0.6, y: 0.7 },   // 26: Right knee (bent)
            { x: 0.4, y: 0.9 },   // 27: Left ankle
            { x: 0.6, y: 0.9 }    // 28: Right ankle
        ],
        
        "Shoulder Press": [
            null, null, null, null, null, null, null, null, null, null, null,
            { x: 0.4, y: 0.3 },   // 11: Left shoulder
            { x: 0.6, y: 0.3 },   // 12: Right shoulder
            { x: 0.35, y: 0.25 }, // 13: Left elbow (up)
            { x: 0.65, y: 0.25 }, // 14: Right elbow (up)
            { x: 0.35, y: 0.15 }, // 15: Left wrist (above head)
            { x: 0.65, y: 0.15 }, // 16: Right wrist (above head)
            null, null, null, null, null, null, null,
            { x: 0.4, y: 0.55 },  // 23: Left hip
            { x: 0.6, y: 0.55 },  // 24: Right hip
            { x: 0.4, y: 0.75 },  // 25: Left knee
            { x: 0.6, y: 0.75 },  // 26: Right knee
            { x: 0.4, y: 0.95 },  // 27: Left ankle
            { x: 0.6, y: 0.95 }   // 28: Right ankle
        ],
        
        "Lateral Raise": [
            null, null, null, null, null, null, null, null, null, null, null,
            { x: 0.4, y: 0.3 },   // 11: Left shoulder
            { x: 0.6, y: 0.3 },   // 12: Right shoulder
            { x: 0.2, y: 0.35 },  // 13: Left elbow (out)
            { x: 0.8, y: 0.35 },  // 14: Right elbow (out)
            { x: 0.1, y: 0.35 },  // 15: Left wrist (extended)
            { x: 0.9, y: 0.35 },  // 16: Right wrist (extended)
            null, null, null, null, null, null, null,
            { x: 0.4, y: 0.55 },  // 23: Left hip
            { x: 0.6, y: 0.55 },  // 24: Right hip
            { x: 0.4, y: 0.75 },  // 25: Left knee
            { x: 0.6, y: 0.75 },  // 26: Right knee
            { x: 0.4, y: 0.95 },  // 27: Left ankle
            { x: 0.6, y: 0.95 }   // 28: Right ankle
        ],
        
        "Plank": [
            null, null, null, null, null, null, null, null, null, null, null,
            { x: 0.35, y: 0.4 },  // 11: Left shoulder
            { x: 0.45, y: 0.4 },  // 12: Right shoulder
            { x: 0.3, y: 0.5 },   // 13: Left elbow
            { x: 0.4, y: 0.5 },   // 14: Right elbow
            { x: 0.25, y: 0.55 }, // 15: Left wrist
            { x: 0.35, y: 0.55 }, // 16: Right wrist
            null, null, null, null, null, null, null,
            { x: 0.55, y: 0.4 },  // 23: Left hip
            { x: 0.65, y: 0.4 },  // 24: Right hip
            { x: 0.6, y: 0.4 },   // 25: Left knee
            { x: 0.7, y: 0.4 },   // 26: Right knee
            { x: 0.7, y: 0.4 },   // 27: Left ankle
            { x: 0.8, y: 0.4 }    // 28: Right ankle
        ]
    };
    
    return guides[exerciseName] || guides["Bicep Curl"];
}

// Check if user pose matches guide pose (alignment check)
function checkPoseAlignment(userLandmarks, exerciseName, threshold = 0.15) {
    if (!userLandmarks || userLandmarks.length === 0) {
        return { aligned: false, score: 0, message: "No pose detected" };
    }
    
    const guidePose = getGuidePoseForExercise(exerciseName, 1, 1);
    if (!guidePose) {
        return { aligned: true, score: 100, message: "Ready" };
    }
    
    // Check key landmarks (shoulders, hips, knees)
    const keyPoints = [11, 12, 23, 24, 25, 26];
    let totalDistance = 0;
    let validPoints = 0;
    
    keyPoints.forEach(idx => {
        if (guidePose[idx] && userLandmarks[idx]) {
            const dx = userLandmarks[idx].x - guidePose[idx].x;
            const dy = userLandmarks[idx].y - guidePose[idx].y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            totalDistance += distance;
            validPoints++;
        }
    });
    
    if (validPoints === 0) {
        return { aligned: false, score: 0, message: "Position yourself in frame" };
    }
    
    const avgDistance = totalDistance / validPoints;
    const score = Math.max(0, Math.min(100, (1 - avgDistance / threshold) * 100));
    
    if (score >= 70) {
        return { aligned: true, score: Math.round(score), message: "✅ Aligned! Ready to start" };
    } else if (score >= 40) {
        return { aligned: false, score: Math.round(score), message: "⚠️ Almost there... adjust position" };
    } else {
        return { aligned: false, score: Math.round(score), message: "❌ Move to match the guide" };
    }
}
