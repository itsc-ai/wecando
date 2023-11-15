from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from wecando.models import Diary, AuthUser, Writen, Music,Wise,Type
from django.shortcuts import render, redirect, get_object_or_404, reverse
# 회원 가입시 필요
from wecando.forms import UserForm, WriteUpdateForm
from django.contrib.auth import authenticate, login
from django.apps import AppConfig
from .apps import WecandoConfig
from django.db.models.functions import Cast
from django.db.models import TextField
from datetime import datetime
import random
import tensorflow as tf
import numpy as np
from transformers import TFBertModel, BertTokenizer

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

        def lyrics_evaluation_predict(sentence):
            data_x = WecandoConfig.sentence_convert_data(sentence)  # 문장을 모델 입력 형식으로 변환
            predict = WecandoConfig.model.predict(data_x)
            predict_value = np.ravel(predict[0])
            predict_emotion: {0: '기쁨', 1: '사랑', 2: '슬픔', 3: '분노', 4: '걱정', 5: '중립'}
            # 예측된 클래스의 인덱스를 찾기.
            predicted_class = np.argmax(predict_value)

            return predicted_class

        a = lyrics_evaluation_predict(self.request.POST.get("writen_content"))
        print(a)
        type_key = Type.objects.get(type_num=a)
        form.instance.type_num = type_key

        music_max = Music.objects.filter(type_num=a).count()

        music_ran = random.randint(0, music_max - 1)

        music_key = Music.objects.filter(type_num=a)[music_ran]
        form.instance.music_num = music_key

        if (a == 0 or a == 1 or a == 5):
            wise_max = Wise.objects.filter(type_num=0).count()

            wise_ran = random.randint(0, wise_max - 1)

            wise_key = Wise.objects.filter(type_num=0)[wise_ran]
            form.instance.wise_num = wise_key
        else:
            wise_max = Wise.objects.filter(type_num=1).count()

            wise_ran = random.randint(0, wise_max - 1)

            wise_key = Wise.objects.filter(type_num=1)[wise_ran]
            form.instance.wise_num = wise_key
        print(form)

        form.save()
        # 태그와 관련된 작업을 하기 전에 form_valid()의 결괏값을 response에 저장
        response = super().form_valid(form)
        return response

    # 성공할 경우 my_review 라는 주소를 가진 페이지로 이동
    def get_success_url(self):
        diary_num = (self.kwargs["q"])

        return reverse('diary_check', kwargs={"pk":Writen.objects.filter(diary_num = diary_num).order_by("-writen_num")[0].pk})

# 일기 작성 완료전 감정 체크
class DiaryCheck(UpdateView):
    model = Writen
    context_object_name = 'writen'
    fields = ["writen_title", "writen_content", "img_file"]
    template_name = "wecando/diary_check.html"

    def get_object(self):
        writen = get_object_or_404(Writen, pk=self.kwargs['pk'])
        return writen

    def form_valid(self, form):

        if self.request.POST.get("type_num") == 10:
            writen_num = (self.kwargs["pk"])
            return reverse('diary_detail',
                           kwargs={"pk": Writen.objects.get(writen_num=writen_num).pk})
        else:
            type_num = (self.request.POST.get("type_num"))
            type_key = Type.objects.get(type_num=type_num)
            form.instance.type_num = type_key

            music_max = Music.objects.filter(type_num=type_num).count()

            music_ran = random.randint(0, music_max - 1)

            music_key = Music.objects.filter(type_num=type_num)[music_ran]
            form.instance.music_num = music_key

            if (type_num == 0 or type_num == 1 or type_num == 5):
                wise_max = Wise.objects.filter(type_num=0).count()

                wise_ran = random.randint(0, wise_max - 1)

                wise_key = Wise.objects.filter(type_num=0)[wise_ran]
                form.instance.wise_num = wise_key
            else:
                wise_max = Wise.objects.filter(type_num=1).count()

                wise_ran = random.randint(0, wise_max - 1)

                wise_key = Wise.objects.filter(type_num=1)[wise_ran]
                form.instance.wise_num = wise_key

        print(form)

        form.save()
        # 태그와 관련된 작업을 하기 전에 form_valid()의 결괏값을 response에 저장
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        writen_num = (self.kwargs["pk"])
        return reverse('diary_detail',
                       kwargs={"pk": Writen.objects.get(writen_num=writen_num).pk})

