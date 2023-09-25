from django.urls import path

from .views import UserList, UserChange, UserCreate, \
    UserLogs, UserDeleteView, GroupCreate, GroupList, \
    GroupChange, GroupDeleteView, UserProfile

app_name = 'accounts'

urlpatterns = [
    path('', UserList.as_view(), name="user_list"),
    path('details/<pk>/', UserChange.as_view(), name="change_list"),
    path('create/', UserCreate.as_view(), name="user_create"),
    path('logs/', UserLogs.as_view(), name="user_logs"),
    path("details/<pk>/delete/", UserDeleteView.as_view(), name="user_delete"),
    path("groupCreate/", GroupCreate.as_view(), name="GroupCreate"),
    path('group/details/<pk>/', GroupChange.as_view(), name="change_group"),
    path('group/', GroupList.as_view(), name="group_list"),
    path("group/<pk>/delete/", GroupDeleteView.as_view(), name="group_delete"),
    path("profile", UserProfile.as_view(), name="profile")
]
