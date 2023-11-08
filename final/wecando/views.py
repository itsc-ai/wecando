from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView
from wecando.models import Diary, AuthUser, Writen
from django.shortcuts import render, redirect, get_object_or_404, reverse
# 회원 가입시 필요
from wecando.forms import UserForm
from django.contrib.auth import authenticate, login

from django.db.models.functions import Cast
from django.db.models import TextField
from datetime import datetime
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

        pk = (self.kwargs["pk"])

        # current_user : 현재 로그인된 사용자를 나타내는 속성
        current_user = self.request.user.id

        context["today"] = datetime.today().strftime("%Y-%m-%d")

        context["writen"] = Writen.objects.filter(diary_num = pk).annotate(
	            created_str = Cast('created_at',TextField()),
                modified_str = Cast('modified_at', TextField())
	            )

        print(pk)
        print(Writen.objects.filter(diary_num = pk))
        # context 값 출력
        return context

# 내 일기 상세 보기 페이지 생성
class DiaryDetail(DetailView):
    model = Writen
    template_name = "wecando/diary_detail.html"


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
    template_name = "wecando/diary_create.html"

# 일기 작성 페이지 생성

class DiaryWrite(CreateView):
    model = Writen
    fields = ["writen_title", "writen_content", "img_file"]
    success_url = "/calendar/"
    template_name = "wecando/diary_write.html"
