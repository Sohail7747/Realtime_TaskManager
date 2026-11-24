from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from tasks.models import Task
from .models import User
from .serializers import RegistrationSerializer, LoginSerializer, UserSerializer

def login_page(request):
    if request.user.is_authenticated:
        return redirect("admin_dashboard" if request.user.is_staff else "home")
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        
        user = authenticate(request, username=username, password=password)
        
        if user and user.is_active:
            login(request, user)
            return redirect("admin_dashboard" if user.is_staff else "home")
        
        messages.error(request, "Invalid username or password.")
    return render(request, "accounts/login.html")

def register_page(request):
    if request.user.is_authenticated:
        return redirect("home")
    
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        password2 = request.POST.get("password2", "")
        if password != password2:
            messages.error(request, "Passwords do not match.")
        elif User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
        else:
            try:
                validate_password(password)
            except ValidationError as exc:
                for error in exc.messages:
                    messages.error(request, error)
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                login(request, user)
                return redirect("home")
    return render(request, "accounts/register.html")

@login_required
def logout_page(request):
    logout(request)
    return redirect("login")

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@user_passes_test(is_admin, login_url="/login/")
def admin_dashboard_page(request):
    
    context = {
        "total_users": User.objects.count(),
        "active_users": User.objects.filter(is_active=True).count(),
        "total_tasks": Task.objects.count(),
        "running_tasks": Task.objects.filter(status=Task.Status.RUNNING).count(),
        "stopped_tasks": Task.objects.filter(status=Task.Status.STOPPED).count(),
    }
    return render(request, "admin_panel/dashboard.html", context)

@user_passes_test(is_admin, login_url="/login/")
def admin_users_page(request):
    return render(request, "admin_panel/users.html", {"users": User.objects.order_by("-date_joined")})

@user_passes_test(is_admin, login_url="/login/")
def admin_tasks_page(request):
    from tasks.models import Task
    return render(request, "admin_panel/tasks.html", {"tasks": Task.objects.select_related("created_by").order_by("-created_at")})

@api_view(["POST"])
@permission_classes([AllowAny])
def register_api(request):
    serializer = RegistrationSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    login(request, user)
    return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

@api_view(["POST"])
@permission_classes([AllowAny])
def login_api(request):
    serializer = LoginSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    login(request, user)
    return Response({"message": "Login successful.", "user": UserSerializer(user).data})

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_api(request):
    logout(request)
    return Response({"message": "Logout successful."})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me_api(request):
    return Response(UserSerializer(request.user).data)
