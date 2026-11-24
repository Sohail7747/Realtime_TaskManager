from django.urls import path
from . import admin_api

urlpatterns = [
    path("users/", admin_api.admin_users_api, name="admin_users_api"),
    path("users/<int:pk>/", admin_api.admin_user_detail_api, name="admin_user_detail_api"),
    path("tasks/", admin_api.admin_tasks_api, name="admin_tasks_api"),
    path("tasks/<int:pk>/", admin_api.admin_task_detail_api, name="admin_task_detail_api"),
]
