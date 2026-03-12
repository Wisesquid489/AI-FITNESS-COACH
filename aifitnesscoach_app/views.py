from django.shortcuts import render,redirect,HttpResponse
from . import models
from math import *
import json
from .pose_utils import (
    get_pose_landmarks,
    calculate_angle,
    identify_exercise,
    check_posture
)
from .advanced_pose_analysis import MovementTracker



# Create your views here.
def index(request):
    return render(request,'index.html')

def register(request):
    if request.method=='POST':
        name=request.POST.get('name')
        age=request.POST.get('age')
        gender=request.POST.get('gender')
        email=request.POST.get('email')
        height=request.POST.get('height')
        weight=request.POST.get('weight')
        image=request.FILES.get('image')
        fitnessgoal=request.POST.get('fitnessgoal')
        password=request.POST.get('password')
        confirmpassword=request.POST.get('confirmpassword')
    
        if password==confirmpassword:
            if models.Register.objects.filter(email=email).exists():
                return HttpResponse('email is already exists')
            user=models.Register(name=name,age=age,gender=gender,email=email,fitnessgoal=fitnessgoal,height=height,weight=weight,password=password,image=image)
            user.save()
            return HttpResponse('<script>alert("Registered Successfully"); window.location.href="/login/";</script>')
        return HttpResponse('Password and Confirmpassword do not match')
    return render(request,'register.html')

