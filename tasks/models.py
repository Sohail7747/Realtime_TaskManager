from django.conf import settings
from django.db import models

class Task(models.Model):
    class Status(models.TextChoices):
        STOPPED = "STOPPED", "Stopped"
        RUNNING = "RUNNING", "Running"

    task_name = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.STOPPED,
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.task_name


class TaskStatusHistory(models.Model):
    task = models.ForeignKey(
        Task,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="status_history",
    )
    task_name = models.CharField(max_length=200)
    status = models.CharField(max_length=10, choices=Task.Status.choices)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="task_status_changes",
    )
    username = models.CharField(max_length=150)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-changed_at", "-pk")

    def __str__(self):
        return f"{self.task_name}: {self.get_status_display()}"
