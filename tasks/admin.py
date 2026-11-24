from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("id", "task_name", "date", "time", "status", "created_by")
    list_filter = ("status", "date")
    search_fields = ("task_name", "created_by__username")
