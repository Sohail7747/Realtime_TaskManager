from asgiref.sync import sync_to_async
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import Client, TransactionTestCase
from django.urls import reverse
from rest_framework.test import APIRequestFactory, force_authenticate

from .consumers import TaskConsumer
from .models import Task, TaskStatusHistory
from .views import change_task_status


class TaskRealtimeTests(TransactionTestCase):
    def test_signed_in_user_can_view_activity_page_and_history_api(self):
        user = get_user_model().objects.create_user(
            username="history-viewer",
            password="test-password",
        )
        other_user = get_user_model().objects.create_user(
            username="other-history-viewer",
            password="test-password",
        )
        task = Task.objects.create(
            task_name="History task",
            date="2026-11-24",
            time="12:00",
            created_by=user,
        )
        other_task = Task.objects.create(
            task_name="Other user's task",
            date="2026-11-24",
            time="13:00",
            created_by=other_user,
        )
        TaskStatusHistory.objects.create(
            task=task,
            task_name=task.task_name,
            status=Task.Status.RUNNING,
            changed_by=user,
            username=user.username,
        )
        TaskStatusHistory.objects.create(
            task=other_task,
            task_name=other_task.task_name,
            status=Task.Status.STOPPED,
            changed_by=other_user,
            username=other_user.username,
        )
        client = Client()

        self.assertEqual(client.get(reverse("activity")).status_code, 302)
        client.force_login(user)
        self.assertContains(client.get(reverse("activity")), "Activity history")

        response = client.get(reverse("task_status_history"))
        self.assertEqual(response.status_code, 200)
        results = response.json()["results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["username"], user.username)
        self.assertEqual(results[0]["task_name"], task.task_name)
        task_history = client.get(
            reverse("task_history", kwargs={"pk": task.pk}),
        ).json()["results"]
        self.assertEqual(len(task_history), 1)
        self.assertEqual(task_history[0]["task_name"], task.task_name)
        self.assertEqual(
            client.get(reverse("task_history", kwargs={"pk": other_task.pk})).json()["results"],
            [],
        )

        client.force_login(other_user)
        other_results = client.get(reverse("task_status_history")).json()["results"]
        self.assertEqual(len(other_results), 1)
        self.assertEqual(other_results[0]["task_name"], other_task.task_name)

    async def test_task_status_broadcast_reaches_all_connected_users(self):
        user_model = get_user_model()
        user_one = await sync_to_async(user_model.objects.create_user)(
            username="live-user-one",
            password="test-password",
        )
        user_two = await sync_to_async(user_model.objects.create_user)(
            username="live-user-two",
            password="test-password",
        )
        task = await sync_to_async(Task.objects.create)(
            task_name="Live task",
            date="2026-11-24",
            time="12:00",
            created_by=user_one,
        )

        clients = [
            WebsocketCommunicator(TaskConsumer.as_asgi(), "/ws/tasks/"),
            WebsocketCommunicator(TaskConsumer.as_asgi(), "/ws/tasks/"),
        ]
        for communicator, user in zip(clients, (user_one, user_two)):
            communicator.scope["user"] = user
            connected, _ = await communicator.connect()
            self.assertTrue(connected)

        try:
            factory = APIRequestFactory()
            request = factory.post("/api/tasks/1/start/", {}, format="json")
            force_authenticate(request, user=user_one)
            response = await sync_to_async(change_task_status)(
                request,
                pk=task.pk,
                action="start",
            )
            self.assertEqual(response.status_code, 200)

            for index, communicator in enumerate(clients):
                message = await communicator.receive_json_from(timeout=2)
                self.assertEqual(message["event"], "task.status")
                self.assertEqual(message["task"]["status"], Task.Status.RUNNING)
                if index == 0:
                    self.assertEqual(message["history"]["username"], user_one.username)
                else:
                    self.assertIsNone(message["history"])

            request = factory.post("/api/tasks/1/stop/", {}, format="json")
            force_authenticate(request, user=user_two)
            response = await sync_to_async(change_task_status)(
                request,
                pk=task.pk,
                action="stop",
            )
            self.assertEqual(response.status_code, 200)

            for index, communicator in enumerate(clients):
                message = await communicator.receive_json_from(timeout=2)
                self.assertEqual(message["task"]["status"], Task.Status.STOPPED)
                if index == 0:
                    self.assertEqual(message["history"]["username"], user_two.username)
                else:
                    self.assertIsNone(message["history"])

            history = await sync_to_async(list)(
                TaskStatusHistory.objects.order_by("pk").values_list(
                    "status",
                    "username",
                )
            )
            self.assertEqual(
                history,
                [
                    (Task.Status.RUNNING, user_one.username),
                    (Task.Status.STOPPED, user_two.username),
                ],
            )
        finally:
            for communicator in clients:
                await communicator.disconnect()
