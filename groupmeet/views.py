from django.contrib.auth.forms import UsernameField
from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect,  get_object_or_404
from .models import Schedule, Group, GroupSchedule, UserGroup, Comment
from account.models import CustomUser
from django.contrib.auth.decorators import login_required
import datetime
import calendar
from .calendar import (Calendar, UserCalendar)
from django.utils.safestring import mark_safe
import logging
import json
from django.core import serializers
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from .forms import (UserScheduleCreationForm, GroupScheduleCreationForm)
from django.contrib import messages

#Calendar: 한달 단위 모든 일정
#Schedule: 일정 하나 하나
# Create your views here.

commentlist=[]

def userCalendar_view(request):
   if request.user.is_authenticated:
      user = get_object_or_404(CustomUser, pk=request.user.id)

      today = get_date(request.GET.get('month'))
      prev_month_url = prev_month(today)
      next_month_url = next_month(today)
      
      cal = UserCalendar(today.year, today.month)
      cal = cal.formatmonth(withyear=True, user=user)
      cal = mark_safe(cal)

      form = UserScheduleCreationForm()
      invitedGroup = UserGroup.objects.filter(user=user, allowed=0)      
      invitedGroup=list(invitedGroup)

      return render(request, 'userCalendar.html', {
                              'calendar' : cal,
                              'cur_year' : today.year, 
                              'cur_month' : today.month, 
                              'prev_month' : prev_month_url, 
                              'next_month' : next_month_url,
                              'form' : form,
                              'invitedGroup':invitedGroup
                              })
   else:
      return render(request,'forbidden.html')
      
def show_userschedule(request):
   if request.user.is_authenticated:
      jsonObj = json.loads(request.body) #jsonObg.get('key')를 통해 접근가능, value들은 다 string형임

      year = int(jsonObj.get('year'))
      month = int(jsonObj.get('month'))
      day = int(jsonObj.get('day'))

      user = get_object_or_404(CustomUser, pk=request.user.id)
      date = datetime.date(year, month, day)

      schedules = Schedule.objects.filter(user=user, start__date__lte=date, end__date__gte=date).order_by('start')   # 유저가 클릭한 날짜에 있는 스케줄들
      data = serializers.serialize("json", schedules)                                                                # 스케줄들을 json형태로 바꿔줌
      
      return JsonResponse(data, safe=False)    # 파라미터로 딕셔너리 형태가 아닌 것을 받으면 두 번째 파라미터로 safe=False를 해야함
   else:
      return render(request,'forbidden.html')

def delete_userschedule(request):
   if request.user.is_authenticated:
      jsonObj = json.loads(request.body) #jsonObg.get('key')를 통해 접근가능, value들은 다 string형임
      pk = int(jsonObj.get('pk'))

      schedule = get_object_or_404(Schedule, pk=pk)
      schedule.delete()

      return JsonResponse(jsonObj)
   else:
      return render(request,'forbidden.html')

def create_userschedule(request):
   if request.user.is_authenticated:
      user = get_object_or_404(CustomUser, pk=request.user.id)
      new_schedule = Schedule(user=user)
      form = UserScheduleCreationForm(request.POST)
      
      if form.is_valid():
         s = form.cleaned_data['start_date'].strftime('%Y-%m-%d') + ' ' + form.cleaned_data['start_hour'] + ':' + form.cleaned_data['start_minute']
         e = form.cleaned_data['end_date'].strftime('%Y-%m-%d') + ' ' + form.cleaned_data['end_hour'] + ':' + form.cleaned_data['end_minute']
         start = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M')
         end = datetime.datetime.strptime(e, '%Y-%m-%d %H:%M')
         title = form.cleaned_data['title']
         color = form.cleaned_data['color']

         new_schedule.start = start
         new_schedule.end = end
         new_schedule.title = title
         new_schedule.color = color

         new_schedule.save()

         data = {
            'result' : 'success'
         }
      else:
         data = {
            'result' : 'fail',
            'form_errors' : form.errors.as_json()
         }

      return JsonResponse(data)
   else:
      return render(request,'forbidden.html')

