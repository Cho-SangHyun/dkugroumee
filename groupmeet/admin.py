from django.contrib import admin
from .models import Schedule, Group, GroupSchedule, UserGroup, Comment

# Register your models here.
# admin.site.register(User)
admin.site.register(Schedule)
admin.site.register(UserGroup)
admin.site.register(Group)
admin.site.register(GroupSchedule)
admin.site.register(Comment)