from django.utils import timezone
def login(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        try:
            user=models.Register.objects.get(email=email)
            if user.password==password:
                request.session['email']=email
                user.loggedin_at=timezone.now()
                user.save()
                
                return HttpResponse('<script>alert("Login Successfully"); window.location.href="/home/";</script>')
            return HttpResponse('password does not match')
        except models.Register.DoesNotExist:
           return HttpResponse('email does not exist')  
    return render(request,'login.html')


def home(request):
    if 'email' not in request.session:
        return redirect('login')
    return render(request,'home.html')
    
def logout(request):
     request.session.flush()
     return redirect('index')

def profile(request):
    if 'email' in request.session:
        email=request.session['email']
        try:
            user=models.Register.objects.get(email=email)
            height=user.height/100
            bmi=user.weight/pow(height,2)
            bmi=round(bmi,2)
            fitnessgoal=user.fitnessgoal
            return render(request,'profile.html',{'user':user,'bmi':bmi, 'f':fitnessgoal})
        except models.Register.DoesNotExist:
            return HttpResponse('user not found')
    return HttpResponse('email not found')

def editprofile(request):
    if 'email' in request.session:
        email=request.session['email']
        user=models.Register.objects.get(email=email)
        if request.method=='POST':
            user.name=request.POST.get('name')
            user.age=request.POST.get('age')
            user.gender=request.POST.get('gender')
            user.email=request.POST.get('email')
            user.height=request.POST.get('height')
            user.weight=request.POST.get('weight')
            user.fitnessgoal=request.POST.get('fitnessgoal')
            if 'image' in request.FILES:
                user.image=request.FILES.get('image')
            user.password=request.POST.get('password')
            user.save()
            return redirect('profile')
        return render(request,'editprofile.html',{'user':user})
    return redirect('login')

def adminlogin(request):
    if request.method=='POST':
        username=request.POST.get('username')
        password=request.POST.get('password')
        if username=='admin' and password=='admin':
            return redirect('adminhome')
        return HttpResponse('<script>alert("Invalid Username or Password"); window.history.back();</script>')
    return render(request,'adminlogin.html')

from django.db.models import Sum
from django.utils import timezone

def adminhome(request):
    users = models.Register.objects.all()
    feedbacks = models.Feedback.objects.all()
    users_today = models.Register.objects.filter(loggedin_at__date=timezone.localdate())
    revenue = models.SubscriptionOrder.objects.filter(payment_status='success').aggregate(total=Sum('amount'))['total'] or 0
    return render(request,'adminhome.html',{'users': users,'feedbacks': feedbacks,'users_today': users_today,'revenue': revenue,})


def userlist(request):
    users=models.Register.objects.all()
    return render(request,'userlist.html',{'users':users})

def deleteuser(request,id):
    users=models.Register.objects.get(id=id)
    users.delete()
    return redirect('userlist')
    
def workouttips(request):
    if request.method=='POST':
        workout=request.POST.get('workout')
        duration=request.POST.get('duration')
        description=request.POST.get('description')
        image=request.FILES.get('image')
        work=models.Workouttips(workout=workout,duration=duration,description=description,image=image)
        work.save()
        return redirect('adminhome')
    return render(request,'workouttips.html')


def workouttipslist(request):
    work=models.Workouttips.objects.all()
    return render(request,'workouttipslist.html',{'work':work})

def deletework(request,id):
    works=models.Workouttips.objects.get(id=id)
    works.delete()
    return redirect('workouttipslist')

def editworkouttips(request,id):
        work=models.Workouttips.objects.get(id=id)
        if request.method=='POST':
            work.workout=request.POST.get('workout')
            work.description=request.POST.get('description')
            if 'image' in request.FILES:
                work.image=request.FILES.get('image')
            work.duration=request.POST.get('duration')
            work.save()
            return redirect('workouttipslist')
        return render(request,'editworkouttips.html',{'work':work})

def workouttips_user(request):
    work=models.Workouttips.objects.all()
    return render(request,'workouttips_user.html',{'work':work})
 

def add_feedback(request):
    if request.method == 'POST':
        website_rating = request.POST.get('website_rating')
        workout_rating = request.POST.get('workout_rating')
        comment = request.POST.get('comment')

        email = request.session.get('email')

        fb = models.Feedback(
            website_rating=website_rating,
            workout_rating=workout_rating,
            comment=comment,
            email=email
        )
        fb.save()

        return redirect('user_feedback_list')  

    return render(request, 'feedback.html')



#manage feedback at user dashboard

def user_feedback_list(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')  
    feedbacks = models.Feedback.objects.filter(email=email).order_by('-created_at')

    return render(request, 'user_feedback_list.html', {'feedbacks': feedbacks,'email': email})

#delete feedback at user side

def user_feedback_delete(request, id):
    fb =models.Feedback.objects.get(id=id)
    fb.delete()
    return redirect('user_feedback_list')



#edit user feedback at user side

def user_feedback_edit(request, id):
    if 'email' in request.session:
        feedback = models.Feedback.objects.get(id=id)

        if request.method == 'POST':
            feedback.website_rating = request.POST.get('website_rating')
            feedback.workout_rating = request.POST.get('workout_rating')
            feedback.comment = request.POST.get('comment', '') 

            feedback.save()
            return redirect('user_feedback_list')  
        return render(request, 'user_feedback_edit.html', {'feedback': feedback})
    return redirect('login')




def feedback_list(request):
    work=models.Feedback.objects.all()
    return render(request,'feedbacklist.html',{'work':work})
    
def deletefeedback(request, id):
    fb =models.Feedback.objects.get(id=id)
    fb.delete()
    return redirect('feedback_list')




import json
import requests
from django.conf import settings
from django.shortcuts import render, redirect
from . import models


def Healthcondition(request):
    if 'email' not in request.session:
        return redirect('login')

    email = request.session['email']
    user = models.Register.objects.get(email=email)

    if request.method == "POST":

        age = request.POST.get("age")
        gender = request.POST.get("gender")
        weight = request.POST.get("weight")
        height = request.POST.get("height")
        fitness_goal = request.POST.get("fitnessgoal")
        notes = request.POST.get("ai_notes")
        fat = request.POST.get("fat")
        chol = request.POST.get("cholesterol")
        sugar = request.POST.get("sugar")
        injuries = request.POST.get("injuries")

        try:
            api_key = settings.GROQ_API_KEY2
            api_url = settings.GROQ_API_URL2
            model = settings.GROQ_MODEL2

            system_message = {
                "role": "system",
                "content": """
You are a professional AI dietitian and certified fitness trainer.

Return STRICT JSON in this EXACT structure:

{
  "ai_suggestions": "string",
  "risks": "string",
  "workout_plan": "string",
  "lifestyle": "string",
  "diet_plan": [
    {
      "day": "Day 1",
      "meals": [
        {"time":"Breakfast","meal":"full detailed meal"},
        {"time":"Lunch","meal":"full detailed meal"},
        {"time":"Snack","meal":"full detailed meal"},
        {"time":"Dinner","meal":"full detailed meal"}
      ]
    }
  ],
  "summary": "string"
}

Rules:
- Must generate FULL 7 days.
- Each meal must include calories, protein, and weight.
- Use Kerala foods.
- No empty strings allowed.
- Do not leave any field blank.
- Do not include explanations.
- JSON only.

Workout Plan Requirements:
- Create a FULL 7-DAY structured home workout plan.
- Clearly label Day 1 to Day 7.
- Specify exact exercises each day.
- Mention sets, reps, and rest time for EACH exercise.
- Include warm-up (5–7 min).
- Include cool-down/stretching (5 min).
- Split structure example:
    Day 1 – Upper Body
    Day 2 – Lower Body
    Day 3 – Core + Cardio
    Day 4 – Active Recovery
    Day 5 – Upper Body
    Day 6 – Lower Body + HIIT
    Day 7 – Mobility + Core
- Include progressive overload guidance for week 2.
- Make exercises practical for home (no gym equipment).
- Make it detailed and professional.
"""
            }

            user_message = {
                "role": "user",
                "content": f"""
User Details:
Age: {age}
Gender: {gender}
Weight: {weight}
Height: {height}
Goal: {fitness_goal}
Body Fat: {fat}
Cholesterol: {chol}
Sugar: {sugar}
Injuries: {injuries}
Notes: {notes}
"""
            }

            payload = {
                "model": model,
                "messages": [system_message, user_message],
                "temperature": 0.2,
                "max_tokens": 3800,
                "response_format": {"type": "json_object"}
            }

            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }

            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=90
            )

            print("STATUS:", response.status_code)
            print("RAW:", response.text)

            response.raise_for_status()
            response_json = response.json()

            if "error" in response_json:
                raise Exception(response_json["error"]["message"])

            content = response_json["choices"][0]["message"]["content"].strip()
            ai_data = json.loads(content)

            if not ai_data.get("diet_plan"):
                raise Exception("Diet plan empty")

        except Exception as e:
            print("🔥 AI ERROR:", str(e))

            ai_data = {
                "ai_suggestions": "Maintain balanced nutrition and regular exercise.",
                "risks": "Consult doctor for abnormal readings.",
                "workout_plan": "30 minutes walking daily.",
                "lifestyle": "Sleep well, hydrate, manage stress.",
                "diet_plan": [],
                "summary": "Fallback due to AI error."
            }

        health = models.Health_condition(
            user=user,
            age=age,
            gender=gender,
            current_weight=weight,
            current_height=height,
            fitness_goal=fitness_goal,
            current_fat=fat,
            current_cholestrole=chol,
            current_suger=sugar,
            ai_suggestions=json.dumps(ai_data),
            injuries=injuries,
        )
        health.save()

        return redirect("health_result", pk=health.id)

    return render(request, "Health_condition.html", {"user": user})


