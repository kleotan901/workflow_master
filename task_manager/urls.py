from django.contrib import admin
from django.urls import path

from task_manager.views import (
    HomePage,
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
    WorkerCreateView,
    WorkerUpdateView,
    WorkerDeleteView,
    ToggleAssignToTaskView,
    RegisterWorker,
    TaskTypeListView,
    TaskTypeCreateView,
    TaskTypeUpdateView,
    TaskTypeDeleteView,
    TagListView,
    TagCreateView,
    TagUpdateView,
    TagDeleteView
)

urlpatterns = [
    path("", HomePage.as_view(), name="index"),
    path("register/", RegisterWorker.as_view(), name="register"),
    path("tasks/", TaskListView.as_view(), name="task-list"),
    path("tasks/<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
    path("tasks/create/", TaskCreateView.as_view(), name="task-create"),
    path("tasks/<int:pk>/update/", TaskUpdateView.as_view(), name="task-update"),
    path("tasks/<int:pk>/delete/", TaskDeleteView.as_view(), name="task-delete"),
    path(
        "tasks/<int:pk>/toggle-assign/",
        ToggleAssignToTaskView.as_view(),
        name="toggle-task-assign",
    ),
    path("workers/", WorkerListView.as_view(), name="worker-list"),
    path(
        "workers/<int:pk>/",
         WorkerDetailView.as_view(),
         name="worker-detail"
    ),
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
        "workers/<int:pk>/delete/",
        WorkerDeleteView.as_view(),
        name="worker-delete"
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
    path(
        "task_types/",
        TaskTypeListView.as_view(),
        name="task-type-list",
    ),
    path(
        "task_types/create/",
         TaskTypeCreateView.as_view(),
         name="task-type-create"
    ),
    path(
        "task_types/<int:pk>/update/",
        TaskTypeUpdateView.as_view(),
        name="task-type-update",
    ),
    path(
        "task_types/<int:pk>/delete/",
        TaskTypeDeleteView.as_view(),
        name="task-type-delete",
    ),
    path(
        "tags/",
        TagListView.as_view(),
        name="tag-list",
    ),
    path(
        "tags/create/",
         TagCreateView.as_view(),
         name="tag-create"
    ),
    path(
        "tags/<int:pk>/update/",
        TagUpdateView.as_view(),
        name="tag-update",
    ),
    path(
        "tags/<int:pk>/delete/",
        TagDeleteView.as_view(),
        name="tag-delete",
    ),
]

app_name = "task_manager"