@login_required
def edit_userschedule(request, schedule_id):
   if request.user.is_authenticated:
      schedule = get_object_or_404(Schedule, pk=schedule_id)
      if request.method == "POST":
         form = UserScheduleCreationForm(request.POST)
         if form.is_valid():
            s = form.cleaned_data['start_date'].strftime('%Y-%m-%d') + ' ' + form.cleaned_data['start_hour'] + ':' + form.cleaned_data['start_minute']
            e = form.cleaned_data['end_date'].strftime('%Y-%m-%d') + ' ' + form.cleaned_data['end_hour'] + ':' + form.cleaned_data['end_minute']
            start = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M')
            end = datetime.datetime.strptime(e, '%Y-%m-%d %H:%M')

            title = form.cleaned_data['title']
            color = form.cleaned_data['color']

            schedule.start = start
            schedule.end = end
            schedule.title = title
            schedule.color = color

            schedule.save()

            data = {
               'result' : 'success'
            }
         else:
            data = {
               'result' : 'fail',
               'form_errors' : form.errors.as_json()
            }
      else:          # GET방식으로 들어오면
         s = schedule.start.strftime('%Y-%m-%d %H:%M').split(' ')
         e = schedule.end.strftime('%Y-%m-%d %H:%M').split(' ')
         s_time = s[1].split(':')
         e_time = e[1].split(':')

         start_date = s[0]
         start_hour = s_time[0]
         start_minute = s_time[1]

         end_date = e[0]
         end_hour = e_time[0]
         end_minute = e_time[1]
         title = schedule.title
         color = schedule.color
         
         data = {
            'start_date' : start_date,
            'start_hour' : start_hour,
            'start_minute' : start_minute,
            'end_date' : end_date,
            'end_hour' : end_hour,
            'end_minute' : end_minute,
            'title' : title,
            'color' : color,
         }
      return JsonResponse(data)
   else:
      return render(request,'forbidden.html')

#사용자의 Id를 받아와서 사용자가 속한 group list return
def getuserGroupList(request):
   if request.user.is_authenticated:
      user = request.user
      usergroup=UserGroup.objects.filter(user=user, allowed=2)

      userGroup_list=[]
      alluser_list = []

      for ug in usergroup:
         userGroup_list.append(ug.group)
         allUser = UserGroup.objects.filter(group=ug.group, allowed=2).exclude(user=user)
         alluser_list.append(allUser)

      invitedGroup = UserGroup.objects.filter(user=user, allowed=0)
      invitedGroup=list(invitedGroup)
      return render(request,'userGroupList.html',{'userGroup_list':userGroup_list,'invitedGroup':invitedGroup,'alluser_list':alluser_list})
   else:
      return render(request,'forbidden.html')
      
