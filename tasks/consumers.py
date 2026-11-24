from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .models import Task, TaskStatusHistory
from .serializers import TaskSerializer, TaskStatusHistorySerializer


@database_sync_to_async
def get_task_payload(task_id):
    task = Task.objects.select_related("created_by").filter(pk=task_id).first()
    return TaskSerializer(task).data if task else None


@database_sync_to_async
def get_history_payload(history_id, user_id):
    history = TaskStatusHistory.objects.filter(
        pk=history_id,
        task__created_by_id=user_id,
    ).first()
    return TaskStatusHistorySerializer(history).data if history else None


class TaskConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
        await self.channel_layer.group_add("tasks_live", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "channel_layer") and hasattr(self, "channel_name"):
            await self.channel_layer.group_discard("tasks_live", self.channel_name)

    async def task_event(self, event):
        task = await get_task_payload(event["task_id"])
        history = None
        if event.get("history_id") is not None:
            history = await get_history_payload(
                event["history_id"],
                self.scope["user"].pk,
            )
        if task is None:
            await self.send_json({
                "event": "task.deleted",
                "task_id": event["task_id"],
                "history": history,
            })
            return
        await self.send_json({
            "event": event["event"],
            "task": task,
            "history": history,
        })

    async def task_deleted(self, event):
        await self.send_json({
            "event": "task.deleted",
            "task_id": event["task_id"],
        })