# 일기 수정
class DiaryUpdate(UpdateView):
    model = Writen
    context_object_name = 'writen'
    fields = ["writen_title", "writen_content", "img_file"]
    template_name = "wecando/diary_update.html"

    def get_object(self):
        writen = get_object_or_404(Writen, pk=self.kwargs['pk'])
        return writen

    def form_valid(self, form):

        def lyrics_evaluation_predict(sentence):
            data_x = WecandoConfig.sentence_convert_data(sentence)  # 문장을 모델 입력 형식으로 변환
            predict = WecandoConfig.model.predict(data_x)
            predict_value = np.ravel(predict[0])
            predict_emotion: {0: '기쁨', 1: '사랑', 2: '슬픔', 3: '분노', 4: '걱정', 5: '중립'}
            # 예측된 클래스의 인덱스를 찾기.
            predicted_class = np.argmax(predict_value)

            return predicted_class

        a = lyrics_evaluation_predict(self.request.POST.get("writen_content"))
        print(a)
        type_key = Type.objects.get(type_num=(a))
        form.instance.type_num = type_key

        music_max = Music.objects.filter(type_num=a).count()

        music_ran = random.randint(0, music_max - 1)

        music_key = Music.objects.filter(type_num=a)[music_ran]
        form.instance.music_num = music_key

        if (a == 0 or a == 1 or a == 5):
            wise_max = Wise.objects.filter(type_num=0).count()

            wise_ran = random.randint(0, wise_max - 1)

            wise_key = Wise.objects.filter(type_num=0)[wise_ran]
            form.instance.wise_num = wise_key
        else:
            wise_max = Wise.objects.filter(type_num=1).count()

            wise_ran = random.randint(0, wise_max - 1)

            wise_key = Wise.objects.filter(type_num=1)[wise_ran]
            form.instance.wise_num = wise_key

        print(form)

        form.save()
        # 태그와 관련된 작업을 하기 전에 form_valid()의 결괏값을 response에 저장
        response = super().form_valid(form)
        return response

    def get_success_url(self):
        writen_num = (self.kwargs["pk"])
        return reverse('diary_detail',
                       kwargs={"pk": Writen.objects.get(writen_num=writen_num).pk})

# 일기 삭제
def write_delete(request, pk):
    write = get_object_or_404(Writen, pk=pk)
    diary_num = write.diary_num.diary_num

    write.delete()
    return redirect("/calendar/"+str(diary_num)+"/")

# 일기 삭제
def diary_delete(request, pk):
    diary = get_object_or_404(Diary, pk=pk)

    diary.delete()
    return redirect("/diary/")


class CoverUpdate(UpdateView):
    model = Diary
    context_object_name = 'diary'
    fields = ["img_file"]
    template_name = "wecando/cover_update.html"

    def get_object(self):
        diary = get_object_or_404(Diary, pk=self.kwargs['pk'])
        return diary

    def get_success_url(self):

        return reverse('diary')

def test(request):
    def lyrics_evaluation_predict(sentence):
        data_x = WecandoConfig.sentence_convert_data(sentence)  # 문장을 모델 입력 형식으로 변환
        predict = WecandoConfig.model.predict(data_x)
        predict_value = np.ravel(predict[0])
        predict_emotion: {0: '기쁨', 1: '사랑', 2: '슬픔', 3: '분노', 4: '걱정', 5: '중립'}
        # 예측된 클래스의 인덱스를 찾기.
        predicted_class = np.argmax(predict_value)
        if predicted_class == 0:
            print("(기쁨 확률: {:.2f}) 기쁨을 나타내는 문장입니다.".format(predict_value[predicted_class]))
            a = "기쁨 확률:" + str(predict_value[predicted_class]) + " 기쁨을 나타내는 문장입니다."

        elif predicted_class == 1:
            print("(사랑 확률: {:.2f}) 사랑을 나타내는 문장입니다.".format(predict_value[predicted_class]))
            a = "사랑 확률:" + str(predict_value[predicted_class]) + " 사랑을 나타내는 문장입니다."

        elif predicted_class == 2:
            print("(슬픔 확률: {:.2f}) 슬픔을 나타내는 문장입니다.".format(predict_value[predicted_class]))
            a = "슬픔 확률:" + str(predict_value[predicted_class]) + " 슬픔을 나타내는 문장입니다."

        elif predicted_class == 3:
            print("(분노 확률: {:.2f} 분노를 나타내는 문장입니다.)".format(predict_value[predicted_class]))
            a = "분노 확률:" + str(predict_value[predicted_class]) + " 분노을 나타내는 문장입니다."

        elif predicted_class == 4:
            print("(걱정 확률: {:.2f} 걱정을 나타내는 문장입니다.)".format(predict_value[predicted_class]))
            a = "걱정 확률:" + str(predict_value[predicted_class]) + " 걱정을 나타내는 문장입니다."

        elif predicted_class == 5:
            print("(중립 확률: {:.2f} 중립을 나타내는 문장입니다.)".format(predict_value[predicted_class]))
            a = "중립 확률:" + str(predict_value[predicted_class]) + " 중립을 나타내는 문장입니다."

        else:
            a = "잘못된 형식의 문장입니다."

        return a
    a = lyrics_evaluation_predict("""Will it be a pavement or a sidewalk
When I finally lay my eyes on you?
Someone I've already loved
Or will you find your way out of the blue?
Will it be my flat or your apartment
When I finally realise I do?
Will we meet on Baker Street
Or find ourselves on Melrose Avenue?
I don't know who you are
But I'll save you a seat
Hang my coat on a chair next to me
I tried to reassure the waiter
Say you're down the street
He laughed at me
So here's to you
The most beautiful thing
that I have never seen
Someone on a screen asked me a question
Something about what love means to me
Maybe it's just circumstance
Or general compatibility
I don't know who you are
But I'll save you a seat
Hang my coat on a chair next to me
I tried to reassure the waiter
Say you're down the street
He laughed at me
So here's to you
The most beautiful thing
that I have never seen""")

    context = {"predict" : a}
    print(context)

    return render(request, "wecando/test.html", context)