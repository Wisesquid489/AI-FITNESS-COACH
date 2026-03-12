from django.db import models

# Create your models here.
   
class Subscriptionplan(models.Model):
    duration = models.IntegerField(help_text="Duration in days",blank=True,null=True)
    fees=models.IntegerField(blank=True,null=True)
    description=models.CharField(max_length=200,blank=True,null=True)
    package_name=models.CharField(max_length=20,null=True,blank=True)
    Type= [
        ('beginner','Beginner'),
        ('intermediate','Intermediate'),
        ('expert','Expert'),
    ]
    type=models.CharField(max_length=50,choices=Type)
    image=models.ImageField(upload_to='img/',blank=True,null=True)

class Register(models.Model):
    name=models.CharField(max_length=100,null=True,blank=True)
    email=models.EmailField(null=True,blank=True,unique=True)
    age=models.IntegerField(null=True,blank=True)
    gender=models.CharField(max_length=10,null=True,blank=True)
    height=models.IntegerField(null=True,blank=True)
    weight=models.IntegerField(null=True,blank=True)
    image=models.FileField(upload_to="profile_image/",null=True,blank=True)
    password=models.CharField(max_length=30,null=True,blank=True)
    

    FITNESS_CHOICES=[
        ('musclebuilding','musclebuilding'),
        ('weightloss','weightloss'),
        ('weightgain','weightgain'),
        ('bodybuilding','bodybuilding'),
        ('fitness','fitness'),
    ]
    fitnessgoal=models.CharField(max_length=30,null=True,blank=True,choices=FITNESS_CHOICES)
    loggedin_at=models.DateTimeField(auto_now_add=True,null=True)
    subscription_plan = models.ForeignKey(
        Subscriptionplan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )


class Workouttips(models.Model):
    workout=models.CharField(max_length=100,null=True,blank=True)
    image=models.FileField(upload_to="profile_image/",null=True,blank=True)
    description =models.CharField(max_length=100, null=True, blank=True)
    duration = models.CharField(max_length=100,null=True,blank=True)
    

from django.db import models

class Feedback(models.Model):
    website_rating = models.PositiveSmallIntegerField()
    workout_rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Health_condition(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='health_name', null=True, blank=True)
    age=models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10,null=True)
    current_weight = models.CharField(max_length=300,null=True, blank=True)
    current_height = models.CharField(max_length=300,null=True, blank=True)
    fitness_goal = models.CharField(max_length=100, null=True, blank=True)
    current_fat = models.CharField(max_length=300,null=True, blank=True)
    current_cholestrole = models.CharField(max_length=300,null=True, blank=True)
    current_suger = models.CharField(max_length=300,null=True, blank=True)
    ai_suggestions = models.TextField(max_length=100,null=True, blank=True)
    injuries = models.CharField(max_length=100, null=True, blank=True)


 
# models.py

# class SubscriptionOrder(models.Model):
#     user = models.ForeignKey(Register, on_delete=models.CASCADE)
#     plan = models.ForeignKey(Subscriptionplan, on_delete=models.CASCADE)
#     amount = models.FloatField()
#     payment_status = models.CharField(max_length=20, default='pending')
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.name} - {self.plan.name} - {self.payment_status}"


from django.db import models
from django.utils import timezone
from datetime import timedelta

class SubscriptionOrder(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    plan = models.ForeignKey(Subscriptionplan, on_delete=models.CASCADE)

    amount = models.FloatField(default=0)
    payment_status = models.CharField(max_length=20, default='pending')

    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    is_active = models.BooleanField(default=False)
    is_trial = models.BooleanField(default=False)   # ✅ NEW
    def __str__(self):
        return self.user.name
    # ✅ PAID SUBSCRIPTION
    def activate(self):
        self.start_date = timezone.now()
        self.end_date = self.start_date + timedelta(days=self.plan.duration)

        self.is_active = True
        self.is_trial = False
        self.payment_status = 'success'
        self.save()

    # ✅ FREE TRIAL (7 DAYS)
    def activate_trial(self):
        self.start_date = timezone.now()
        self.end_date = self.start_date + timedelta(days=7)

        self.amount = 0
        self.is_active = True
        self.is_trial = True
        self.payment_status = 'trial'
        self.save()

    # ✅ CHECK EXPIRY
    def is_expired(self):
        return self.end_date and timezone.now() > self.end_date
    
    def activate_trial(self):
        # 🚫 extra protection
        if SubscriptionOrder.objects.filter(user=self.user, is_trial=True).exists():
            raise ValueError("Trial already used")

        self.start_date = timezone.now()
        self.end_date = self.start_date + timedelta(days=7)
        self.amount = 0
        self.is_active = True
        self.is_trial = True
        self.payment_status = 'trial'
        self.save()



class WorkoutAnalysis(models.Model):
    POSTURE_STATUS = [
        ("CORRECT", "Correct"),
        ("INCORRECT", "Incorrect"),
    ]

    user = models.ForeignKey(
        Register,
        on_delete=models.CASCADE,
        related_name="workout_analyses",
        null=True,
        blank=True
    )

    image = models.ImageField(upload_to="workouts/", null=True, blank=True)

    workout_name = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    posture_status = models.CharField(
        max_length=10,
        choices=POSTURE_STATUS,
        null=True,
        blank=True
    )

    confidence_score = models.IntegerField(
        null=True,
        blank=True
    )

    # 🔥 increase length for real feedback
    ai_feedback = models.TextField(
        null=True,
        blank=True
    )

    # 🔁 for rep-based workouts
    rep_count = models.IntegerField(default=0)

    # ⏱️ NEW: for time-based workouts like plank (seconds)
    duration_seconds = models.IntegerField(
        null=True,
        blank=True
    )

    analyzed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-analyzed_at"]

    def __str__(self):
        return f"{self.user} | {self.workout_name}"

