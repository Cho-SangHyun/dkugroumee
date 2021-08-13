from calendar import HTMLCalendar, weekday
from .models import Schedule, GroupSchedule
import datetime
import calendar

class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None, firstweekday=6):
        self.year = year
        self.month = month
        super(Calendar, self).__init__(firstweekday)

    def formatmonth(self, withyear=True, group=None):
        cal = f'<table class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'       # 영어로 몇 월인지, 몇 년도인지에 대한 문자열
        cal += '<tr><th colspan="2"><p onclick="go_prev_month();">저번달</p></th>' + f'<th colspan="3" class="month-number">{self.month}</th>' + '<th colspan="2"><p onclick="go_next_month();">다음달</p></th></tr>\n'
        cal += '<tr class="weekheader"><th class="sun">SUN</th><th class="mon">MON</th><th class="tue">TUE</th><th class="wed">WED</th><th class="thu">THU</th><th class="fri">FRI</th><th class="sat">SAT</th></tr>\n' 
        # cal += f'{self.formatweekheader()}\n'                                              # 일 ~ 토 문자열 추가
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, group)}\n'
        return cal + '</table>'

    def formatweek(self, theweek, group):
        week = ''
        for d, weekday in theweek:              # d : 몇일인지(5일, 15일..) weekday : 요일(0=sun, 6=sat)
            week += self.formatday(d, group)
        return f'<tr> {week} </tr>'

    def formatday(self, day, group):
        if day != 0:
            date = datetime.date(self.year, self.month, day)  # 날짜(ex: 2021-07-26)
            min_end_time = datetime.time(9, 0, 0)         # 오전 09:00:00 객체(시간객체)
            min_datetime = datetime.datetime.combine(date, min_end_time) #날짜와 시간을 결합한 객체 (ex : 2021-07-26 09:00:00)

            group_schedules = GroupSchedule.objects.filter(group=group, start__date__lte=date, end__date__gte=date) # 이 그룹의 그룹스케줄 중 이 날 있는 스케줄들을 담음
            all_members_schedules = []            # 그룹의 모든 구성원들의 개인스케줄들 중에서, 이 날에 있는 스케줄들만 담을 리스트
            for member in group.members.all():
                member_schedule = Schedule.objects.filter(user=member, start__date__lte=date, end__date__gte=date) # 시작일이 date보다 작거나 같고, 종료일에 date보다 크거나 같은 애들 필터링
                member_schedule = member_schedule.exclude(end__lte=min_datetime)                                   # 그 중에서 date날짜의 9시 전에 끝나는 일정 제외
                all_members_schedules += member_schedule

            if all_members_schedules or group_schedules:      # 그 날에 어떠한 스케줄(그룹스케줄이던 개인스케줄이던)이라도 있으면
                return f"<td class='date is_schedule' onclick='view_day_schedule(this);'>" + f"{day}</td>"
            else:                                             # 그 날에 아무 스케줄도 없으면
                return f"<td class='date is_not_schedule' onclick='view_day_schedule(this);'>{day}</td>"
        return '<td></td>'




MONTH_NAME = ['0', 'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE', 'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER']

