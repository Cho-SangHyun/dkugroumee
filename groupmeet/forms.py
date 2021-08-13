from django import forms
from django.forms import widgets
from .models import Schedule
from django.core.exceptions import ValidationError
import datetime

class UserScheduleCreationForm(forms.Form):
    HOUR_CHOICES = (      # 오른쪽 값 : 화면에 보이는 값, 왼쪽 값 : 실 저장되는 값
        ('00', '00'),
        ('01', '01'),
        ('02', '02'),
        ('03', '03'),
        ('04', '04'),
        ('05', '05'),
        ('06', '06'),
        ('07', '07'),
        ('08', '08'),
        ('09', '09'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
        ('13', '13'),
        ('14', '14'),
        ('15', '15'),
        ('16', '16'),
        ('17', '17'),
        ('18', '18'),
        ('19', '19'),
        ('20', '20'),
        ('21', '21'),
        ('22', '22'),
        ('23', '23'),
    )
    MINUTE_CHOICES = (
        ('00', '00'),
        ('30', '30'),
    )
    COLOR_CHOICES = (
        ('#838de9', '보라'),
        ('#6495ed', '파랑'),
        ('#28d68e', '연두'),
        ('#ff8b17', '주황'),
        ('#ff6c6c', '빨강'),
        ('#eeee00', '노랑'),
    )

    start_date = forms.DateField(widget=forms.DateInput(attrs={'type' : 'date'}))
    start_hour = forms.ChoiceField(choices=HOUR_CHOICES)
    start_minute = forms.ChoiceField(choices=MINUTE_CHOICES)

    end_date = forms.DateField(widget=forms.DateInput(attrs={'type' : 'date'}))
    end_hour = forms.ChoiceField(choices=HOUR_CHOICES)
    end_minute = forms.ChoiceField(choices=MINUTE_CHOICES)

    title = forms.CharField(max_length=60, error_messages={'required' : "일정 이름을 입력해주세요",})
    color = forms.ChoiceField(choices=COLOR_CHOICES)

    def clean_end_minute(self):
        s = self.cleaned_data['start_date'].strftime('%Y-%m-%d') + ' ' + self.cleaned_data['start_hour'] + ':' + self.cleaned_data['start_minute']
        e = self.cleaned_data['end_date'].strftime('%Y-%m-%d') + ' ' + self.cleaned_data['end_hour'] + ':' + self.cleaned_data['end_minute']

        start = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M')
        end = datetime.datetime.strptime(e, '%Y-%m-%d %H:%M')

        if start >= end:
            raise ValidationError("일정이 끝나는 시간이 시작시간보다 이후여야 합니다")
        return self.cleaned_data['end_minute']



class GroupScheduleCreationForm(forms.Form):
    HOUR_CHOICES = (      # 오른쪽 값 : 화면에 보이는 값, 왼쪽 값 : 실 저장되는 값
        ('07', '07'),
        ('08', '08'),
        ('09', '09'),
        ('10', '10'),
        ('11', '11'),
        ('12', '12'),
        ('13', '13'),
        ('14', '14'),
        ('15', '15'),
        ('16', '16'),
        ('17', '17'),
        ('18', '18'),
        ('19', '19'),
        ('20', '20'),
        ('21', '21'),
        ('22', '22'),
        ('23', '23'),
    )
    MINUTE_CHOICES = (
        ('00', '00'),
        ('30', '30'),
    )

    start_date = forms.DateField(widget=forms.DateInput(attrs={'type' : 'date'}))
    start_hour = forms.ChoiceField(choices=HOUR_CHOICES)
    start_minute = forms.ChoiceField(choices=MINUTE_CHOICES)

    end_date = forms.DateField(widget=forms.DateInput(attrs={'type' : 'date'}))
    end_hour = forms.ChoiceField(choices=HOUR_CHOICES)
    end_minute = forms.ChoiceField(choices=MINUTE_CHOICES)

    title = forms.CharField(max_length=60, error_messages={'required' : "일정 이름을 입력해주세요",})

    def clean_end_minute(self):
        s = self.cleaned_data['start_date'].strftime('%Y-%m-%d') + ' ' + self.cleaned_data['start_hour'] + ':' + self.cleaned_data['start_minute']
        e = self.cleaned_data['end_date'].strftime('%Y-%m-%d') + ' ' + self.cleaned_data['end_hour'] + ':' + self.cleaned_data['end_minute']

        start = datetime.datetime.strptime(s, '%Y-%m-%d %H:%M')
        end = datetime.datetime.strptime(e, '%Y-%m-%d %H:%M')

        if start >= end:
            raise ValidationError("일정이 끝나는 시간이 시작시간보다 이후여야 합니다")
        return self.cleaned_data['end_minute']

# class UserScheduleCreationForm(forms.ModelForm):
#     class Meta:
#         model = Schedule
#         fields = ('start', 'end', 'title')
#         widgets = {'start' : forms.DateTimeInput(attrs={'type' : 'datetime-local'}),
#                     'end' : forms.DateTimeInput(attrs={'type' : 'datetime-local'})}
#         error_messages = {
#             'start': {
#                 'required': "일정 시작 시간을 입력해주세요",
#             },

#             'end' : {
#                 'required': "일정 종료 시간을 입력해주세요",
#             },

#             'title' : {
#                 'required' : "일정 이름을 입력해주세요",
#             },
#         }

#     def clean_end(self):
#         start = self.cleaned_data.get('start')
#         end = self.cleaned_data.get('end')

#         if start >= end:
#             raise ValidationError("일정이 끝나는 시간이 시작시간보다 이후여야 합니다")
#         return end