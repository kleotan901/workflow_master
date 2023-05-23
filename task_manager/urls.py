from django.contrib import admin
from django.urls import path

from task_manager.views import (
    index,
    TaskListView,
    WorkerListView,
    PositionListView,
    TaskDetailView,
    WorkerDetailView,
    TaskCreateView,
    TaskUpdateView
)

urlpatterns = [
    path("", index, name="index"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/update/", TaskUpdateView.as_view(), name="task-update"),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path("workers/<int:pk>/", WorkerDetailView.as_view(), name="worker-detail"),
    path("positions/", PositionListView.as_view(), name="position-list"),
]

app_name = "task_manager"
