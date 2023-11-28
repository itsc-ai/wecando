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
from django.contrib.auth import authenticate, login
from django.apps import AppConfig
from .apps import WecandoConfig
from django.db.models import TextField
from datetime import datetime
import random
from django.core.exceptions import PermissionDenied
# 모델 돌릴때 필요 (설치해야함)
import tensorflow as tf
import numpy as np
from transformers import TFBertModel, BertTokenizer,DistilBertTokenizer, DistilBertForSequenceClassification
import torch

# Create your views here.
# landing 페이지 생성
class MainPage(ListView):
    model = Diary
    template_name = "wecando/landing.html"


# 내 모든 다이어리 표지 보기 페이지 생성
class DiaryMain(ListView):
    model = Diary  # 모델을 Diary로 설정

    template_name = "wecando/diary.html"  # 템플릿 지정

    # 페이지 구성을 위한 데이터를 구성하는 부분
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        # current_user : 현재 로그인된 사용자를 나타내는 속성
        current_user = self.request.user.id


        try:
            user_id = AuthUser.objects.get(id = current_user)
        except:
            return dict()


        # 한 줄에 5개의 다이어리가 보이도록 다이어리를 5개씩 잘라서 담는 부분
        diary_list = []
        diary_total = []

        # 만들어진 다이어리가 5개 이상이면 5개씩 잘라서 저장
        if Diary.objects.filter(id=user_id.id).order_by('-diary_num').count() > 5:

            for i in Diary.objects.filter(id=user_id.id).order_by('-diary_num'):

                diary_list.append(i)

                if len(diary_list) == 5:
                    diary_total.append(diary_list)
                    diary_list = []
            diary_total.append(diary_list)
            context["diary_list"] = diary_total

        # 5개 이하라면 배열에 담아서 2차원 배열로 저장
        else:
            diary_total.append(Diary.objects.filter(id=user_id.id).order_by('-diary_num'))
            context["diary_list"] = diary_total

        print(diary_total)

        return context

# 캘린더 페이지 생성
class Calendar(ListView):
    model = Diary   # 모델은 Diary로 설정
    template_name = "wecando/calendar.html" # 템플릿 설정

    # 페이지 구성에 필요한 데이터 구성
    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        # 해당 다이어리에 맞는 일기만 불러와야해서 diary_num을 get방식으로 받아옴
        q = self.kwargs["q"]

        # 받아온 diary_num을 저장
        context["diary_num"] = q

        # 오늘 날짜를 저장
        today = datetime.today().strftime("%Y-%m-%d")
        context["today"] = today

        # 캘린더에서 오늘 날짜에 일기가 작성 되어 있는지 확인하여 일기 작성 전이면
        # 일기 작성이라는 버튼을 보여주고 아니면 안보여 주기 위해 확인 하는 부분
        today_for_check = Writen.objects.filter(diary_num = q).order_by('-created_at')

        if(today_for_check):
            if (today_for_check[0].created_at.strftime("%Y-%m-%d") == today):
                context["today_check"] = 1
            else:
                context["today_check"] = 0

            context["writen"] = Writen.objects.filter(diary_num = q)
        else:
            context["today_check"] = 0

        return context


#일기 상세 보기
def diary_detail(request, pk):

    # 해당 일기를 반환
    write = get_object_or_404(Writen, pk=pk)
    return render(request, "wecando/diary_detail.html", {"write":write})


# 회원 가입 페이지 생성
def signup(request):
    # 입력한 데이터로 사용자를 생성하기 위해 POST 요청
    if request.method == "POST":
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()

            # 자동로그인 되지 않도록 수정

            # # 인증할 때 필요한 사용자 이름과 비밀번호
            # username = form.cleaned_data.get('username')
            # raw_password = form.cleaned_data.get('password1')
            # # # 사용자 생성 후에 자동 로그인 위해 authenticate(사용자 인증)와 login(로그인)사용
            # # user = authenticate(username=username, password=raw_password)   # 사용자 인증
            # # login(request, user)
            return redirect('/')
    else:
        form = UserForm()
    return render(request, 'wecando/signup.html', {'form':form})

