from rest_framework import serializers
from .models import Task, TaskStatusHistory

class TaskSerializer(serializers.ModelSerializer):
    created_by_username = serializers.CharField(source="created_by.username", read_only=True)

    class Meta:
        model = Task
        fields = (
            "id", "task_name", "date", "time", "status",
            "created_by", "created_by_username", "created_at", "updated_at",
        )
        read_only_fields = ("id", "status", "created_by", "created_at", "updated_at")


class TaskStatusHistorySerializer(serializers.ModelSerializer):
    task_id = serializers.IntegerField(read_only=True, allow_null=True)

    class Meta:
        model = TaskStatusHistory
        fields = ("id", "task_id", "task_name", "status", "username", "changed_at")
        read_only_fields = fields
