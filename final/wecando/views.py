from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from .models import Diary, AuthUser, Writen, Music, Wise, Type
from django.shortcuts import render, redirect, get_object_or_404, reverse
# 회원 가입, 비밀번호 찾을시 필요
from .forms import UserForm, WriteUpdateForm, PasswordResetForm
from django.contrib.auth import authenticate, login, get_user_model
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import BadHeaderError, HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.db.models.query_utils import Q
from django.contrib.auth.views import PasswordResetView

from django.db.models.functions import Cast

from datetime import datetime
from django.core.exceptions import PermissionDenied


# Create your views here.
# landing 페이지 생성
class MainPage(ListView):
    model = Diary
    template_name = "wecando/landing.html"

# 내 모든 다이어리 표지 보기 페이지 생성
class DiaryMain(ListView):
    model = Diary  # 모델을 Review로 설정

    template_name = "wecando/diary.html"  # 템플릿 지정

    # 내가 작성한 리뷰를 불러오기 위해 함수 작성
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        # current_user : 현재 로그인된 사용자를 나타내는 속성
        current_user = self.request.user.id
        user_id = AuthUser.objects.get(id = current_user)

        # 작성자가 현재 로그인된 사용자인 Review의 정보만 담아올 수 있게 함

        diary_list = []
        diary_total = []

        if Diary.objects.filter(id=user_id.id).order_by('-diary_num').count() > 5:

            for i in Diary.objects.filter(id=user_id.id).order_by('-diary_num'):

                diary_list.append(i)

                if len(diary_list) == 5:
                    diary_total.append(diary_list)
                    diary_list = []
            diary_total.append(diary_list)
            context["diary_list"] = diary_total
        else:
            diary_total.append(Diary.objects.filter(id=user_id.id).order_by('-diary_num'))
            context["diary_list"] = diary_total

        print(diary_total)
        # context 값 출력
        return context

# 캘린더 페이지 생성
class Calendar(ListView):
    model = Diary
    template_name = "wecando/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        q = self.kwargs["q"]
        # current_user : 현재 로그인된 사용자를 나타내는 속성
        current_user = self.request.user.id

        context["diary_num"] = q
        today = datetime.today().strftime("%Y-%m-%d")
        context["today"] = today
        today_for_check = Writen.objects.filter(diary_num = q).order_by('-created_at')

        if(today_for_check):
            if (today_for_check[0].created_at.strftime("%Y-%m-%d") == today):
                context["today_check"] = 1
            else:
                context["today_check"] = 0

            context["writen"] = Writen.objects.filter(diary_num = q)
        else:
            context["today_check"] = 0

        # context 값 출력
        return context


#일기 상세 보기
def diary_detail(request, pk):
    write = get_object_or_404(Writen, pk=pk)
    return render(request, "wecando/diary_detail.html", {"write":write})


# 회원 가입 페이지 생성
def signup(request):
    # 입력한 데이터로 사용자를 생성하기 위해 POST 요청
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            # 인증할 때 필요한 사용자 이름과 비밀번호
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            # 사용자 생성 후에 자동 로그인 위해 authenticate(사용자 인증)와 login(로그인)사용
            user = authenticate(username=username, password=raw_password)   # 사용자 인증
            login(request, user)
            return redirect('/')
    else:
        form = UserForm()
    return render(request, 'wecando/signup.html', {'form':form})

# 내 다이어리 꾸미기 페이지 생성
class DiaryCreate(CreateView):
    model = Diary
    fields = ["img_file"]
    template_name = "wecando/diary_create.html"

    def form_valid(self, form):
        print("form_valid start")

        # current_user : 현재 로그인된 사용자를 나타내는 속성
        current_user = self.request.user.id
        user_id = AuthUser.objects.get(id=current_user)

        form.instance.id = user_id

        form.save()
        # 태그와 관련된 작업을 하기 전에 form_valid()의 결괏값을 response에 저장
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        return reverse('diary')

# 일기 작성 페이지 생성
class DiaryWrite(CreateView):
    model = Writen
    fields = ["writen_title", "writen_content", "img_file"]
    template_name = "wecando/diary_form.html"

    def form_valid(self, form):
        print("form_valid start")
        diary_num = (self.kwargs["q"])

        # current_user : 현재 로그인된 사용자를 나타내는 속성
        current_user = self.request.user.id
        user_id = AuthUser.objects.get(id=current_user)

        form.instance.id = user_id

        diary_key = Diary.objects.get(diary_num = diary_num)
        form.instance.diary_num = diary_key

        music_key = Music.objects.get(music_num=1)
        form.instance.music_num = music_key

        wise_key = Wise.objects.get(wise_num=1)
        form.instance.wise_num = wise_key

        type_key = Type.objects.get(type_num=1)
        form.instance.type_num = type_key


        print(form)

        form.save()
        # 태그와 관련된 작업을 하기 전에 form_valid()의 결괏값을 response에 저장
        response = super().form_valid(form)
        return response

    # 성공할 경우 my_review 라는 주소를 가진 페이지로 이동
    def get_success_url(self):
        diary_num = (self.kwargs["q"])

        return reverse('diary_detail', kwargs={"pk":Writen.objects.filter(diary_num = diary_num).order_by("-writen_num")[0].pk})



# 일기 수정
class DiaryUpdate(UpdateView):
    model = Writen
    context_object_name = 'writen'
    fields = ["writen_title", "writen_content", "img_file"]
    template_name = "wecando/diary_update.html"

    def get_object(self):
        writen = get_object_or_404(Writen, pk=self.kwargs['pk'])
        return writen

    def get_success_url(self):
        writen_num = (self.kwargs["pk"])
        return reverse('diary_detail',
                       kwargs={"pk": Writen.objects.get(writen_num=writen_num).pk})

# 일기 삭제
def write_delete(request, pk):
    write = get_object_or_404(Writen, pk=pk)
    write.delete()
    return redirect("/calendar/")


# 비밀번호 찾기
def password_reset_request(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = get_user_model().objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    current_site = get_current_site(request)
                    subject = '비밀번호 재설정'
                    email_template_name = "wecando/password_reset_email.html"
                    c = {
                        "email": user.email,
                        # local: '127.0.0.1:8000', prod: 'givwang.herokuapp.com'
                        'domain': current_site.domain,
                        'site_name': '11:57',
                        # MTE4
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        # Return a token that can be used once to do a password reset for the given user.
                        'token': default_token_generator.make_token(user),
                        # local: http, prod: https
                        # 'protocol': settings.PROTOCOL,
                    }
                    email = render_to_string(email_template_name, c)
                    try:
                        send_mail(subject, email, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    return redirect("/password_reset/done/")
        else:
            return render(request, 'wecando/password_reset_done_fail.html')

    else:
        password_reset_form = PasswordResetForm()
    return render(
        request=request,
        template_name='wecando/password_reset.html',
        context={'password_reset_form': password_reset_form})


# 다이어리 표지 꾸미기
class CoverUpdate(ListView):
    model = Diary
    fields = ["img_file"]
    template_name = "wecando/cover_update.html"