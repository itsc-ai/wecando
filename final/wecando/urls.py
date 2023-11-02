from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.LandingPage.as_view(), name="landing_page"),
    path("diary/", views.MainPage.as_view(), name="main_page"),

]