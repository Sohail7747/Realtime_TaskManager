from django.urls import path
from . import views

urlpatterns = [
    path("", views.TaskListCreateAPI.as_view(), name="task_list_create"),
    path("history/", views.TaskStatusHistoryAPI.as_view(), name="task_status_history"),
    path("<int:pk>/history/", views.TaskStatusHistoryAPI.as_view(), name="task_history"),
    path("<int:pk>/", views.TaskDetailAPI.as_view(), name="task_detail"),
    path("<int:pk>/<str:action>/", views.change_task_status, name="change_task_status"),
]