def health_result(request, pk):
    record = models.Health_condition.objects.get(id=pk)
    ai_report = json.loads(record.ai_suggestions)

    return render(request, "health_result.html", {
        "record": record,
        "ai": ai_report
    })



from django.shortcuts import render, redirect
from django.contrib.auth.models import User


def subscriptionplan(request):
    if request.method=='POST':
        duration=request.POST.get('duration')
        fees=request.POST.get('fees')
        description=request.POST.get('description')
        package_name=request.POST.get('package_name')
        type=request.POST.get('type')
        image=request.FILES.get('image')
        user=models.Subscriptionplan(duration=duration,fees=fees,description=description,package_name=package_name,type=type,image=image)
        user.save()
        return HttpResponse('<script>alert("Added Successfully"); window.location.href="/adminhome/";</script>')
    return render(request,'subscriptionplan.html')

from django.utils import timezone

def usersubscription(request):
    plans = models.Subscriptionplan.objects.all()
    user = None
    active_trial = None
    expired_trial_order = None

    if 'email' in request.session:
        user = models.Register.objects.get(email=request.session['email'])

        # 🔴 Auto-expire trial / subscription
        expire_subscription(user)

        # 🟢 ACTIVE TRIAL (for countdown banner)
        active_trial = models.SubscriptionOrder.objects.filter(
            user=user,
            is_trial=True,
            is_active=True,
            end_date__gt=timezone.now()
        ).first()

        # 🔴 EXPIRED TRIAL (for Pay Now banner)
        expired_trial_order = models.SubscriptionOrder.objects.filter(
            user=user,
            is_trial=True,
            payment_status='trial_expired'
        ).first()

    return render(request, 'usersubscription.html', {
        'work': plans,
        'user': user,
        'active_trial': active_trial,          # ✅ REQUIRED FOR COUNTDOWN
        'expired_trial_order': expired_trial_order
    })


def adminsubscription(request):
    work=models.Subscriptionplan.objects.all()
    return render(request,'adminsubscription.html',{'work':work})
 
def deletesubscription(request,id):
    users=models.Subscriptionplan.objects.get(id=id)
    users.delete()
    return redirect('adminsubscription')

def editsubscription(request,id):
        work=models.Subscriptionplan.objects.get(id=id)
        if request.method=='POST':
            work.fees=request.POST.get('fees')
            work.description=request.POST.get('description')
            if 'image' in request.FILES:
                work.image=request.FILES.get('image')
            work.duration=request.POST.get('duration')
            work.package_name=request.POST.get('package_name')
            work.edit=request.POST.get('edit')
            work.save()
            return redirect('adminsubscription')
        return render(request,'editsubscription.html',{'work':work})

from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import timedelta
from .models import Register, Subscriptionplan, SubscriptionOrder
from .utils import expire_subscription


def subscription_buynow(request, id):
    if 'email' not in request.session:
        return redirect('login')

    user = Register.objects.get(email=request.session['email'])

    # Expire old subscriptions first
    expire_subscription(user)

    plan = Subscriptionplan.objects.get(id=id)

    # Block ONLY active paid subscriptions
    active_paid = SubscriptionOrder.objects.filter(
        user=user,
        is_active=True,
        is_trial=False
    ).first()

    if active_paid:
        return render(request, 'subscription_blocked.html', {
            'active_plan': active_paid.plan,
            'end_date': active_paid.end_date
        })

    # Check if trial exists
    trial_order = SubscriptionOrder.objects.filter(
        user=user,
        is_trial=True
    ).first()

    # 🟢 If trial still active → show info page
    if trial_order and trial_order.is_active:
        return render(request, 'trial_started.html', {
            'user': user,
            'plan': trial_order.plan,
            'end_date': trial_order.end_date
        })

    # 🔴 If trial expired → create NEW paid order
    if trial_order and not trial_order.is_active:
        paid_order = SubscriptionOrder.objects.create(
            user=user,
            plan=plan,
            amount=plan.fees,
            payment_status='pending',
            is_trial=False,
            is_active=False
        )

        # ✅ PASS ORDER ID (NOT PLAN ID)
        return redirect('subscription_payment_view', id=paid_order.id)

    # 🆕 If no trial used → start free trial
    order = SubscriptionOrder.objects.create(
        user=user,
        plan=plan,
        amount=0,
        payment_status='trial',
        is_trial=True,
        is_active=True,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=7)
    )

    user.subscription_plan = plan
    user.save()

    return render(request, 'trial_started.html', {
        'user': user,
        'plan': plan,
        'end_date': order.end_date
    })



import razorpay
from django.conf import settings
from django.shortcuts import redirect, render
from django.utils import timezone
from .utils import expire_subscription
from . import models


def subscription_payment_view(request, id):
    if 'email' not in request.session:
        return redirect('login')

    user = models.Register.objects.get(email=request.session['email'])

    # Expire old subscription
    expire_subscription(user)

    try:
        order = models.SubscriptionOrder.objects.get(id=id)
    except models.SubscriptionOrder.DoesNotExist:
        return redirect('usersubscription')

    # Block only if trial still active
    if order.is_trial and order.is_active:
        return redirect('usersubscription')

    amount_paise = int(order.plan.fees * 100)

    order.amount = order.plan.fees
    order.payment_status = 'pending'
    order.save()

    client = razorpay.Client(
        auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET)
    )

    razorpay_order = client.order.create({
        'amount': amount_paise,
        'currency': 'INR',
        'payment_capture': 1
    })

    return render(request, 'subscription_razorpay.html', {
        'order': order,
        'api_key': settings.RAZOR_KEY_ID,
        'amount': amount_paise,
        'razorpay_order_id': razorpay_order['id']
    })



