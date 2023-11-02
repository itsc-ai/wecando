from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", views.MainPage.as_view(), name="main_page"),
    path("diary/", views.Diary.as_view(), name="diary"),
    path("calendar/", views.Calendar.as_view(), name="calendar"),
    path("diary_detail/", views.diary_detail, name="diary_detail"),
    path("signup/", views.signup, name="signup"),
    path("diary_create/", views.DiaryCreate.as_view(), name="diary_create"),
    path("diary_write/", views.DiaryWrite.as_view(), name="diary_write"),
    path('accounts/', include('allauth.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='wecando/landing.html'), name='login'), # django.contrib.auth의 views를 import해서 따로 views에 입력하지 않고 기능 구현
]