class UserCalendar(HTMLCalendar):
    def __init__(self, year=None, month=None, firstweekday=6):
        self.year = year
        self.month = month
        self.long_events = []                                                     # 1박2일급 이벤트들 담길 녀석
        self.days_in_month = calendar.monthrange(self.year, self.month)[1]        # 이 달 말일
        self.schedule_line_per_day = [    # 그 날짜에 표기가능한 스케줄은 3개씩임. True면 스케줄이 안 채워진 상태를 의미
            [True, True, True] for d in range(0, self.days_in_month + 1)  # 즉 schedules_line_per_day[1] = [F, F, F]면 1일에 3개의 스케줄이 채워진 것
        ]
        super(UserCalendar, self).__init__(firstweekday)

    def is_full(self, day):         # 그 날 일정들이 꽉 찼는지. 꽉 찼으면 True를 리턴
        for i in self.schedule_line_per_day[day]:
            if i == True:   # True가 하나라도 있다면 일정들이 꽉 찬 게 아니므로 False를 리턴
                return False
        return True         # 전부다 False일 때는 일정들이 꽉 찬거니까 True를 리턴

    def formatmonth(self, withyear=True, user=None):
        cal = f'<div class="calendar-container">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'       # 영어로 몇 월인지, 몇 년도인지에 대한 문자열
        # cal += '<div><div><p onclick="go_prev_month();">저번달</p></div>' + f'<div class="month-number">{self.month}</div>' + '<div><p onclick="go_next_month();">다음달</p></div></div>\n'
        cal += '<div class="calendar">\n<span class="day-name weekend" id="sunday">SUN</span><span class="day-name">MON</span><span class="day-name">TUE</span><span class="day-name">WED</span><span class="day-name">THU</span><span class="day-name">FRI</span><span class="day-name weekend">SAT</span>' 
        # cal += f'{self.formatweekheader()}\n'                                              # 일 ~ 토 문자열 추가
        for index, week in enumerate(self.monthdays2calendar(self.year, self.month)):
            cal += f'{self.formatweek(week, index + 1, user)}\n'
        
        st = ''
        for text in self.long_events:
            st += text
        return cal + f'{st}</div></div>'

    def formatmonthname(self, theyear, themonth, withyear=True):
        """
        Return a month name as a table row.
        """
        if withyear:
            s = '%s %s' % (MONTH_NAME[themonth], theyear)
        else:
            s = '%s' % MONTH_NAME[themonth]
        return '<div class="calendar-header"><h1 class="%s"><i class="far fa-calendar-alt"></i>%s</h1>' % (self.cssclass_month_head, s) + '<div class="header-body"><i onclick="go_prev_month();" class="fas fa-chevron-circle-left go-prev"></i>' + ' <i onclick="go_next_month();" class="fas fa-chevron-circle-right go-next"></i></div></div>\n' 

    def formatweek(self, theweek, week_num, user):         # week_num : 그 달의 몇 번째 주인지
        week = ''
        for d, weekday in theweek:              # d : 몇일인지(5일, 15일..) weekday : 요일(0=sun, 6=sat)
            week += self.formatday(d, week_num, user)
        return f'{week}'

    def formatday(self, day, week_num, user):              # week_num : 그 달의 몇 번째 주인지
        if day != 0:
            if self.is_full(day) == True: # 이 날 일정들이 꽉 찼다면
                pass
            else:                         # 이 날 일정들이 꽉 차지 않았다면 
                break_point = -1          # first, second, thrid line 중 어느 라인에 스케줄을 추가할 것인지에 대한 변수
                date = datetime.date(self.year, self.month, day)
                if day == 1:
                    long_schedules_per_day = Schedule.objects.filter(user=user, start__date__lte=date, end__date__gte=date).order_by('start')
                    long_schedules_per_day = long_schedules_per_day.exclude(start__date=date, end__date=date)
                else:    
                    long_schedules_per_day = Schedule.objects.filter(user=user, start__date=date, end__date__gt=date).order_by('start') # 그 날 일정 중 1박2일 이상급 일정들 필터링
                                                                                                    # 문제점 : 8월 27~9월 3일정을 예로 하면, 9월꺼를 만들 때 필터링안됨
                
                if len(long_schedules_per_day) > 3:                            # 필터링된 일정이 3개 이상이면 3개까지만 추리기
                    long_schedules_per_day = long_schedules_per_day[0:3]

                for schedule in long_schedules_per_day: # 각 1박2일급 일정들에 대해 루프
                    start_date = schedule.start             # 시작일
                    end_date = schedule.end                 # 종료일
                    event_title = ['', '', '']
                    event_line = [False, False, False]

                    if (self.year != start_date.year) or (self.month != start_date.month):      # 시작일이 이번달보다 이전이라면
                        start_date = start_date.replace(month=self.month, day=1)                # 시작일을 이번달 1일로 여기기
                    
                    if (self.year != end_date.year) or (self.month != end_date.month):                    # 종료일이 이번달보다 이후라면
                        end_date = end_date.replace(month=self.month, day=self.days_in_month)             # 종료일을 이번달 말일로 여기기

                    start_week_number = int(start_date.strftime("%U"))  # 시작일이 몆 주차인지
                    end_week_number = int(end_date.strftime("%U"))      # 종료일이 몇 주차인지
                    num_of_event_line = end_week_number - start_week_number + 1      # 생성할 event요소들 개수, 즉 줄 개수. 예를 들어 3주에 걸치는 일정이면 3개의 요소를 만들어야 하므로

                    for i in range(0, 3):
                        if self.schedule_line_per_day[start_date.day][i] == True:
                            break_point = i
                            break
                        # break_point = -1  #schedule_line_per_day[start_date.day]의 값이 전부다 F면 스케줃들이 꽉 찬 거니까

                    # if break_point != -1:
                    for d in range(start_date.day, end_date.day + 1):
                        self.schedule_line_per_day[d][break_point] = False
                    event_title[break_point] = schedule.title
                    event_line[break_point] = True
                    event_color = schedule.color

                    lines_length = 0   # 몇 칸 차지할지 길이에 대한 변수

                    if num_of_event_line == 1:   # 한 줄만 만들어진다면
                        lines_length = end_date.day - start_date.day + 1
                        x_start = (start_date.weekday() + 2) if start_date.weekday() != 6 else 1
                        y_start = week_num + 1

                        self.long_events.append(
                            f'<div class="long-event-container" xsize="{lines_length}" xstart="{x_start}" ystart="{y_start}"">\
                                <div class="event-header"></div>\
                                <div class="first-event" is_event="{event_line[0]}" is_first="True" is_last="True" selected_color="{event_color}">{event_title[0]}</div>\
                                <div class="second-event" is_event="{event_line[1]}" is_first="True" is_last="True" selected_color="{event_color}">{event_title[1]}</div>\
                                <div class="third-event" is_event="{event_line[2]}" is_first="True" is_last="True" selected_color="{event_color}">{event_title[2]}</div>\
                            </div>'
                        )
                    else:
                        for i in range(1, num_of_event_line + 1):
                            if i == 1:
                                lines_length = (5 - start_date.weekday() + 1) if start_date.weekday() != 6 else 7   # 첫 번째 줄의 길이(몇 칸 차지할지)
                                x_start = (start_date.weekday() + 2) if start_date.weekday() != 6 else 1
                                y_start = week_num + 1

                                self.long_events.append(
                                    f'<div class="long-event-container" xsize="{lines_length}" xstart="{x_start}" ystart="{y_start}"">\
                                        <div class="event-header"></div>\
                                        <div class="first-event" is_event="{event_line[0]}" is_first="True" is_last="False" selected_color="{event_color}">{event_title[0]}</div>\
                                        <div class="second-event" is_event="{event_line[1]}" is_first="True" is_last="False" selected_color="{event_color}">{event_title[1]}</div>\
                                        <div class="third-event" is_event="{event_line[2]}" is_first="True" is_last="False" selected_color="{event_color}">{event_title[2]}</div>\
                                    </div>'
                                )
                            elif i == num_of_event_line:
                                lines_length = (end_date.weekday() + 2) if end_date.weekday() != 6 else 1           # 마지막 줄의 길이
                                x_start = 1
                                y_start = week_num + i

                                self.long_events.append(
                                    f'<div class="long-event-container" xsize="{lines_length}" xstart="{x_start}" ystart="{y_start}"">\
                                        <div class="event-header"></div>\
                                        <div class="first-event" is_event="{event_line[0]}" is_first="False" is_last="True" selected_color="{event_color}"></div>\
                                        <div class="second-event" is_event="{event_line[1]}" is_first="False" is_last="True" selected_color="{event_color}"></div>\
                                        <div class="third-event" is_event="{event_line[2]}" is_first="False" is_last="True" selected_color="{event_color}"></div>\
                                    </div>'
                                )
                            else:
                                lines_length = 7                                                                    # 중간 줄의 길이
                                x_start = 1
                                y_start = week_num + i

                                self.long_events.append(
                                    f'<div class="long-event-container" xsize="{lines_length}" xstart="{x_start}" ystart="{y_start}"">\
                                        <div class="event-header"></div>\
                                        <div class="first-event" is_event="{event_line[0]}" is_first="False" is_last="False" selected_color="{event_color}"></div>\
                                        <div class="second-event" is_event="{event_line[1]}" is_first="False" is_last="False" selected_color="{event_color}"></div>\
                                        <div class="third-event" is_event="{event_line[2]}" is_first="False" is_last="False" selected_color="{event_color}"></div>\
                                    </div>'
                                )
                    
                    if self.is_full(day) == True:
                        break

                else:
                    short_schedules_per_day = Schedule.objects.filter(user=user, start__date=date, end__date=date).order_by('start')
                    
                    if len(short_schedules_per_day) > 3:                            # 필터링된 일정이 3개 이상이면 3개까지만 추리기
                        short_schedules_per_day = short_schedules_per_day[0:3]
                    
                    for schedule in short_schedules_per_day: # 각 당일 일정들에 대해 루프
                        event_title = ['', '', '']
                        event_line = [False, False, False]
                        event_color = schedule.color

                        for i in range(0, 3):
                            if self.schedule_line_per_day[schedule.start.day][i] == True:
                                self.schedule_line_per_day[schedule.start.day][i] = False
                                break_point = i
                                break
                        
                        s = schedule.start.strftime('%H:%M')
                        
                        event_title[break_point] = ('• ' + schedule.start.strftime('%H:%M') + ' ' + schedule.title)\
                                        if len(schedule.title) < 8 else ('• ' + schedule.start.strftime('%H:%M') + ' ' + schedule.title[:8] + '...')
                        event_line[break_point] = True

                        lines_length = 1
                        x_start = (schedule.start.weekday() + 2) if schedule.start.weekday() != 6 else 1
                        y_start = week_num + 1
                        
                        self.long_events.append(
                            f'<div class="short-event-container" xsize="{lines_length}" xstart="{x_start}" ystart="{y_start}"">\
                                <div class="event-header"></div>\
                                <div class="first-event" is_event="{event_line[0]}" selected_color="{event_color}">{event_title[0]}</div>\
                                <div class="second-event" is_event="{event_line[1]}" selected_color="{event_color}">{event_title[1]}</div>\
                                <div class="third-event" is_event="{event_line[2]}" selected_color="{event_color}">{event_title[2]}</div>\
                            </div>'
                        )

                        if self.is_full(day) == True:
                            break

            return f"<div class='day'>{day}</div>"
        return '<div class="day-disabled"></div>'

        # (schedule.end - schedule.start).days = 두 날짜간 차이. 정수형. 1박2일이면 1, 2박3일이면 2가 나옴
        # 요일구하기 : weekday()활용. 0 = 월, 6 = 일
        # 몇 주차인지 구하기 : schdule.start.strftime("%U")  -> 일요일을 주의 첫 날로 잡아서 계산. string형임


