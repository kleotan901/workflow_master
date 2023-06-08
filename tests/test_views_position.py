from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from task_manager.models import Position


POSITION_LIST_URL = reverse("task_manager:position-list")


class PublicPositionTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_position_list_login_required(self):
        response = self.client.get(POSITION_LIST_URL)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, "/accounts/login/?next=/task_manager/positions/")


class PrivatePositionTest(TestCase):
    def setUp(self) -> None:
        for position_id in range(8):
            Position.objects.create(name=f"Test {position_id}")
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test password"
        )
        self.client.force_login(self.user)

    def test_position_pagination_is_five(self):
        response = self.client.get(POSITION_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["position_list"]), 5)
        self.assertTemplateUsed(response, "task_manager/position_list.html")

    def test_position_pagination_second_page(self):
        response = self.client.get(POSITION_LIST_URL + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["position_list"]), 3)
        self.assertTemplateUsed(response, "task_manager/position_list.html")

    def test_create_position(self):
        form_data = {
            "name": "test new_position"
        }
        response = self.client.post(
            reverse("task_manager:position-create"),
            data=form_data
        )
        new_position = Position.objects.get(name=form_data["name"])

        self.assertEqual(new_position.name, form_data["name"])
        self.assertRedirects(response, "/task_manager/positions/")

    def test_delete_position(self):
        position = Position.objects.get(pk=1)
        response = self.client.post(
            reverse("task_manager:position-delete", kwargs={"pk": position.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Position.objects.filter(pk=position.id).exists()
        )

    def test_position_search_matches_found(self):
        response = self.client.get("/task_manager/positions/?name=Test+1")
        searching_manufacturer = Position.objects.filter(name="Test 1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["position_list"]),
            list(searching_manufacturer)
        )

    def test_position_search_no_matches_found(self):
        response = self.client.get("/task_manager/positions/?name=Fake+name")
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "There are no positions in the company."
        )

    def test_pagination_position_search_with_value_current_page(self):
        response = self.client.get("/task_manager/positions/?name=Test")
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["position_list"]), 5)

    def test_pagination_position_search_with_value_next_page(self):
        response = self.client.get("/task_manager/positions/?name=Test&page=2")
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["position_list"]), 3)
