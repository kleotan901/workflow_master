from datetime import date

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.test import TestCase
from django.urls import reverse

from task_manager.forms import WorkerCreationForm, TaskSearchForm, WorkerSearchForm, TaskForm
from task_manager.models import Worker, Task, Position, TaskType, Tag


class WorkerFormTest(TestCase):
    def setUp(self) -> None:
        position = Position.objects.create(name="test position")
        get_user_model().objects.create_user(
            username="TEST_user",
            password="test_Password123",
            first_name="test first_name",
            last_name="test last_name",
            position=position
        )
        self.user = get_user_model().objects.get(pk=1)
        self.client.force_login(self.user)

    def test_worker_creation_form_is_valid(self):
        position = Position.objects.create(name="test Position")
        form_data = {
            "username": "test_user1",
            "first_name": "Test first",
            "last_name": "Test last",
            "password1": "Test password123",
            "password2": "Test password123",
            "position": position,
        }
        form = WorkerCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data, form_data)

    def test_worker_search_form(self):
        search_form_last_name = WorkerSearchForm(data={"search_query": "last"})
        search_form_first_name = WorkerSearchForm(data={"search_query": "first"})
        search_form_username = WorkerSearchForm(data={"search_query": "first"})
        self.assertTrue(search_form_last_name.is_valid())
        self.assertTrue(search_form_first_name.is_valid())
        self.assertTrue(search_form_username.is_valid())

        worker = Worker.objects.get(username="TEST_user")
        queryset = Worker.objects.filter(
            Q(username__icontains="test") |
            Q(first_name__icontains="first") |
            Q(last_name__icontains="last")
        )

        self.assertIn(worker, search_form_last_name.search(queryset))
        self.assertIn(worker, search_form_first_name.search(queryset))
        self.assertIn(worker, search_form_username.search(queryset))


class TaskFormTest(TestCase):
    def setUp(self) -> None:
        position = Position.objects.create(name="test position")
        task_type = TaskType.objects.create(name="test type")
        Tag.objects.create(name="test tag")
        Task.objects.create(
            name="Test task_1",
            description="test description",
            deadline=date(year=2023, month=10, day=10),
            task_type=task_type,
        )
        get_user_model().objects.create_user(
            username="TeST_22!!",
            password="test_Password123",
            first_name="test first_name",
            last_name="test last_name",
            position=position
        )
        self.user = get_user_model().objects.create_user(
            username="test",
            password="test password"
        )
        self.client.force_login(self.user)

    def test_template_task_form(self):
        response = self.client.get(reverse("task_manager:task-create"))
        self.assertTrue(response.status_code, 200)
        self.assertTemplateUsed(response, "task_manager/task_form.html")

    def test_task_form_checkbox_select_multiple_widget(self):
        response = self.client.get(reverse("task_manager:task-create"))
        form = response.context["form"]
        self.assertIsInstance(
            form.fields["assignees"].widget,
            forms.CheckboxSelectMultiple
        )
        self.assertIsInstance(
            form.fields["tags"].widget,
            forms.CheckboxSelectMultiple
        )

    def test_tags_is_not_required(self):
        response = self.client.get(reverse("task_manager:task-create"))
        form = response.context["form"]
        self.assertFalse(form.fields["tags"].required)

    def test_task_search_form(self):
        search_form_tag = TaskSearchForm(data={"search_query": "Tag"})
        search_form_task_name = TaskSearchForm(data={"search_query": "task_1"})
        self.assertTrue(search_form_tag.is_valid())
        self.assertTrue(search_form_task_name.is_valid())
        tag = Tag.objects.get(name="test tag")
        test_task = Task.objects.get(pk=1)
        test_task.tags.set([tag])
        queryset = Task.objects.filter(
            Q(name__icontains="test") |
            Q(tags__name__icontains="Tag")
        )

        self.assertIn(test_task, search_form_tag.search(queryset))
        self.assertIn(test_task, search_form_task_name.search(queryset))

    def test_task_form_is_valid(self):
        task_type = TaskType.objects.get(pk=1)
        worker = get_user_model().objects.get(pk=1)
        form_data = {
            "name": "test_task_1",
            "description": "Test description",
            "deadline": date(year=2023, month=10, day=10),
            "priority": "High priority",
            "task_type": task_type,
            "assignees": [worker]
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(list(form.cleaned_data["assignees"]),  form_data["assignees"])
        self.assertEqual(form.cleaned_data["name"], form_data["name"])
        self.assertEqual(form.cleaned_data["description"], form_data["description"])
        self.assertEqual(form.cleaned_data["deadline"].date(), form_data["deadline"])

    def test_clean_deadline_in_past(self):
        form = TaskForm(data={
            "deadline": date(year=2020, month=3, day=2),
            "is_completed": False
        })
        self.assertFalse(form.is_valid())

        with self.assertRaises(ValidationError) as error_message:
            form.clean()
        self.assertEqual(
            error_message.exception.messages,
            ["Deadline cannot be in the past!"]
        )

    def test_task_form_updates_task_with_completed_true_when_deadline_in_past(self):
        task_type = TaskType.objects.get(pk=1)
        worker = get_user_model().objects.get(pk=1)
        form_data = {
            "name": "test_task_1",
            "description": "Test description",
            "deadline": date(year=2020, month=3, day=2),
            "is_completed": True,
            "priority": "High priority",
            "task_type": task_type,
            "assignees": [worker]
        }
        form = TaskForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        task = Task.objects.get(name="test_task_1")
        self.assertEqual(
            task.is_completed, form.cleaned_data.get("is_completed")
        )
