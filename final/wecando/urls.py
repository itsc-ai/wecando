from django.urls import path,include
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.MainPage.as_view(), name="main_page"),
    path("diary/", views.DiaryMain.as_view(), name="diary"),
    path("calendar/<int:q>/", views.Calendar.as_view(), name="calendar"),
    path("diary_detail/<int:pk>/", views.diary_detail, name="diary_detail"),
    path("signup/", views.signup, name="signup"),
    path("diary_create/", views.DiaryCreate.as_view(), name="diary_create"),
    path("diary_write/<int:q>/", views.DiaryWrite.as_view(), name="diary_write"),
    path('accounts/', include('allauth.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='wecando/landing.html'), name='login'), # django.contrib.auth의 views를 import해서 따로 views에 입력하지 않고 기능 구현
    path("write_delete/<int:pk>/", views.write_delete, name='write_delete'),
    path("diary_delete/<int:pk>/", views.diary_delete, name='diary_delete'),
    path("diary_update/<int:pk>/", views.DiaryUpdate.as_view(), name="diary_update"),
    path('password_reset/', views.password_reset_request, name="password_reset"),
    path("diary_check/<int:pk>/", views.DiaryCheck.as_view(), name="diary_check"),
    path("cover_update/<int:pk>/", views.CoverUpdate.as_view(), name="cover_update"),
    path("test/", views.test, name='test'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)