from django.contrib.auth.models import AbstractUser
from django.db import models


class Worker(AbstractUser):
    position = models.CharField(max_length=255)

    class Meta:
        verbose_name = "worker"
        verbose_name_plural = "workers"

    def __str__(self):
        return f"{self.username} ({self.first_name} {self.last_name})"


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return {self.name}


class TaskType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return {self.name}


class Task(models.Model):
    PRIORITY_CHOICES = [
        ("Urgent and important", "Urgent and important"),
        ("High priority", "High priority"),
        ("Medium priority", "Medium priority"),
        ("Low priority", "Low priority"),
    ]
    name = models.CharField(max_length=255)
    description = models.TextField()
    deadline = models.DateTimeField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    task_type = models.ForeignKey(TaskType, on_delete=models.CASCADE)
    assignees = models.ManyToManyField(Worker, related_name="tasks")

    def __str__(self):
        return f"{self.name} {self.deadline}"