def subscription_payment_success(request, id):
    if 'email' not in request.session:
        return redirect('login')

    order = models.SubscriptionOrder.objects.get(
        id=id,
        payment_status='pending'
    )

    # Activate subscription
    order.activate()

    # Save active plan in user
    user = order.user
    user.subscription_plan = order.plan
    user.save()

    return render(request, 'subscription_payment_success.html', {
        'user': user,
        'plan': order.plan,
        'end_date': order.end_date
    })


from django.utils import timezone

def expire_subscription(user):
    active_order = models.SubscriptionOrder.objects.filter(
        user=user,
        is_active=True
    ).first()

    if active_order and active_order.end_date < timezone.now():
        active_order.is_active = False

        # trial finished → waiting for payment
        if active_order.is_trial:
            active_order.payment_status = 'trial_expired'

        active_order.save()

        user.subscription_plan = None
        user.save()





import time
import cv2
import numpy as np
import base64
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.core.files.base import ContentFile
from .models import WorkoutAnalysis
from . import models   # Register model

# -------- GLOBAL STATE ----------
PREV_GRAY = None
CAMERA_START_TIME = None
CAPTURE_DURATION = 15
ANALYSIS_LOCKED = False
CURRENT_ANALYSIS_ID = None
REP_COUNT = 0
MOVEMENT_STATE = "UP"
MOVEMENT_TRACKER = None  # Revolutionary movement tracker
# --------------------------------


def analyze_workout_with_groq(frame):
    success, buffer = cv2.imencode(".jpg", frame)
    if not success:
        return None

    b64 = base64.b64encode(buffer).decode()
    data_uri = f"data:image/jpeg;base64,{b64}"

    prompt = (
        "This is a person performing a physical workout or exercise. "
        "Identify the workout/exercise name. "
        "Check whether the posture is CORRECT or INCORRECT. "
        "Give a confidence score (0-100). "
        "If incorrect, explain what is wrong and how to correct it. "
        "Respond in the following format:\n"
        "Workout: <name>\n"
        "Posture: CORRECT or INCORRECT\n"
        "Confidence: <number>\n"
        "Feedback: <text>"
    )

    payload = {
        "model": settings.GROQ_MODEL2,
        "temperature": 0,
        "max_tokens": 400,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            }
        ],
    }

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY2}",
        "Content-Type": "application/json",
    }

    r = requests.post(
        settings.GROQ_API_URL2,
        json=payload,
        headers=headers,
        timeout=10
    )
    r.raise_for_status()

    return r.json()["choices"][0]["message"]["content"]


def verify_exercise_match(frame, selected_workout, detected_workout):
    """
    Use Groq AI to verify if user is doing the correct exercise.
    Returns: (is_correct, ai_detected_workout, message)
    """
    # If pose detection matches selection, likely correct
    if detected_workout == selected_workout:
        return True, detected_workout, "Exercise matches selection"
    
    # If different, use AI to double-check
    try:
        success, buffer = cv2.imencode(".jpg", frame)
        if not success:
            return True, detected_workout, "Could not verify"

        b64 = base64.b64encode(buffer).decode()
        data_uri = f"data:image/jpeg;base64,{b64}"

        prompt = (
            f"The user selected '{selected_workout}' as their workout. "
            f"Look at this image and identify what exercise they are actually performing. "
            f"Respond with ONLY the exercise name, nothing else. "
            f"Choose from: Bicep Curl, Hammer Curl, Shoulder Press, Lateral Raise, "
            f"Push-up, Tricep Dip, Squat, Lunges, Calf Raise, Plank, Standing Knee Raise, Crunch, or Unknown."
        )

        payload = {
            "model": settings.GROQ_MODEL2,
            "temperature": 0,
            "max_tokens": 50,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": data_uri}},
                    ],
                }
            ],
        }

        headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY2}",
            "Content-Type": "application/json",
        }

        r = requests.post(
            settings.GROQ_API_URL2,
            json=payload,
            headers=headers,
            timeout=10
        )
        r.raise_for_status()

        ai_detected = r.json()["choices"][0]["message"]["content"].strip()
        
        # Check if AI detection matches selection
        if selected_workout.lower() in ai_detected.lower():
            return True, selected_workout, "AI verified correct exercise"
        else:
            return False, ai_detected, f"You selected '{selected_workout}' but appear to be doing '{ai_detected}'"
    
    except Exception as e:
        # If AI fails, trust pose detection
        return True, detected_workout, "AI verification unavailable"


