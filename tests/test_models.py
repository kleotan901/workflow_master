from django.contrib.auth import get_user_model
from django.test import TestCase

from task_manager.models import Position, TaskType, Task


class ModelsTest(TestCase):
    def test_position_str(self):
        position = Position.objects.create(name="Test Position")
        self.assertEqual(str(position), position.name)

    def test_worker_str(self):
        position = Position.objects.create(name="Test Position")
        worker = get_user_model().objects.create_user(
            username="Test username",
            position=position
        )
        self.assertEqual(
            str(worker),
            f"{worker.username} ({worker.position})"
        )

    def test_task_str(self):
        task_type = TaskType.objects.create(name="test Type")
        task = Task.objects.create(
            name="Test task",
            description="test description",
            deadline="2023-10-10 10:10",
            task_type=task_type
        )
        self.assertEqual(str(task), f"{task.name} {task.deadline}")
