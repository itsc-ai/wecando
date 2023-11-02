from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

# 이메일 속성 추가 위해 UserCreationForm 상속
class UserForm(UserCreationForm):
    email = forms.EmailField(label="이메일")
    class Meta:
        model = User
        # 사용자 이름, 비밀번호, 비밀번호 확인, 이메일
        fields = ("username", "password1", "password2", "email")