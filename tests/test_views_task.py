from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from task_manager.models import Task, TaskType, Position

TASK_LIST_URL = reverse("task_manager:task-list")


class PublicTaskTest(TestCase):
    def setUp(self) -> None:
        task_type = TaskType.objects.create(name="Test TaskType")
        Task.objects.create(
            name="Test task",
            description="test description_1",
            deadline=date(year=2023, month=10, day=2),
            task_type=task_type,
            slug="test-task"
        )
        self.client = Client()

    def test_login_required_task_list(self):
        response = self.client.get(TASK_LIST_URL)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, "/accounts/login/?next=/tasks/")

    def test_login_required_task_detail(self):
        task_detail = Task.objects.get(pk=1)
        response = self.client.get(
            reverse("task_manager:task-detail", kwargs={"slug": task_detail.slug})
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, "/accounts/login/?next=/tasks/test-task/")

    def test_login_required_creation_task_form(self):
        response = self.client.get(reverse("task_manager:task-create"))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, "/accounts/login/?next=/tasks/create/")


class PrivateTaskTest(TestCase):
    def setUp(self) -> None:
        task_type = TaskType.objects.create(name="Test type")
        position = Position.objects.create(name="test position_1")
        for task_id in range(8):
            Task.objects.create(
                name=f"Test task_{task_id}",
                description="test description",
                deadline=date(year=2323, month=10, day=10),
                task_type=task_type,
                priority="High priority",
                slug=f"test-task_{task_id}"
            )
        get_user_model().objects.create_user(
            username="test_worker_1",
            password="test Password123",
            position=position,
            slug="test_worker_1"
        )
        get_user_model().objects.create_user(
            username="test_worker_2",
            password="test Password123",
            position=position,
            slug="test_worker_2"
        )

        self.user = get_user_model().objects.get(username="test_worker_1")
        self.client.force_login(self.user)

    def test_tasks_pagination_is_five(self):
        response = self.client.get(TASK_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["task_list"]), 5)
        self.assertTemplateUsed(response, "task_manager/task_list.html")

    def test_tasks_pagination_save_search_value_on_next_page(self):
        response = self.client.get(TASK_LIST_URL + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["task_list"]), 3)
        self.assertTemplateUsed(response, "task_manager/task_list.html")

    def test_retrieve_task_detail(self):
        task_detail = Task.objects.get(pk=1)
        response = self.client.get(
            reverse("task_manager:task-detail", kwargs={"slug": "test-task_0"})
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_manager/task_detail.html")

    def test_toggle_assign_to_task(self):
        new_task = Task.objects.get(pk=5)
        test_worker = get_user_model().objects.get(pk=2)
        new_task.assignees.set([test_worker])
        response = self.client.get(reverse(
            "task_manager:task-detail",
            kwargs={"slug": new_task.slug}
        ))

        self.assertEqual(new_task.assignees.count(), 1)
        self.assertNotContains(response, "Delete me from this project")
        self.assertContains(response, "Assign me to this project")

        self.user.tasks.add(new_task)
        response = self.client.get(reverse(
            "task_manager:task-detail", kwargs={"slug": new_task.slug}
        ))

        self.assertEqual(new_task.assignees.count(), 2)
        self.assertContains(response, "Delete me from this project")
        self.assertNotContains(response, "Assign me to this project")

    def test_create_task(self):
        task_type = TaskType.objects.get(pk=1)
        worker = get_user_model().objects.get(pk=1)
        response = self.client.post(
            reverse("task_manager:task-create"),
            {
                "name": "Task Test",
                "description": "test description",
                "task_type": task_type.id,
                "deadline": date(year=2323, month=10, day=2),
                "priority": "High priority",
                "assignees": [worker.id],
                "slug": "task-test"
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Task.objects.get(id=worker.tasks.first().id).name, "Task Test"
        )

    def test_delete_task(self):
        task = Task.objects.get(name="Test task_1")
        response = self.client.post(
            reverse("task_manager:task-delete", kwargs={"slug": "test-task_1"})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=task.id).exists())

    def test_task_search_matches_found(self):
        response = self.client.get("/tasks/?search_query=Test task_1")
        searching_task = Task.objects.filter(name="Test task_1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["task_list"]),
            list(searching_task)
        )

    def test_task_search_no_matches_found(self):
        response = self.client.get("/tasks/?search_query=Fake+name")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no tasks")
