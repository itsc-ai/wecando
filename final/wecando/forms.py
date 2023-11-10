from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Writen

# 이메일 속성 추가 위해 UserCreationForm 상속
class UserForm(UserCreationForm):
    email = forms.EmailField(label="이메일")
    class Meta:
        model = User
        # 사용자 이름, 비밀번호, 비밀번호 확인, 이메일
        fields = ("username", "password1", "password2", "email")

# 일기 수정
class WriteUpdateForm(forms.ModelForm):
    class Meta:
        model = Writen
        fields = ['writen_title', 'writen_content', 'img_file']

