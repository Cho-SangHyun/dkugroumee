"""calendarproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from groupmeet import views
from account import views as account_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', account_view.login_view, name="login"),
    path('admin/', admin.site.urls),
    path('grouplist/',views.getuserGroupList,name="getuserGroupList"),
    path('group/<str:id>',views.groupCalendar_view,name="groupCalendar_view"),
    path('group/<str:id>/addschedule', views.createGroupSchedule, name="createGroupSchedule"),
    path('group/<str:id>/addcomment', views.addComment, name="addComment"),
    path('group/<str:group_id>/delcomment/<str:comment_id>', views.delComment, name="delComment"),
    path('group/<str:id>/leaveGroup',views.leaveGroup,name="leaveGroup"),
    path('addschedule/<str:id>', views.allowRegister, name="allowRegister"),
    path('deleteschedule/<str:id>', views.deleteGroupSchedule, name="deleteGroupSchedule"),
    path('usercalendar/', views.userCalendar_view, name="userCalendar_view"),
    path('usercalendar/show', views.show_userschedule, name="show-userschedule"),
    path('usercalendar/delete', views.delete_userschedule, name="delete-userschedule"),
    path('usercalendar/create', views.create_userschedule, name="create-userschedule"),
    path('usercalendar/edit/<str:schedule_id>/', views.edit_userschedule, name="edit-userschedule"),
    path('account/', include('account.urls')),
    path('createGroup/', views.createGroup, name="createGroup"),
    path('createGroup/groupInvite', views.groupInvite, name="groupInvite"),
    path('editGroup/<str:group_id>', views.editGroup, name="editGroup"),
    path('editGroup/<str:group_id>/updateGroup', views.updateGroup, name="updateGroup"),
    path('groupInvitation/<str:id>',views.invitation_view,name="invitation"),
    path('groupInvitation/acceptIvitation/<str:id>', views.acceptInvitation, name="acceptInvitation"),
    path('groupInvitation/refuseIvitation/<str:id>', views.refuseInvitation, name="refuseInvitation"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)