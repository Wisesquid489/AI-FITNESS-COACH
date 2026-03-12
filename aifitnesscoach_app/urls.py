from django.urls import path
from . import views

urlpatterns=[
    path('',views.index,name="index"),
    path('register/',views.register,name="register"),
    path('login/',views.login,name="login"),
    path('home/',views.home,name="home"),
    path('profile/',views.profile,name="profile"),
    path('logout/',views.logout,name="logout"),
    path('editprofile/',views.editprofile,name="editprofile"),
    path('adminlogin/',views.adminlogin,name="adminlogin"),
    path('adminhome/',views.adminhome,name="adminhome"),
    path('userlist/',views.userlist,name="userlist"),
    path('deleteuser/<int:id>/',views.deleteuser,name="deleteuser"), 
    path('workouttips/',views.workouttips,name="workouttips"),
    path('workouttipslist/',views.workouttipslist,name="workouttipslist"),
    path('deletework/<int:id>/',views.deletework,name="deletework"), 
    path('editworkouttips/<int:id>/',views.editworkouttips,name="editworkouttips"),
    path('workouttips_user/',views.workouttips_user,name="workouttips_user"),
    path('addfeedback/', views.add_feedback, name='add_feedback'),
    path('feedback_list/', views.feedback_list, name='feedback_list'),
    path('deletefeedback/<int:id>/', views.deletefeedback, name='deletefeedback'),
    path('Health_condition/', views.Healthcondition, name='Health_condition'),
    path('health_result/<int:pk>/', views.health_result, name='health_result'),
    path("subscriptionplan/", views.subscriptionplan, name="subscriptionplan"),
    path("usersubscription/", views.usersubscription, name="usersubscription"),
    path("adminsubscription/", views.adminsubscription, name="adminsubscription"),
    path('deletesubscription/<int:id>/',views.deletesubscription,name="deletesubscription"), 
    path('editsubscription/<int:id>/',views.editsubscription,name="editsubscription"), 
    path('subscription/buynow/<int:id>/', views.subscription_buynow, name='subscription_buynow'),
    path('subscription/payment/<int:id>/', views.subscription_payment_view, name='subscription_payment_view'),
    path('subscription_payment_success/<int:id>/', views.subscription_payment_success,name='subscription_payment_success'),
    path('user_feedback_list/',views.user_feedback_list,name='user_feedback_list'),
    path('user_feedback_delete/<int:id>/',views.user_feedback_delete,name='user_feedback_delete'),
    path('user_feedback_edit/<int:id>/',views.user_feedback_edit,name='user_feedback_edit'),
    
    path("workout_camera/", views.camera_view, name="workout_camera"),
    path("workout_result/<int:id>/", views.workout_result, name="workout_result"),
    path("workout_report_list/", views.workout_report_list, name="workout_report_list"),

    
    
    
]

