from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from task_manager.models import Position

WORKER_LIST_URL = reverse("task_manager:worker-list")


class PublicWorkerTest(TestCase):
    def setUp(self) -> None:
        position = Position.objects.create(name="test position_1")
        get_user_model().objects.create_user(
            username="test_worker_1",
            password="test Password123",
            position=position
        )

        self.client = Client()

    def test_login_required_workers(self):
        response = self.client.get(WORKER_LIST_URL)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, "/accounts/login/?next=/task_manager/workers/")

    def test_login_required_worker_detail(self):
        worker_detail = get_user_model().objects.get(pk=1)
        response = self.client.get(
            reverse("task_manager:worker-detail", kwargs={"pk": worker_detail.pk})
        )
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, "/accounts/login/?next=/task_manager/workers/1/")

    def test_login_required_creation_worker_form(self):
        response = self.client.get(reverse("task_manager:worker-create"))
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            "/accounts/login/?next=/task_manager/workers/create/"
        )


class PrivateDriverTest(TestCase):
    def setUp(self) -> None:
        position = Position.objects.create(name="test position_1")
        for user_id in range(8):
            get_user_model().objects.create_user(
                username=f"test_worker_{user_id}",
                password="test Password123",
                position=position
            )
        self.user = get_user_model().objects.get(pk=1)
        self.client.force_login(self.user)

    def test_workers_pagination_is_five(self):
        response = self.client.get(WORKER_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["worker_list"]), 5)
        self.assertTemplateUsed(response, "task_manager/worker_list.html")

    def test_workers_pagination_second_page(self):
        response = self.client.get(WORKER_LIST_URL + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["worker_list"]), 3)
        self.assertTemplateUsed(response, "task_manager/worker_list.html")

    def test_retrieve_worker_detail(self):
        worker_detail = get_user_model().objects.get(pk=1)
        response = self.client.get(
            reverse("task_manager:worker-detail", kwargs={"pk": worker_detail.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "task_manager/worker_detail.html")

    def test_worker_search_result_matches_found(self):
        response = self.client.get("/task_manager/workers/?search_query=test_worker_4")
        searching_worker = get_user_model().objects.filter(
            username="test_worker_4"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["worker_list"]),
            list(searching_worker)
        )

    def test_worker_search_no_matches_found(self):
        response = self.client.get("/task_manager/workers/?search_query=Fake+name")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no workers.")

    def test_pagination_worker_search_with_value_current_page(self):
        response = self.client.get("/task_manager/workers/?search_query=Test")
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["worker_list"]), 5)

    def test_pagination_worker_search_with_value_next_page(self):
        response = self.client.get("/task_manager/workers/?search_query=Test&page=2")
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["worker_list"]), 3)
