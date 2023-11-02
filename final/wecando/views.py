from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from wecando.models import Test, DiaryNew
from django.shortcuts import render, redirect, get_object_or_404
# 회원 가입시 필요
from wecando.forms import UserForm
from django.contrib.auth import authenticate, login
# Create your views here.
# landing 페이지 생성
class MainPage(ListView):
    model = Test
    template_name = "wecando/landing.html"

# 내 모든 다이어리 표지 보기 페이지 생성
class Diary(ListView):
    model = Test
    template_name = "wecando/diary.html"

# 캘린더 페이지 생성
class Calendar(ListView):
    model = Test
    template_name = "wecando/calendar.html"

# 내 일기 상세 보기 페이지 생성
def diary_detail(request, pk):
    diary_detail = get_object_or_404(DiaryNew, pk=pk)
    return render(request, "wecando/diary_detail.html", {"diary_detail":diary_detail})

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
    model = Test
    template_name = "wecando/diary_create.html"

# 일기 작성 페이지 생성
class DiaryWrite(CreateView):
    model = DiaryNew
    fields = ["title", "content"]
    success_url = "diary_detail/"
    template_name = "wecando/diary_write.html"