def cleanup_old_workout_images(days=1, dry_run=False):
    """
    Delete workout images older than specified days to save storage.
    
    Args:
        days: Number of days to keep (default 1)
        dry_run: If True, only show what would be deleted without actually deleting
    
    Returns:
        dict with deleted_count and error_count
    """
    from datetime import timedelta
    from django.utils import timezone
    from django.conf import settings
    import os
    
    # Get analyses older than specified days
    cutoff_date = timezone.now() - timedelta(days=days)
    old_analyses = WorkoutAnalysis.objects.filter(analyzed_at__lt=cutoff_date)
    
    deleted_count = 0
    error_count = 0
    
    for analysis in old_analyses:
        if analysis.image:
            try:
                # Get the full file path
                image_path = analysis.image.path
                
                if dry_run:
                    print(f"Would delete: {image_path}")
                    if os.path.isfile(image_path):
                        deleted_count += 1
                else:
                    # Delete the physical file
                    if os.path.isfile(image_path):
                        os.remove(image_path)
                        deleted_count += 1
                        print(f"Deleted: {image_path}")
                    
                    # Clear the image field but keep the analysis record
                    analysis.image = None
                    analysis.save()
            except Exception as e:
                error_count += 1
                print(f"Error deleting {analysis.id}: {str(e)}")
    
    # Also clean up orphaned files (files not in database)
    try:
        workouts_dir = os.path.join(settings.MEDIA_ROOT, 'workouts')
        if os.path.exists(workouts_dir):
            all_files = set(os.listdir(workouts_dir))
            
            # Get all image filenames from database
            db_images = set()
            for analysis in WorkoutAnalysis.objects.exclude(image='').exclude(image=None):
                if analysis.image:
                    db_images.add(os.path.basename(analysis.image.name))
            
            # Find orphaned files
            orphaned_files = all_files - db_images
            
            for filename in orphaned_files:
                if filename.startswith('workout_') and filename.endswith('.jpg'):
                    file_path = os.path.join(workouts_dir, filename)
                    
                    # Check file age
                    file_time = os.path.getmtime(file_path)
                    file_age = timezone.now().timestamp() - file_time
                    
                    if file_age > (days * 24 * 3600):  # Convert days to seconds
                        if dry_run:
                            print(f"Would delete orphaned: {file_path}")
                            deleted_count += 1
                        else:
                            try:
                                os.remove(file_path)
                                deleted_count += 1
                                print(f"Deleted orphaned: {file_path}")
                            except Exception as e:
                                error_count += 1
                                print(f"Error deleting orphaned {filename}: {str(e)}")
    except Exception as e:
        print(f"Error cleaning orphaned files: {str(e)}")
    
    return {"deleted": deleted_count, "errors": error_count}


