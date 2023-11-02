from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Test(models.Model):
    test_num = models.AutoField(primary_key=True)

# 일기 작성 모델
class DiaryNew(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField(blank=True)
    create_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    modify_date = models.DateTimeField(null=True, blank=True)