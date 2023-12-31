from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Writen, AuthUser
from django import forms
from django.core.exceptions import ValidationError
import django.contrib.auth.forms as auth_forms

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

class PasswordResetForm(auth_forms.PasswordResetForm):
    username = auth_forms.UsernameField(label="ID")

    # validation 절차:
    # 1. username에 대응하는 User 인스턴스의 존재성 확인
    # 2. username에 대응하는 email과 입력받은 email이 동일한지 확인

    def clean_username(self):
        # 입력받은 username 데이터 가져오기
        data = self.cleaned_data['username']
        # username에 대응하는 User 인스턴스가 존재하는지 확인
        if not AuthUser.objects.filter(username=data).exists():
            raise ValidationError("해당 ID가 존재하지 않습니다.")

        return data

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        email = cleaned_data.get("email")

        # username과 email이 모두 입력되었을 때
        if username and email:
            # username에 해당하는 User 인스턴스의 이메일과 입력받은 이메일이 일치하는지 확인
            if AuthUser.objects.get(username=username).email != email:
                raise ValidationError("사용자의 이메일 주소가 일치하지 않습니다")

    def get_users(self, email=''):
        # 활성화된 사용자 중에서 username이 일치하고, 비밀번호가 설정되어 있는 경우 반환
        active_users = AuthUser.objects.filter(**{
            'username__iexact': self.cleaned_data["username"],
            'is_active': True,
        })
        return (
            u for u in active_users
            if u.has_usable_password()
        )