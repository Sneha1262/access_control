from django.urls import path
from . import views

urlpatterns = [
    path("", views.register_doctor, name="home"),
    path("register/", views.register_doctor, name="register_doctor"),
    path("submit-register/", views.submit_register, name="submit_register"),

    path("login/", views.doctor_login, name="doctor_login"),
    # Use the name "dashboard" because redirects/templates often call {% url 'dashboard' %}
    path("dashboard/", views.doctor_dashboard, name="doctor_dashboard"),

    # Request access expects POST body (patient_id); no path parameter here
    path("request-access/", views.request_access, name="request_access"),

    # Token-based patient view
    path("view_patient/<str:token>/", views.view_patient, name="view_patient"),

    path('view_patient/<str:token>/', views.view_patient, name='view_patient')

]
