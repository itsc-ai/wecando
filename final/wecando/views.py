from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from wecando.models import Diary, AuthUser, Writen, Music,Wise,Type
from django.shortcuts import render, redirect, get_object_or_404, reverse
# 회원 가입시 필요
from wecando.forms import UserForm, WriteUpdateForm
from django.contrib.auth import authenticate, login

from django.db.models.functions import Cast
from django.db.models import TextField
from datetime import datetime

from django.core.exceptions import PermissionDenied

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from .decorators import unauthenticated_user
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

# 내 일기 상세 보기 페이지 생성
# class DiaryDetail(DetailView):
#     model = Writen
#     template_name = "wecando/diary_detail.html"
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

