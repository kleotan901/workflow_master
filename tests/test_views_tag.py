from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from task_manager.models import Tag


TAG_TYPE_LIST_URL = reverse("task_manager:tag-list")


class PublicTagTest(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    def test_task_type_list_login_required(self):
        response = self.client.get(TAG_TYPE_LIST_URL)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, "/accounts/login/?next=/tags/")


class PrivateTagTest(TestCase):
    def setUp(self) -> None:
        for tag_id in range(8):
            Tag.objects.create(name=f"Test {tag_id}")
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test password",
            slug="test"
        )
        self.client.force_login(self.user)

    def test_tag_pagination_is_five(self):
        response = self.client.get(TAG_TYPE_LIST_URL)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["tag_list"]), 5)
        self.assertTemplateUsed(response, "task_manager/tag_list.html")

    def test_tag_pagination_second_page(self):
        response = self.client.get(TAG_TYPE_LIST_URL + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["tag_list"]), 3)
        self.assertTemplateUsed(response, "task_manager/tag_list.html")

    def test_create_tag(self):
        form_data = {
            "name": "test new_tag"
        }
        response = self.client.post(
            reverse("task_manager:tag-create"),
            data=form_data
        )
        task_type = Tag.objects.get(name=form_data["name"])

        self.assertEqual(task_type.name, form_data["name"])
        self.assertRedirects(response, "/tags/")

    def test_delete_tag(self):
        tag = Tag.objects.get(pk=1)
        response = self.client.post(
            reverse("task_manager:tag-delete", kwargs={"pk": tag.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            Tag.objects.filter(pk=tag.id).exists()
        )

    def test_tag_search_matches_found(self):
        response = self.client.get("/tags/?name=Test+1")
        searching_manufacturer = Tag.objects.filter(name="Test 1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            list(response.context["tag_list"]),
            list(searching_manufacturer)
        )

    def test_tag_search_no_matches_found(self):
        response = self.client.get("/tags/?name=Fake+name")
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "There are no tags"
        )

    def test_pagination_tag_search_with_value_current_page(self):
        response = self.client.get("/tags/?name=Test")
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["tag_list"]), 5)

    def test_pagination_tag_search_with_value_next_page(self):
        response = self.client.get("/tags/?name=Test&page=2")
        self.assertTrue(response.context["is_paginated"] is True)
        self.assertEqual(len(response.context["tag_list"]), 3)
