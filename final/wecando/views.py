from django.shortcuts import render
from django.views.generic import ListView
from wecando.models import Test
# Create your views here.
class MainPage(ListView):
    model = Test
    template_name = "wecando/landing.html"