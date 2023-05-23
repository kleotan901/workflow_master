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
    TaskUpdateView,
    TaskDeleteView,
    PositionCreateView,
    PositionDeleteView,
    PositionUpdateView,
    WorkerCreateView, WorkerUpdateView
)

urlpatterns = [
    path("", index, name="index"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/update/", TaskUpdateView.as_view(), name="task-update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path(
        "workers/create/",
        WorkerCreateView.as_view(),
        name="worker-create"
    ),
    path(
        "workers/<int:pk>/update/",
        WorkerUpdateView.as_view(),
        name="worker-update"
    ),
    path(
        "workers/<int:pk>/",
         WorkerDetailView.as_view(),
         name="worker-detail"
    ),

    path("positions/", PositionListView.as_view(), name="position-list"),
    path(
        "positions/create/",
         PositionCreateView.as_view(),
         name="position-create"
    ),
    path(
        "positions/<int:pk>/update/",
        PositionUpdateView.as_view(),
        name="position-update",
    ),
    path(
        "positions/<int:pk>/delete/",
        PositionDeleteView.as_view(),
        name="position-delete",
    ),
]

app_name = "task_manager"
