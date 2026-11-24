from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import get_object_or_404
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import User
from .permissions import IsAdminUserRole
from .serializers import UserSerializer
from tasks.models import Task
from tasks.serializers import TaskSerializer
from tasks.views import broadcast_task

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def admin_users_api(request):
    if request.method == "GET":
        return Response(UserSerializer(User.objects.order_by("-date_joined"), many=True).data)
    data = request.data.copy()
    password = data.pop("password", None)
    if not password:
        return Response({"password": "This field is required."}, status=400)
    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    if not username:
        return Response({"username": "This field is required."}, status=400)
    if User.objects.filter(username=username).exists():
        return Response({"username": "A user with this username already exists."}, status=400)
    if email and User.objects.filter(email=email).exists():
        return Response({"email": "A user with this email already exists."}, status=400)
    try:
        validate_password(password)
    except ValidationError as exc:
        return Response({"password": exc.messages}, status=400)
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        is_active=data.get("is_active", True),
    )
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def admin_user_detail_api(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == "GET":
        return Response(UserSerializer(user).data)
    if request.method == "DELETE":
        if user.is_superuser:
            return Response({"detail": "Superuser accounts cannot be deleted here."}, status=400)
        user.delete()
        return Response(status=204)
    serializer = UserSerializer(user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    if serializer.validated_data.get("role") == User.Role.ADMIN and not request.user.is_superuser:
        return Response({"detail": "Only a superuser can promote an admin."}, status=403)
    serializer.save()
    return Response(serializer.data)

@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def admin_tasks_api(request):
    if request.method == "GET":
        return Response(TaskSerializer(Task.objects.select_related("created_by"), many=True).data)
    serializer = TaskSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    task = serializer.save(created_by=request.user)
    broadcast_task(task, "task.created")
    return Response(TaskSerializer(task).data, status=201)

@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated, IsAdminUserRole])
def admin_task_detail_api(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == "GET":
        return Response(TaskSerializer(task).data)
    if request.method == "DELETE":
        task.delete()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "tasks_live",
            {"type": "task_deleted", "task_id": pk},
        )
        return Response(status=204)
    serializer = TaskSerializer(task, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    broadcast_task(task, "task.updated")
    return Response(serializer.data)