# 다이어리 생성 페이지 생성
class DiaryCreate(CreateView):
    model = Diary   # 모델은 Diary를 사용
    fields = ["img_file"]   # form 에서 img_file을 받아옴
    template_name = "wecando/diary_create.html" # 템플릿 적용

    # form이 submit 될 때 데이터를 넣어주는 부분
    def form_valid(self, form):
        print("form_valid start")

        # current_user : 현재 로그인된 사용자를 나타내는 속성
        current_user = self.request.user.id
        user_id = AuthUser.objects.get(id=current_user)

        # Diary의 id에 현재 접속중인 유저의 id를 저장
        form.instance.id = user_id

        # 폼을 저장
        form.save()

        response = super().form_valid(form)
        return response

    # 저장에 성공하면 diary 페이지로 이동
    def get_success_url(self):
        return reverse('diary')

# 일기 작성 페이지 생성
class DiaryWrite(CreateView):
    model = Writen  # 모델은 Writen을 사용
    fields = ["writen_title", "writen_content", "img_file"] # 폼에서 writen_title, writen_content, img_file을 받아옴
    template_name = "wecando/diary_form.html"   # 템플릿 적용

    # form이 submit 될 때 데이터를 넣어주는 부분
    def form_valid(self, form):
        print("form_valid start")

        # 현재 선택 중인 다이어리에 일기를 작성하기 위해 diary_num을 get방식으로 받아옴
        diary_num = (self.kwargs["q"])

        # current_user : 현재 로그인된 사용자를 나타내는 속성
        current_user = self.request.user.id
        user_id = AuthUser.objects.get(id=current_user)

        # Writen의 id에 현재 접속중인 유저의 id를 저장
        form.instance.id = user_id

        # Writen의 diary_num에 현재 선택중인 diary_num을 저장
        diary_key = Diary.objects.get(diary_num = diary_num)
        form.instance.diary_num = diary_key

        # 일기내용중에 한글과 영어 중 더 많이 사용된 언어의 모델을 사용하기 위해 각 문자의 사용량을 확인
        content = self.request.POST.get("writen_content")
        ko = 0
        eng = 0
        for i in content:
            if (ord(i) >= 65 and ord(i) <=90) or (ord(i) >= 97 and ord(i) <= 122):
                eng = eng + 1
            else:
                ko =  ko + 1

        print(ko , eng)

        # 한국어가 더 많이 사용됬으면 한국어 모델을 사용하여 예측
        if ko >= eng:

            a = WecandoConfig.lyrics_evaluation_predict(self.request.POST.get("writen_content"))
            print("한국어 모델 사용 " + str(a))

        # 영어가 더 많이 사용됬으면 영어 모델을 사용하여 예측
        else:
            a = WecandoConfig.predict_emotion(self.request.POST.get("writen_content"))
            print("영어 모델 사용 " + str(a))

        # Writen의 type_num에 예측된 감정을 저장
        type_key = Type.objects.get(type_num=a)
        form.instance.type_num = type_key

        # 예측된 감정과 같은 감정의 음악을 랜덤으로 저장하기 위한 부분
        music_max = Music.objects.filter(type_num=a).count()

        music_ran = random.randint(0, music_max - 1)

        # Writen의 music_num에 선택된 music_num을 저장
        music_key = Music.objects.filter(type_num=a)[music_ran]
        form.instance.music_num = music_key

        # 긍정적인 감정으로 예측됬을 때 긍정적인 명언 중 랜덤으로 저장하기 위한 부분
        if (a == 0 or a == 1 or a == 5):
            wise_max = Wise.objects.filter(type_num=0).count()

            wise_ran = random.randint(0, wise_max - 1)

            # Writen의 wise_num에 선택된 wise_num을 저장
            wise_key = Wise.objects.filter(type_num=0)[wise_ran]
            form.instance.wise_num = wise_key

        # 긍정적인 감정으로 예측됬을 때 긍정적인 명언 중 랜덤으로 저장하기 위한 부분
        else:
            wise_max = Wise.objects.filter(type_num=1).count()

            wise_ran = random.randint(0, wise_max - 1)

            # Writen의 wise_num에 선택된 wise_num을 저장
            wise_key = Wise.objects.filter(type_num=1)[wise_ran]
            form.instance.wise_num = wise_key
        print(form)

        # form을 저장
        form.save()

        response = super().form_valid(form)
        return response


    # 저장에 성공하면 예측을 잘 했는지 확인하기 위해 diary_check 페이지로 이동
    def get_success_url(self):
        diary_num = (self.kwargs["q"])

        return reverse('diary_check', kwargs={"pk":Writen.objects.filter(diary_num = diary_num).order_by("-writen_num")[0].pk})