# 그룹 캘린더 보여주기
@login_required
def groupCalendar_view(request, id): 
   if request.user.is_authenticated:
      try:
         group = Group.objects.get(id=id)
      except Group.DoesNotExist:
         return render(request,'forbidden.html')   
      members=[]
      allmembers= group.members.all()
      waiting_members = []    # allowed가 0인 멤버들 담을 리스트
      nono_members = []       # allowed가 1인 멤버들 담을 리스트
      for member in allmembers:    # 그룹원들에 대해 루프
         ug = UserGroup.objects.get(user=member, group=group)
         if ug.allowed == 0:
            waiting_members.append(member)
         elif ug.allowed==2:
            members.append(member)
         else:
            nono_members.append(member)

      invitedGroup = UserGroup.objects.filter(user=request.user, allowed=0)
      invitedGroup=list(invitedGroup)

      today = get_date(request.GET.get('month'))
      prev_month_url = prev_month(today)
      next_month_url = next_month(today)
      cur_month_url = "month=" + str(today.year) + '-' + str(today.month)
      # now = datetime.now()
      # cur_year = now.year        # 현재 연도
      # cur_month = now.month      # 현재 월

      if request.user in members:
         cal = Calendar(today.year, today.month)
         cal = cal.formatmonth(withyear=True, group=group)
         cal = mark_safe(cal)
         form = GroupScheduleCreationForm()

         #group에 속한 user들의 모든 일정 list로 return
         if request.GET.get('day'):
            day = request.GET.get('day')
         else:
            day = today.day
         schedule_list={'7':[0,0], '8':[0,0], '9':[0,0], '10':[0,0], '11':[0,0], '12':[0,0], '13':[0,0], '14':[0,0], '15':[0,0], '16':[0,0], '17':[0,0], '18':[0,0], '19':[0,0], '20':[0,0], '21':[0,0], '22':[0,0], '23':[0,0]}

         date_format = str(today.year)+"-"+str(today.month).zfill(2)+"-"+str(day).zfill(2)

         for user in members:
            schedules = Schedule.objects.filter(user=user, start__lte = date_format+" 23:59:59", end__gte = date_format+" 07:00:00")
            if schedules:
               for schedule in schedules:
                  if schedule.start < datetime.datetime(int(today.year), int(today.month), int(day), 7, 0):
                     s = 7
                  else:
                     if schedule.start.minute == 30:
                        schedule_list[str(schedule.start.hour)][1] = -1
                     s = schedule.start.hour + 1 if schedule.start.minute == 30 else int(schedule.start.hour)
                  if schedule.end > datetime.datetime(int(today.year), int(today.month), int(day)+1, 0, 0):
                     e = 23
                  else:
                     if schedule.end.minute == 30:
                        schedule_list[str(schedule.end.hour)][0] = -1
                     e = schedule.end.hour - 1
                  for i in range(s, e+1):
                     schedule_list[str(i)][0] = -1
                     schedule_list[str(i)][1] = -1
         groupSchedules = GroupSchedule.objects.filter(group=group, start__lte = date_format+" 23:59:59", end__gte = date_format+" 07:00:00")
         if groupSchedules:
            for schedule in groupSchedules:
               if schedule.start < datetime.datetime(int(today.year), int(today.month), int(day), 7, 0):
                  s = 7
               else:
                  if schedule.start.minute == 30:
                        schedule_list[str(schedule.start.hour)][1] = GroupSchedule.objects.get(id=schedule.id)
                  s = schedule.start.hour+1 if schedule.start.minute == 30 else schedule.start.hour
                  if schedule.end > datetime.datetime(int(today.year), int(today.month), int(day)+1, 0, 0):
                     e = 23
                  else:
                     if schedule.end.minute == 30:
                        schedule_list[str(schedule.end.hour)][0] = GroupSchedule.objects.get(id=schedule.id)
                     e = schedule.end.hour - 1
                  for i in range(s, e+1):
                     schedule_list[str(i)][0] = GroupSchedule.objects.get(id=schedule.id)
                     schedule_list[str(i)][1] = GroupSchedule.objects.get(id=schedule.id)
         comments=Comment.objects.filter(group=group)
         comment_list=list(comments)
         return render(request, 'groupCalendar.html',
         {'groupschedules':groupSchedules,'calendar' : cal, 'cur_month' : cur_month_url, 'prev_month' : prev_month_url, 'next_month' : next_month_url, 'group' : group, 'form' : form,
         'schedule_list':schedule_list, 'date' : [today.year, str(today.month).zfill(2), str(day).zfill(2)],'comment_list':comment_list, 'members':members, 'waiting_members' : waiting_members,'invitedGroup':invitedGroup, 'nono_members' : nono_members})
      else:
         return render(request,'forbidden.html')
   else:
      return render(request,'forbidden.html')

def get_date(request_day):
   if request_day:
      year, month = (int(x) for x in request_day.split('-'))
      return datetime.date(year, month, day=1)
   return datetime.datetime.today()

