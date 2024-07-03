from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from task_manager.models import TaskType


TASK_TYPE_LIST_URL = reverse("task_manager:task-type-list")


class PublicTaskTypeTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_task_type_list_login_required(self):
        response = self.client.get(TASK_TYPE_LIST_URL)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, "/accounts/login/?next=/task_types/")


class PrivateTaskTypeTest(TestCase):
    def setUp(self) -> None:
        for task_type_id in range(8):
            TaskType.objects.create(name=f"Test {task_type_id}")
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test password",
            slug="test"
        )
        self.client.force_login(self.user)

    def test_task_type_pagination_is_five(self):
        response = self.client.get(TASK_TYPE_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["tasktype_list"]), 5)
        self.assertTemplateUsed(response, "task_manager/task_type_list.html")

    def test_task_type_pagination_second_page(self):
        response = self.client.get(TASK_TYPE_LIST_URL + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["tasktype_list"]), 3)
        self.assertTemplateUsed(response, "task_manager/task_type_list.html")

    def test_create_task_type(self):
        form_data = {
            "name": "test new_task_type"
        }
        response = self.client.post(
            reverse("task_manager:task-type-create"),
            data=form_data
        )
        task_type = TaskType.objects.get(name=form_data["name"])

        self.assertEqual(task_type.name, form_data["name"])
        self.assertRedirects(response, "/task_types/")

    def test_delete_task_type(self):
        task_type = TaskType.objects.get(pk=1)
        response = self.client.post(
            reverse("task_manager:task-type-delete", kwargs={"pk": task_type.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            TaskType.objects.filter(pk=task_type.id).exists()
        )

    def test_task_type_search_matches_found(self):
        response = self.client.get("/task_types/?name=Test+1")
        searching_manufacturer = TaskType.objects.filter(name="Test 1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["tasktype_list"]),
            list(searching_manufacturer)
        )

    def test_task_type_search_no_matches_found(self):
        response = self.client.get("/task_types/?name=Fake+name")
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "There are no types"
        )

    def test_pagination_task_type_search_with_value_current_page(self):
        response = self.client.get("/task_types/?name=Test")
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["tasktype_list"]), 5)

    def test_pagination_task_type_search_with_value_next_page(self):
        response = self.client.get("/task_types/?name=Test&page=2")
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["tasktype_list"]), 3)