def camera_view(request):
    global CAMERA_START_TIME, CURRENT_ANALYSIS_ID, REP_COUNT, MOVEMENT_STATE, MOVEMENT_TRACKER

    # Define workout configurations
    WORKOUT_PLAN = {
        "Bicep Curl": {"type": "reps", "sets": 3, "reps": 12, "rest": 30},
        "Hammer Curl": {"type": "reps", "sets": 3, "reps": 12, "rest": 30},
        "Shoulder Press": {"type": "reps", "sets": 3, "reps": 10, "rest": 30},
        "Lateral Raise": {"type": "reps", "sets": 3, "reps": 12, "rest": 30},
        "Push-up": {"type": "reps", "sets": 3, "reps": 12, "rest": 30},
        "Tricep Dip": {"type": "reps", "sets": 3, "reps": 10, "rest": 30},
        "Squat": {"type": "reps", "sets": 3, "reps": 15, "rest": 40},
        "Lunges": {"type": "reps", "sets": 3, "reps": 10, "rest": 40},
        "Calf Raise": {"type": "reps", "sets": 3, "reps": 20, "rest": 25},
        "Plank": {"type": "time", "sets": 3, "duration": 30, "rest": 30},
        "Standing Knee Raise": {"type": "reps", "sets": 3, "reps": 15, "rest": 30},
        "Crunch": {"type": "reps", "sets": 3, "reps": 15, "rest": 30},
    }

    session = request.session
    
    user = None
    if "email" in session:
        user = models.Register.objects.get(email=session["email"])
    
    # GET request - show workout selection page or handle stop action
    if request.method == "GET":
        # Check if this is a stop action
        if request.GET.get("action") == "stop":
            # Get current analysis ID before clearing
            analysis_id = CURRENT_ANALYSIS_ID
            
            # Save the best frame if available
            if analysis_id:
                try:
                    analysis = WorkoutAnalysis.objects.get(id=analysis_id)
                    best_frame_b64 = session.get("best_frame")
                    if best_frame_b64:
                        frame_data = base64.b64decode(best_frame_b64)
                        analysis.image.save(
                            f"workout_{user.id if user else 'guest'}_{int(time.time())}.jpg",
                            ContentFile(frame_data),
                            save=True
                        )
                except:
                    pass
            
            # Clear workout session data
            session.pop("current_set", None)
            session.pop("rep_in_set", None)
            session.pop("total_reps", None)
            session.pop("resting", None)
            session.pop("rest_start", None)
            session.pop("rest_duration", None)
            session.pop("posture_good", None)
            session.pop("posture_bad", None)
            session.pop("bad_frames", None)
            session.pop("selected_workout", None)
            session.pop("set_start_time", None)
            session.pop("custom_config", None)
            session.pop("best_frame", None)
            
            # Reset global state
            CAMERA_START_TIME = None
            CURRENT_ANALYSIS_ID = None
            MOVEMENT_STATE = "DOWN"
            
            return JsonResponse({"status": "stopped", "analysis_id": analysis_id})
        
        # Clear any previous workout session data when page loads
        session.pop("current_set", None)
        session.pop("rep_in_set", None)
        session.pop("total_reps", None)
        session.pop("resting", None)
        session.pop("rest_start", None)
        session.pop("rest_duration", None)
        session.pop("posture_good", None)
        session.pop("posture_bad", None)
        session.pop("bad_frames", None)
        session.pop("selected_workout", None)
        session.pop("set_start_time", None)
        session.pop("custom_config", None)
        
        # Reset global state
        CAMERA_START_TIME = None
        CURRENT_ANALYSIS_ID = None
        MOVEMENT_STATE = "DOWN"
        
        return render(request, "workout_camera.html", {
            "workouts": WORKOUT_PLAN
        })

    # POST request - handle video frame analysis
    if request.method == "POST":
        image_data = request.POST.get("image")
        selected_workout = request.POST.get("workout")
        config_json = request.POST.get("config")

        # Reset session when camera starts (new workout)
        if CAMERA_START_TIME is None:
            CAMERA_START_TIME = time.time()
            MOVEMENT_STATE = "DOWN"
            
            # Initialize Revolutionary Movement Tracker
            MOVEMENT_TRACKER = MovementTracker(
                exercise_name=selected_workout or "Unknown Exercise",
                buffer_size=30
            )
            
            # Parse custom config
            if config_json:
                try:
                    custom_config = json.loads(config_json)
                    session["custom_config"] = custom_config
                except:
                    session["custom_config"] = {}
            else:
                session["custom_config"] = {}
            
            # Clear previous workout session data
            session["current_set"] = 1
            session["rep_in_set"] = 0
            session["total_reps"] = 0
            session["resting"] = False
            session["rest_start"] = 0
            session["rest_duration"] = 0
            session["posture_good"] = 0
            session["posture_bad"] = 0
            session["bad_frames"] = 0
            session["selected_workout"] = selected_workout or "Unknown Exercise"
            session["set_start_time"] = time.time()
            session["best_frame"] = None  # Will store the best frame
            session["movement_state"] = "UP"  # Track movement for rep counting
            session["frame_count"] = 0  # Track frames for AI verification
            session["mismatch_count"] = 0  # Track exercise mismatches
            session["exercise_warning_shown"] = False  # Track if warning shown

            analysis = WorkoutAnalysis.objects.create(
                user=user,
                workout_name=session["selected_workout"],
                posture_status="CORRECT",
                confidence_score=0,
                ai_feedback="Workout started",
                rep_count=0,
                duration_seconds=0
            )
            CURRENT_ANALYSIS_ID = analysis.id

        _, data = image_data.split(",", 1)
        frame = cv2.imdecode(
            np.frombuffer(base64.b64decode(data), np.uint8),
            cv2.IMREAD_COLOR
        )

        landmarks = get_pose_landmarks(frame)

        selected_workout = session.get("selected_workout", "Unknown Exercise")
        custom_config = session.get("custom_config", {})
        
        # Use custom config if available, otherwise use default plan
        plan = WORKOUT_PLAN.get(selected_workout, {}).copy()
        if custom_config:
            plan.update(custom_config)
        
        workout_type = plan.get("type", "reps")

        # -------- REST MODE --------
        if session.get("resting", False):
            elapsed = time.time() - session.get("rest_start", time.time())
            remaining = max(0, int(session.get("rest_duration", 0) - elapsed))

            if remaining == 0:
                session["resting"] = False
                session["rep_in_set"] = 0
                session["current_set"] = session.get("current_set", 1) + 1
                session["set_start_time"] = time.time()
            else:
                return JsonResponse({
                    "stop": False,
                    "status": "REST",
                    "set": session.get("current_set", 1),
                    "reps": session.get("rep_in_set", 0),
                    "rest_seconds": remaining,
                    "workout_name": selected_workout,
                    "workout_type": workout_type,
                    "posture_status": "CORRECT",
                    "posture_feedback": "Recover and breathe"
                })

        # -------- ACTIVE MODE --------
        if landmarks:
            # Verify detected exercise matches selected workout
            detected_exercise = identify_exercise(landmarks)
            
            # Periodic AI verification (every 20 frames = ~4 seconds to save API calls)
            frame_count = session.get("frame_count", 0) + 1
            session["frame_count"] = frame_count
            
            exercise_mismatch = False
            mismatch_message = ""
            
            # Check if detected exercise differs from selected
            if detected_exercise != selected_workout and detected_exercise != "Unknown Exercise":
                # Count mismatches
                mismatch_count = session.get("mismatch_count", 0) + 1
                session["mismatch_count"] = mismatch_count
                
                # Show immediate warning after 5 consecutive mismatches
                if mismatch_count >= 5:
                    exercise_mismatch = True
                    mismatch_message = f"⚠️ Wrong exercise! You selected '{selected_workout}' but detected '{detected_exercise}'"
                    
                    # Verify with AI after 10 frames for more accurate message
                    if mismatch_count >= 10 and frame_count % 20 == 0:
                        is_correct, ai_detected, message = verify_exercise_match(
                            frame, selected_workout, detected_exercise
                        )
                        
                        if not is_correct:
                            mismatch_message = f"⚠️ {message}"
                            session["exercise_warning_shown"] = True
            else:
                # Reset mismatch counter if exercise matches
                session["mismatch_count"] = 0
            
            # Use selected workout for analysis (more accurate)
            posture_status, posture_feedback = check_posture(landmarks, selected_workout)
            
            # Override feedback if wrong exercise detected
            if exercise_mismatch:
                posture_status = "INCORRECT"
                posture_feedback = mismatch_message

            # ========== REVOLUTIONARY MOVEMENT TRACKING ==========
            # Add frame to movement tracker for advanced analysis (quality metrics only)
            if MOVEMENT_TRACKER:
                # Convert landmarks dict to list format for tracker
                landmarks_list = [landmarks.get(i) for i in range(33)]
                MOVEMENT_TRACKER.add_frame(landmarks_list, time.time())
                
                # Get real-time feedback from tracker (for quality metrics only)
                tracker_feedback = MOVEMENT_TRACKER.get_real_time_feedback()
                
                # DON'T use tracker's rep count - use manual angle-based counting instead
                # The tracker is for quality analysis only
                
                # Use tracker feedback ONLY if posture is already correct
            if posture_status == "CORRECT":

             if tracker_feedback.get("quality") == "POOR":
              posture_status = "INCORRECT"
              posture_feedback = tracker_feedback.get("feedback", "Slow down and control movement")

             elif tracker_feedback.get("quality") == "FAIR":
                posture_feedback = tracker_feedback.get("feedback", "Control your movement")

    # If GOOD → keep original posture feedback
            # =====================================================

            # Track posture quality
            if posture_status == "INCORRECT":
                session["bad_frames"] = session.get("bad_frames", 0) + 1
                session["posture_bad"] = session.get("posture_bad", 0) + 1
            else:
                session["bad_frames"] = 0
                session["posture_good"] = session.get("posture_good", 0) + 1

            live_status = posture_status
            live_feedback = posture_feedback

            # Update analysis record
            try:
                analysis = WorkoutAnalysis.objects.get(id=CURRENT_ANALYSIS_ID)
            except WorkoutAnalysis.DoesNotExist:
                # Analysis was deleted or doesn't exist, return error
                return JsonResponse({
                    "stop": True,
                    "error": "Workout session expired. Please start a new workout."
                })
            
            analysis.workout_name = selected_workout

            # Handle rep counting for rep-based workouts (MANUAL ANGLE-BASED)
            if workout_type == "reps":
                # Get current movement state from session
                current_movement = session.get("movement_state", "DOWN")
                
                # Use appropriate angle based on exercise type
                if selected_workout in ["Bicep Curl", "Hammer Curl", "Shoulder Press", "Push-up", "Tricep Dip", "Crunch"]:
                    
                    # Arm/upper body exercises - use elbow angle
                    shoulder = landmarks[12]
                    elbow = landmarks[14]
                    wrist = landmarks[16]
                    angle = calculate_angle(shoulder, elbow, wrist)
                    
                    # DOWN position (extended) - starting position
                    if angle > 160 and current_movement == "UP":
                        session["movement_state"] = "DOWN"
                    # UP position (contracted) - count rep when completing the movement
                    elif angle < 90 and current_movement == "DOWN":
                        session["movement_state"] = "UP"
                        session["rep_in_set"] = session.get("rep_in_set", 0) + 1
                        session["total_reps"] = session.get("total_reps", 0) + 1
                elif selected_workout == "Lateral Raise":
                    hip = landmarks[24]
                    shoulder = landmarks[12]
                    elbow = landmarks[14]
                    current_movement = session.get("movement_state", "DOWN")

    # Arm height difference (positive when lifting)
                    angle = calculate_angle(hip, shoulder, elbow)
                    UP_THRESHOLD = 60
                    DOWN_THRESHOLD = 30
    # DOWN position (arms below shoulder)
                    if angle < DOWN_THRESHOLD:
                       session["movement_state"] = "DOWN"

    # UP position (arms lifted to shoulder level)
                    elif angle > UP_THRESHOLD and current_movement == "DOWN":
                       session["movement_state"] = "UP"
                       session["rep_in_set"] = session.get("rep_in_set", 0) + 1
                       session["total_reps"] = session.get("total_reps", 0) + 1
                elif selected_workout in ["Squat", "Lunges", "Calf Raise", "Standing Knee Raise"]:
                    # Leg exercises - use knee angle
                    hip = landmarks[24]
                    knee = landmarks[26]
                    ankle = landmarks[28]
                    angle = calculate_angle(hip, knee, ankle)
                    
                    # UP position (standing) - starting position
                    if angle > 160 and current_movement == "DOWN":
                        session["movement_state"] = "UP"
                    # DOWN position (bent) - count rep when completing the movement
                    elif angle < 110 and current_movement == "UP":
                        session["movement_state"] = "DOWN"
                        session["rep_in_set"] = session.get("rep_in_set", 0) + 1
                        session["total_reps"] = session.get("total_reps", 0) + 1

                analysis.rep_count = session.get("total_reps", 0)
            
            # Handle time-based workouts (like Plank)
            elif workout_type == "time":
                set_elapsed = int(time.time() - session.get("set_start_time", time.time()))
                analysis.duration_seconds = set_elapsed
            
            # Store current frame temporarily (only save to disk at the end)
            # Save frame in session as base64 to avoid multiple disk writes
            if live_status == "CORRECT":
                # Only keep frames with good posture
                success, buffer = cv2.imencode(".jpg", frame)
                if success:
                    session["best_frame"] = base64.b64encode(buffer.tobytes()).decode('utf-8')
            
            # Calculate confidence
            total_frames = session.get("posture_good", 0) + session.get("posture_bad", 0)
            if total_frames > 0:
                confidence = int((session.get("posture_good", 0) / total_frames) * 100)
                analysis.confidence_score = confidence
                analysis.posture_status = "CORRECT" if confidence >= 70 else "INCORRECT"
                
                if confidence < 70:
                    analysis.ai_feedback = posture_feedback
                else:
                    analysis.ai_feedback = "Excellent form maintained throughout the workout"
            
            analysis.save()

            # Check if set is complete
            set_complete = False
            if workout_type == "reps" and plan:
                target_reps = plan.get("reps", 12)
                current_reps = session.get("rep_in_set", 0)
                # Only complete if we actually did the required reps (must be > 0)
                if current_reps > 0 and current_reps >= target_reps:
                    set_complete = True
            elif workout_type == "time" and plan:
                set_elapsed = int(time.time() - session.get("set_start_time", time.time()))
                if set_elapsed >= plan.get("duration", 30):
                    set_complete = True

            if set_complete:
                if session.get("current_set", 1) < plan.get("sets", 3):
                    session["resting"] = True
                    session["rest_start"] = time.time()
                    session["rest_duration"] = plan.get("rest", 30)

                    return JsonResponse({
                        "stop": False,
                        "status": "SET_COMPLETE",
                        "message": f"Set {session.get('current_set', 1)} completed!",
                        "set": session.get("current_set", 1),
                        "reps": session.get("rep_in_set", 0),
                        "workout_name": selected_workout,
                        "workout_type": workout_type,
                        "confidence": analysis.confidence_score,
                        "posture_status": live_status,
                        "posture_feedback": live_feedback
                    })

                # -------- WORKOUT COMPLETE --------
                # Get workout summary from MovementTracker
                if MOVEMENT_TRACKER:
                    summary = MOVEMENT_TRACKER.get_workout_summary()
                    analysis.ai_feedback = (
                        f"Workout Grade: {summary.get('grade', 'N/A')} | "
                        f"Avg Quality: {summary.get('avg_quality', 0)}% | "
                        f"Avg ROM: {summary.get('avg_rom', 0)}% | "
                        f"Consistency: {summary.get('form_consistency', 0)}%"
                    )
                
                # Save the best frame before clearing session
                analysis = WorkoutAnalysis.objects.get(id=CURRENT_ANALYSIS_ID)
                analysis_id = analysis.id  # Save ID before clearing
                
                best_frame_b64 = session.get("best_frame")
                if best_frame_b64:
                    try:
                        frame_data = base64.b64decode(best_frame_b64)
                        analysis.image.save(
                            f"workout_{user.id if user else 'guest'}_{int(time.time())}.jpg",
                            ContentFile(frame_data),
                            save=True
                        )
                    except:
                        pass  # If frame save fails, continue anyway
                
                # Clear session data
                session.pop("current_set", None)
                session.pop("rep_in_set", None)
                session.pop("total_reps", None)
                session.pop("resting", None)
                session.pop("rest_start", None)
                session.pop("rest_duration", None)
                session.pop("posture_good", None)
                session.pop("posture_bad", None)
                session.pop("bad_frames", None)
                session.pop("selected_workout", None)
                session.pop("set_start_time", None)
                session.pop("best_frame", None)
                session.pop("custom_config", None)
                session.pop("frame_count", None)
                session.pop("mismatch_count", None)
                session.pop("exercise_warning_shown", None)
                session.pop("movement_state", None)
                
                CAMERA_START_TIME = None
                CURRENT_ANALYSIS_ID = None
                MOVEMENT_TRACKER = None  # Reset tracker

                return JsonResponse({
                    "stop": True,
                    "id": analysis_id
                })

            # Return current status
            response_data = {
                "stop": False,
                "set": session.get("current_set", 1),
                "workout_name": selected_workout,
                "workout_type": workout_type,
                "confidence": analysis.confidence_score,
                "posture_status": live_status,
                "posture_feedback": live_feedback,
                "landmarks": landmarks  # Send landmarks for skeleton overlay
            }

            # Add advanced metrics from MovementTracker
            if MOVEMENT_TRACKER:
                tracker_feedback = MOVEMENT_TRACKER.get_real_time_feedback()
                response_data["movement_quality"] = tracker_feedback.get("avg_quality", 0)
                response_data["rom_score"] = tracker_feedback.get("avg_rom", 0)
                response_data["movement_phase"] = tracker_feedback.get("phase", "NEUTRAL")

            if workout_type == "reps":
                response_data["reps"] = session.get("rep_in_set", 0)
            elif workout_type == "time":
                set_elapsed = int(time.time() - session.get("set_start_time", time.time()))
                response_data["duration"] = set_elapsed
                response_data["target_duration"] = plan.get("duration", 30)

            return JsonResponse(response_data)
        else:
            # No landmarks detected
            selected_workout = session.get("selected_workout", "Unknown")
            custom_config = session.get("custom_config", {})
            plan = WORKOUT_PLAN.get(selected_workout, {}).copy()
            if custom_config:
                plan.update(custom_config)
            workout_type = plan.get("type", "reps")
            
            response_data = {
                "stop": False,
                "set": session.get("current_set", 1),
                "workout_name": selected_workout,
                "workout_type": workout_type,
                "confidence": 0,
                "posture_status": "INCORRECT",
                "posture_feedback": "Position yourself in camera view"
            }
            
            if workout_type == "reps":
                response_data["reps"] = session.get("rep_in_set", 0)
            elif workout_type == "time":
                response_data["duration"] = 0
                response_data["target_duration"] = plan.get("duration", 30)
            
            return JsonResponse(response_data)