def prev_month(day):                                                          # 이전 달에 해당하는 URL 리턴
   first = day.replace(day=1)                                                 # first = today가 있는 달의 첫번째 날이 됨
   prev_month = first - datetime.timedelta(days=1)                            # prev_month = 첫 번째 날에서 하루를 뺌, 즉 저번 달 말일이 됨
   month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
   return month

def next_month(day):                                                          # 다음 달에 해당하는 URL 리턴
   days_in_month = calendar.monthrange(day.year, day.month)[1]
   last = day.replace(day=days_in_month)                                      # last = today가 있는 달의 마지막 날이 됨
   next_month = last + datetime.timedelta(days=1)                             # next_month = today에서 하루가 더 해진 날, 즉 다음 달 1일이 됨
   month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
   return month

def createGroupSchedule(request, id):
   if request.user.is_authenticated:
      group = get_object_or_404(Group, pk=id)
      new_schedule = GroupSchedule(group=group)
      form = GroupScheduleCreationForm(request.POST)
      
      if form.is_valid():
         s = form.cleaned_data['start_date'].strftime('%Y-%m-%d') + ' ' + form.cleaned_data['start_hour'] + ':' + form.cleaned_data['start_minute']
         e = form.cleaned_data['end_date'].strftime('%Y-%m-%d') + ' ' + form.cleaned_data['end_hour'] + ':' + form.cleaned_data['end_minute']
         start = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M')
         end = datetime.datetime.strptime(e, '%Y-%m-%d %H:%M')
         title = form.cleaned_data['title']

         new_schedule.start = start
         new_schedule.end = end
         new_schedule.title = title

         new_schedule.save()

         data = {
            'result' : 'success'
         }
      else:
         data = {
            'result' : 'fail',
            'form_errors' : form.errors.as_json()
         }

      return JsonResponse(data)
   else:
      return render(request,'forbidden.html')

def addComment(request, id):
   if request.user.is_authenticated:
      comment=Comment()
      comment.writer=request.user
      comment.group = Group.objects.get(pk=id)
      comment.pub_date=timezone.datetime.now()
      comment.content=request.POST.get('content')
      if comment.content!='':
         comment.save()
      return redirect('groupCalendar_view',id)
   else:
      return render(request,'forbidden.html')

def delComment(request,group_id,comment_id):
   if request.user.is_authenticated:
      delete_comment = get_object_or_404(Comment, pk=comment_id)
      if delete_comment.writer == request.user:
         delete_comment.delete()
      return redirect('groupCalendar_view',group_id)
   else:
      return render(request,'forbidden.html')

def allowRegister(request, id):
   if request.user.is_authenticated:
      groupSchedule = GroupSchedule.objects.get(pk = id)
      newUserSchedule = Schedule()
      user = request.user.nickname
      newUserSchedule.user = CustomUser.objects.get(nickname=user)
      newUserSchedule.start =  groupSchedule.start
      newUserSchedule.end = groupSchedule.end
      newUserSchedule.title = groupSchedule.title
      newUserSchedule.save()
      return redirect('groupCalendar_view', groupSchedule.group.id)
   else:
      return render(request,'forbidden.html')

def deleteGroupSchedule(request, id):
   if request.user.is_authenticated:
      groupSchedule = GroupSchedule.objects.get(pk = id)
      groupMembers = groupSchedule.group.members.all()
      for member in groupMembers:
         user = CustomUser.objects.get(nickname=member.nickname)
         try:
            userSchedule = Schedule.objects.get(user=user, start=groupSchedule.start, end=groupSchedule.end, title=groupSchedule.title)
            userSchedule.delete()
         except Schedule.DoesNotExist:
            continue
      groupSchedule.delete()
      return redirect('groupCalendar_view', groupSchedule.group.id)
   else:
      return render(request,'forbidden.html')

@login_required
def createGroup(request):
   if request.user.is_authenticated:
      user = request.user
      userList = CustomUser.objects.exclude(nickname=user.nickname)
      invitedGroup = UserGroup.objects.filter(user=user, allowed=0)
      invitedGroup=list(invitedGroup)
      return render(request, "createGroup.html", {'userList':userList,'invitedGroup':invitedGroup} )
   else:
      return render(request,'forbidden.html')