# 일기 작성 완료전 감정 체크
class DiaryCheck(UpdateView):
    model = Writen  # 모델은 Writen을 사용
    context_object_name = 'writen'  # 데이터의 이름을 writen으로 설정
    fields = ["writen_title", "writen_content", "img_file"] # form에서 writen_title, writen_content, img_file을 받아옴
    template_name = "wecando/diary_check.html"  # 템플릿 설정

    # 해당 일기 데이터를 받아옴
    def get_object(self):
        writen = get_object_or_404(Writen, pk=self.kwargs['pk'])
        return writen

    # form이 submit 될 때 데이터를 넣어주는 부분
    def form_valid(self, form):

        # 일기를 잘 분석했는지 확인하는 부분
        # type_num이 10이면 잘 분석했다는 의미이므로 뒤의 과정을 생략하고 diary_detail 페이지로 이동
        if int(self.request.POST.get("type_num")) == 10:
            writen_num = (self.kwargs["pk"])

            return redirect("/diary_detail/"+str(Writen.objects.get(writen_num=writen_num).pk)+"/")

        # 일기를 잘못 분석했다면 사용자가 직접 감정을 선택하게 하여 해당 감정에 맞는 데이터로 저장
        else:
            # 사용자가 선택한 감정을 받아오는 부분
            type_num = (self.request.POST.get("type_num"))
            print(type_num)
            print(type(type_num))

            # Writen의 type_num에 선택한 감정을 저장
            type_key = Type.objects.get(type_num=type_num)
            form.instance.type_num = type_key

            # 사용자가 선택한 감정과 일치하는 노래중 랜덤하게 선택하여 저장하는 부분
            music_max = Music.objects.filter(type_num=type_num).count()

            music_ran = random.randint(0, music_max - 1)

            # 선택된 노래를 Writen의 music_num에 저장
            music_key = Music.objects.filter(type_num=type_num)[music_ran]
            form.instance.music_num = music_key

            # 긍정적인 감정일때 긍정적인 명언 중 랜덤하게 선택하여 저장하는 부분
            if (type_num == 0 or type_num == 1 or type_num == 5):
                wise_max = Wise.objects.filter(type_num=0).count()

                wise_ran = random.randint(0, wise_max - 1)

                # Writen의 wise_num에 선택된 명언을 저장
                wise_key = Wise.objects.filter(type_num=0)[wise_ran]
                form.instance.wise_num = wise_key

            # 부정적인 감정일때 부정적인 명언 중 랜덤하게 선택하여 저장하는 부분
            else:
                wise_max = Wise.objects.filter(type_num=1).count()

                wise_ran = random.randint(0, wise_max - 1)

                # Writen의 wise_num에 선택된 명언을 저장
                wise_key = Wise.objects.filter(type_num=1)[wise_ran]
                form.instance.wise_num = wise_key

        print(form)

        # form을 저장
        form.save()

        response = super().form_valid(form)
        return response

    # 성공하면 diary_detail 페이지로 이동
    def get_success_url(self):
        writen_num = (self.kwargs["pk"])
        return reverse('diary_detail',
                       kwargs={"pk": Writen.objects.get(writen_num=writen_num).pk})