def finish_workout(analysis, session):
    total = session["posture_good"] + session["posture_bad"]
    confidence = int((session["posture_good"] / total) * 100) if total else 80

    analysis.confidence_score = confidence
    analysis.posture_status = "CORRECT" if confidence >= 70 else "INCORRECT"

    if analysis.posture_status == "CORRECT":
        analysis.ai_feedback = "Excellent form maintained throughout the workout."
    else:
        analysis.ai_feedback = "Posture issues detected. Review feedback to improve form."

    if session.get("last_frame") is not None:
        success, buffer = cv2.imencode(".jpg", session["last_frame"])
        if success:
            analysis.image.save(
                f"workout_{int(time.time())}.jpg",
                ContentFile(buffer.tobytes()),
                save=False
            )

    analysis.save()
    session.clear()

    return JsonResponse({"stop": True, "id": analysis.id})







def workout_result(request, id):
    analysis = WorkoutAnalysis.objects.get(id=id)
    return render(request, "workout_result.html", {"analysis": analysis})



from django.shortcuts import render, redirect
from .models import WorkoutAnalysis, Register

def workout_report_list(request):
    # 🔐 Check login
    if 'email' not in request.session:
        return redirect('login')  # change if your login url name is different

    email = request.session['email']

    try:
        user = Register.objects.get(email=email)
    except Register.DoesNotExist:
        return redirect('login')

    # ✅ ONLY THIS USER'S REPORTS
    reports = WorkoutAnalysis.objects.filter(user=user).order_by('-analyzed_at')

    return render(
        request,
        "workout_report_list.html",
        {
            "user": user,
            "reports": reports
        }
    )