def editGroup(request, group_id):
   if request.user.is_authenticated:
      groupInfo = Group.objects.get(pk=group_id)
      user = request.user.nickname
      userList = CustomUser.objects.exclude(nickname=user)
      return render(request, "editGroup.html", {'groupInfo':groupInfo, 'userList':userList})
   else:
      return render(request,'forbidden.html')

def updateGroup(request, group_id):
   if request.user.is_authenticated:
      groupInfo = Group.objects.get(pk=group_id)
      groupInfo.name = request.POST.get('name')
      members = request.POST.getlist('members[]')
      for member in members:
         print("hello");
         userGroup = UserGroup()
         userGroup.user = CustomUser.objects.get(nickname=member)
         userGroup.group = groupInfo
         userGroup.allowed = 0
         userGroup.save()
      messages.success(request, '그룹정보가 수정되었습니다.')
      return redirect('groupCalendar_view', group_id)
   else:
      return render(request,'forbidden.html')

def groupInvite(request):
   if request.user.is_authenticated:
      error_messages = []
      new_group_name = request.POST.get("new_group_name")
      new_group_members = request.POST.get("new_group_members")

      if not new_group_name:
         error_messages.append({'error_type' : 'name', 'error_content' : '그룹 이름을 지어야 합니다'})
      if not new_group_members:
         error_messages.append({'error_type' : 'members', 'error_content' : '초대할 멤버를 골라야 합니다'})
      
      if error_messages:
         data = {
            'result' : 'fail',
            'error_messages' : error_messages
         }
      else:
         user = request.user
         group = Group()
         group.name = new_group_name
         group.save()
         userGroup = UserGroup()
         userGroup.user = user
         userGroup.group = group
         userGroup.allowed = 2
         userGroup.save()
         members = new_group_members.split(',')
         for member in members:
            print(type(member))
            userGroup = UserGroup()
            new_member = CustomUser.objects.get(nickname=member)
            userGroup.user = new_member
            userGroup.group = group
            userGroup.allowed = 0
            userGroup.save()
         data = {
            'result' : 'success'
         }
      messages.success(request, '그룹이 생성되었습니다.')
      return JsonResponse(data)
   else:
      return render(request,'forbidden.html')

def invitation_view(request,id):
   if request.user.is_authenticated:
      group=get_object_or_404(Group,id=id)
      members=group.members.all()
      member_list=[]
      for member in members:
         ug= get_object_or_404(UserGroup,group = id,user=member)
         if ug.allowed==2:
            member_list.append(member)
      usergroup=get_object_or_404(UserGroup,group=id,user=request.user)
      user = get_object_or_404(CustomUser, nickname=request.user.nickname)
      invitedGroup = UserGroup.objects.filter(user=user, allowed=0)
      invitedGroup=list(invitedGroup)
      return render(request,'groupInvitation.html',{'group':group,'member_list':member_list,'usergroup':usergroup,'invitedGroup':invitedGroup})
   else:
      return render(request,'forbidden.html')

def acceptInvitation(request, id):
   if request.user.is_authenticated:
      userGroup = UserGroup.objects.get(pk=id) # userGroup id
      userGroup.allowed = 2
      userGroup.save()
      return redirect('getuserGroupList')
   else:
      return render(request,'forbidden.html')

def refuseInvitation(request, id):
   if request.user.is_authenticated:
      userGroup = UserGroup.objects.get(pk=id) # userGroup id
      userGroup.allowed = 1
      userGroup.save()
      return redirect('getuserGroupList')
   else:
      return render(request,'forbidden.html')

@login_required
def leaveGroup(request, id):
   if request.user.is_authenticated:
      group = get_object_or_404(Group, pk=id)
      usergroup = get_object_or_404(UserGroup, user=request.user, group=group)
      usergroup.delete()
      return redirect("getuserGroupList") # 수정2
   else:
      return render(request,'forbidden.html')