# 일기 수정
class DiaryUpdate(UpdateView):
    model = Writen  # 모델은 Writen을 사용
    context_object_name = 'writen'  # 데이터 writen을 사용 
    fields = ["writen_title", "writen_content", "img_file"] # form 에서 데이터를 받아옴
    template_name = "wecando/diary_update.html" # 템플릿을 설정

    # 해당 일기를 받아오는 부분
    def get_object(self):
        writen = get_object_or_404(Writen, pk=self.kwargs['pk'])
        return writen

    # form이 submit 될 때 데이터를 넣어주는 부분
    def form_valid(self, form):

        # 일기내용중에 한글과 영어 중 더 많이 사용된 언어의 모델을 사용하기 위해 각 문자의 사용량을 확인
        content = self.request.POST.get("writen_content")
        ko = 0
        eng = 0
        for i in content:
            if (ord(i) >= 65 and ord(i) <= 90) or (ord(i) >= 97 and ord(i) <= 122):
                eng = eng + 1
            else:
                ko = ko + 1

        print(ko, eng)

        # 한국어가 더 많으면 한국어 모델을 사용
        if ko >= eng:

            a = WecandoConfig.lyrics_evaluation_predict(self.request.POST.get("writen_content"))
            print("한국어 모델 사용 " + str(a))
        
        # 영어가 더 많으면 영어 모델을 사용
        else:
            a = WecandoConfig.predict_emotion(self.request.POST.get("writen_content"))
            print("영어 모델 사용 " + str(a))

        # Writen의 type_num에 분석된 감정을 저장
        type_key = Type.objects.get(type_num=(a))
        form.instance.type_num = type_key

        # 분석된 감정과 일치하는 감정의 노래중 랜덤으로 선택하는 부분
        music_max = Music.objects.filter(type_num=a).count()

        music_ran = random.randint(0, music_max - 1)

        # Writen의 music_num에 선택된 노래를 저장
        music_key = Music.objects.filter(type_num=a)[music_ran]
        form.instance.music_num = music_key

        # 긍정적인 감정일때 긍정적인 명언 중 랜덤하게 선택하여 저장하는 부분
        if (a == 0 or a == 1 or a == 5):
            wise_max = Wise.objects.filter(type_num=0).count()

            wise_ran = random.randint(0, wise_max - 1)

            # Writen의 wise_num에 선택된 명언을 저장
            wise_key = Wise.objects.filter(type_num=0)[wise_ran]
            form.instance.wise_num = wise_key
            
        # 부정적인 감정일때 부정적인 명언 중 랜덤하게 선택하여 저장하는 부분
        else:
            wise_max = Wise.objects.filter(type_num=1).count()

            wise_ran = random.randint(0, wise_max - 1)

            # Writen의 wise_num에 선택된 명언을 저장
            wise_key = Wise.objects.filter(type_num=1)[wise_ran]
            form.instance.wise_num = wise_key

        print(form)

        # form을 저장
        form.save()
        
        response = super().form_valid(form)
        return response

    # 성공하면 분석을 잘 했는지 확인하기 위해 diary_check 페이지로 이동
    def get_success_url(self):
        writen_num = (self.kwargs["pk"])

        return reverse('diary_check',
                       kwargs={"pk": Writen.objects.get(writen_num = writen_num).pk})


# 일기 삭제
def write_delete(request, pk):
    
    # 해당일기를 받아와서 일기삭제후 calendar 페이지로 이동
    write = get_object_or_404(Writen, pk=pk)
    diary_num = write.diary_num.diary_num
    print(diary_num)
    write.delete()
    return redirect("/calendar/"+str(diary_num)+"/")