# class UserCalendar(HTMLCalendar):
#     def __init__(self, year=None, month=None, firstweekday=6):
#         self.year = year
#         self.month = month
#         super(UserCalendar, self).__init__(firstweekday)

#     def formatmonth(self, withyear=True, user=None):
#         cal = f'<table class="calendar">\n'
#         cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'       # 영어로 몇 월인지, 몇 년도인지에 대한 문자열
#         cal += '<tr><th colspan="2"><p onclick="go_prev_month();">저번달</p></th>' + f'<th colspan="3" class="month-number">{self.month}</th>' + '<th colspan="2"><p onclick="go_next_month();">다음달</p></th></tr>\n'
#         cal += '<tr class="weekheader"><th class="sun">일</th><th class="mon">월</th><th class="tue">화</th><th class="wed">수</th><th class="thu">목</th><th class="fri">금</th><th class="sat">토</th></tr>\n' 
#         # cal += f'{self.formatweekheader()}\n'                                              # 일 ~ 토 문자열 추가
#         for week in self.monthdays2calendar(self.year, self.month):
#             cal += f'{self.formatweek(week, user)}\n'
#         return cal + '</table>'

#     def formatweek(self, theweek, user):
#         week = ''
#         for d, weekday in theweek:              # d : 몇일인지(5일, 15일..) weekday : 요일(0=sun, 6=sat)
#             week += self.formatday(d, user)
#         return f'<tr> {week} </tr>'

#     def formatday(self, day, user):
#         if day != 0:
#             date = datetime.date(self.year, self.month, day)

#             schedules_per_day = Schedule.objects.filter(user=user, start__date__lte=date, end__date__gte=date).order_by('start')
#             if len(schedules_per_day) > 3:
#                 schedules_per_day = schedules_per_day[0:3]

#             d = ''
#             for schedule in schedules_per_day:
#                 d += f'<li>{schedule.title[0:7]}</li>'
#             # for member in group.members.all():
#             #     all_members_schedules += Schedule.objects.filter(user=member, start__date__lte=date, end__date__gte=date)

#             return f"<td class='date'>{day}<ul class='schedule_line'>{d}</ul></td>"
#         return '<td></td>'