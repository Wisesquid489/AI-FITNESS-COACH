AI Fitness Coach
Project Overview

AI Fitness Coach is a web-based intelligent fitness training system that helps users perform exercises with correct posture using Artificial Intelligence and Computer Vision.
The application acts as a virtual fitness trainer, monitoring body movements through a webcam and providing real-time feedback to ensure exercises are performed safely and effectively.

The system analyzes body posture using pose estimation technology and detects whether an exercise is being performed correctly. If incorrect posture is detected, the system alerts the user and provides guidance to correct their form. This helps improve workout efficiency and reduces the risk of injury.

Features
Real-Time Posture Detection
The system uses computer vision to analyze the user’s body movements through a webcam and detect exercise posture in real time.

Exercise Monitoring
The platform supports multiple exercises such as:
Push-ups
Bicep curl
Shoulder presses
Squats
The system automatically counts repetitions and monitors exercise posture.

Instant Feedback
If the user performs an exercise incorrectly, the system immediately provides feedback so the posture can be corrected.

User Profiles
Users can register and manage their profiles by entering information such as:
Age
Height
Weight
Fitness goals
This data helps the system personalize workout recommendations.

Workout History
The application stores workout data so users can track their progress over time.

AI Diet Recommendations
The system provides diet suggestions based on the user’s health conditions, body metrics, and fitness goals using an AI language model.

Admin Dashboard
The admin panel allows administrators to:
Manage users
Add workout tips
Manage subscription plans
View feedback
Monitor system activity
Subscription System
The platform includes subscription plans with Razorpay payment integration for premium features.

Technologies Used
Frontend
HTML
CSS
JavaScript
Bootstrap
Backend
Python
Django Framework
Database
SQLite3
AI & Computer Vision
OpenCV
MediaPipe Pose
Payment Integration
Razorpay API
AI Diet Recommendation
Grok LLM API

Advantages of the System
Helps users maintain correct exercise posture
Reduces the risk of injury during workouts
Works as a virtual personal trainer
Provides real-time feedback
Tracks fitness progress automatically
Provides AI-based diet suggestions
Can be used anywhere with a webcam

Installation
1 Clone the Repository
git clone https://github.com/Wisesquid489/AI-FITNESS-COACH.git
cd AI-FITNESS-COACH
2 Create Virtual Environment
python -m venv venv

Activate the environment:
Windows

venv\Scripts\activate
Linux / Mac

source venv/bin/activate
3 Install Dependencies
pip install -r requirements.txt

This will install required libraries including:
Django
OpenCV
MediaPipe
NumPy
Razorpay
Other dependencies listed in requirements.txt

4 Apply Migrations
python manage.py migrate
5 Run the Server
python manage.py runserver

Open in browser:
http://127.0.0.1:8000
Grok API Key Setup (Important)

This project includes an AI Diet Recommendation feature powered by the Grok API.
For security reasons, the API key is not included in this repository.

To enable this feature:
Obtain your own Grok API key
Add it to the project configuration where the API is used.

Example:
GROK_API_KEY = "your_api_key_here"
Without adding your own API key, the diet recommendation feature will not work.

Author
Edwin M B
BSc Computer Science
Don Bosco College Mannuthy
University of Calicut