# 비밀번호 찾기
# django.contrib.auth 앱에 속한 모듈, 내장 함수 사용
# Django에서 제공하는 기본적인 비밀번호 재설정 폼 (폼을 통해 이메일 주소를 입력하여 비밀번호 재설정 이메일을 요청)
def password_reset_request(request):
    # POST 메서드로 요청이 들어왔을 때 실행
    if request.method == "POST":
        # PasswordResetForm(django.contrib.auth.forms 내장 모듈에서 폼 제공)을 이용하여 POST된 데이터를 폼으로 변환
        password_reset_form = PasswordResetForm(request.POST)
        # 폼이 유효한지 확인
        if password_reset_form.is_valid():
            # 폼에서 이메일 데이터 추출
            data = password_reset_form.cleaned_data['email']
            # get_user_model() : Django에서 제공하는 유저 모델을 가져오는 함수
            # 입력된 이메일과 일치하는 사용자들을 가져옴
            associated_users = get_user_model().objects.filter(Q(email=data))
            # 연결된 사용자가 존재하는 경우
            if associated_users.exists():
                # 모든 연결된 사용자에 대해 처리
                for user in associated_users:
                    # django.contrib.sites 내장 모듈에서 함수 제공
                    # get_current_site(request) : 현재 사이트 정보 가져오는 함수
                    # 현재 사이트의 도메인 가져오기
                    current_site = get_current_site(request)
                    # 이메일에 보내질 제목 및 템플릿(이메일 내용) 설정
                    subject = '비밀번호 재설정'
                    email_template_name = "wecando/password_reset_email.html"
                    c = {
                        "email": user.email,
                        'domain': "http://192.168.3.22:8000",
                        'site_name': '11:57',
                        # python 표준 라이브러리인 base64 : urlsafe_base64_encode 함수 제공
                        # 유저의 primary key를 base64로 인코딩하여 토큰 생성
                        # 사용자의 고유 식별자(user.pk)를 안전하게 url에 넣기 위한 함수
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        # Django에서 제공하는 유저에 대한 기본 토큰 생성(django.contrib.auth.tokens 내장 모듈에서 토큰 생성기 제공)
                        # 비밀번호 재설정 토큰 생성
                        'token': default_token_generator.make_token(user),
                    }
                    # 이메일 내용 렌더링
                    # 템플릿 렌더링 -> 문자열 생성 (이메일 본문 생성)
                    email = render_to_string(email_template_name, c)
                    # 이메일 전송 시도
                    try:
                        # send_mail: Django에서 제공하는 메일 전송 함수(이메일을 보내기 위함)
                        send_mail(subject, email, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
                    # 잘못된 헤더가 발견되면 에러 응답
                    except BadHeaderError:
                        return HttpResponse('Invalid header found.')
                    # 비밀번호 재설정 완료 페이지로 리다이렉트
                    return redirect("/password_reset/done/")
        else:
            # 폼이 유효하지 않은 경우 에러 페이지 렌더링
            return render(request, 'wecando/password_reset_done_fail.html')

    else:
        # GET 메서드로 요청이 들어온 경우 빈 폼을 생성
        password_reset_form = PasswordResetForm()
    # 비밀번호 재설정 페이지 렌더링
    return render(
        request=request,
        template_name='wecando/password_reset.html',
        context={'password_reset_form': password_reset_form})





# 다이어리 삭제
def diary_delete(request, pk):
    
    # 해당 다이어리를 받아와 삭제후 diary페이지로 이동
    diary = get_object_or_404(Diary, pk=pk)
    diary.delete()
    return redirect("/diary/")

# 다이어리 표지 변경
class CoverUpdate(UpdateView):
    model = Diary   # 모델은 Diary를 사용

    template_name = "wecando/cover_update.html" # 템플릿을 설정

    # 해당 다이어리를 받아옴
    def get_object(self):
        diary = get_object_or_404(Diary, pk=self.kwargs['pk'])
        return diary

    # 성공하면 diary 페이지로 이동
    def get_success_url(self):

        return reverse('diary')

# 분석된 감정들을 보여주는 페이지
class Analysis(ListView):
    model = Writen  # 모델은 Writen을 사용
    template_name = "wecando/analysis.html" # 템플릿을 설정

# 다이어리 커버 이미지를 생성하는 페이지
class CoverCreate(ListView):
    model = Diary   # 모델은 Diary를 사용
    template_name = "wecando/cover_create.html" # 템플릿을 설정
