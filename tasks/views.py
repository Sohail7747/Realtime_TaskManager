from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from .models import Task, TaskStatusHistory
from .serializers import TaskSerializer, TaskStatusHistorySerializer
from .permissions import IsOwnerOrAdminForEdit

@login_required
def home_page(request):
    return render(request, "tasks/home.html")

@login_required
def activity_page(request):
    return render(request, "tasks/activity.html")

def broadcast_task(task, event_type="task.updated", history_id=None):
    event = {
        "type": "task_event",
        "event": event_type,
        "task_id": task.pk,
    }
    if history_id is not None:
        event["history_id"] = history_id
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)("tasks_live", event)


class TaskStatusHistoryPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = "page_size"
    max_page_size = 100


class TaskStatusHistoryAPI(generics.ListAPIView):
    serializer_class = TaskStatusHistorySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TaskStatusHistoryPagination

    def get_queryset(self):
        queryset = TaskStatusHistory.objects.filter(task__created_by=self.request.user)
        task_id = self.kwargs.get("pk")
        if task_id is not None:
            queryset = queryset.filter(task_id=task_id)
        return queryset

class TaskListCreateAPI(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Task.objects.select_related("created_by").order_by("-created_at")

    def perform_create(self, serializer):
        task = serializer.save(created_by=self.request.user)
        broadcast_task(task, "task.created")

class TaskDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.select_related("created_by").all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdminForEdit]

    def perform_update(self, serializer):
        task = serializer.save()
        broadcast_task(task, "task.updated")

    def perform_destroy(self, instance):
        task_id = instance.id
        instance.delete()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "tasks_live",
            {"type": "task_deleted", "task_id": task_id},
        )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_task_status(request, pk, action):
    if action not in ("start", "stop"):
        return Response({"detail": "Invalid action."}, status=400)

    with transaction.atomic():
        task = get_object_or_404(Task.objects.select_for_update(), pk=pk)
        new_status = Task.Status.RUNNING if action == "start" else Task.Status.STOPPED
        history = None
        if task.status != new_status:
            task.status = new_status
            task.save(update_fields=["status", "updated_at"])
            history = TaskStatusHistory.objects.create(
                task=task,
                task_name=task.task_name,
                status=new_status,
                changed_by=request.user,
                username=request.user.get_username(),
            )

    if history:
        broadcast_task(task, "task.status", history_id=history.pk)
    return Response(TaskSerializer(task).data)

@login_required
def task_api_fallback(request):
    return render(request, "tasks/home.html")
