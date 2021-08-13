from django.db import models
from django.conf import settings
# Create your models here.

class Group(models.Model):
    name=models.CharField(max_length=50)
    members=models.ManyToManyField(settings.AUTH_USER_MODEL, through='UserGroup',through_fields=("group","user"))
    #초대한 사람들 O 수락한 사람 X

#UserGroup은 User와 Group의 중개 모델
class UserGroup(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,default='')
    group=models.ForeignKey(Group,on_delete=models.CASCADE,default='')
    allowed=models.IntegerField(default = 0)  
    #0:연관 없음, 1:초대했지만 수락하지 않음, 2:초대 후 수락 완료

class Schedule(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,default='')
    start=models.DateTimeField()
    end=models.DateTimeField()
    title=models.CharField(max_length=60)
    color=models.CharField(max_length=30, default='#838de9')

class GroupSchedule(models.Model):
    group=models.ForeignKey(Group,on_delete=models.CASCADE,default='')
    start=models.DateTimeField()
    end=models.DateTimeField()
    title=models.CharField(max_length=60)  

class Comment(models.Model):
    writer=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE) 
    group= models.ForeignKey(Group ,on_delete=models.CASCADE,default='')
    pub_date = models.DateTimeField(default='')
    content = models.TextField(default='')
