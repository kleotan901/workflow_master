from datetime import date

from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render

from .forms import TaskForm, WorkerCreationForm
from .models import Position, Worker, Task


def index(request):
    """View function for the home page of the site."""

    num_workers = Worker.objects.count()
    num_positions = Position.objects.count()
    num_tasks = Task.objects.count()

    context = {
        "num_workers": num_workers,
        "num_positions": num_positions,
        "num_tasks": num_tasks,
    }

    return render(request, "task_manager/index.html", context=context)


class TaskListView(generic.ListView):
    model = Task
    ordering = ["name"]
    paginate_by = 5
    queryset = Task.objects.all().prefetch_related("assignees", "task_type")

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        context["today"] = date.today()
        return context


class TaskCreateView(generic.CreateView):
    model = Task
    form_class = TaskForm


class TaskUpdateView(generic.UpdateView):
    model = Task
    form_class = TaskForm


class TaskDeleteView(generic.DeleteView):
    model = Task
    success_url = reverse_lazy("task_manager:task-list")



class TaskDetailView(generic.DetailView):
    model = Task

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        context["today"] = date.today()
        return context


class WorkerListView(generic.ListView):
    model = Worker
    ordering = ["last_name"]
    paginate_by = 5
    queryset = Worker.objects.prefetch_related("position")


class WorkerCreateView(generic.CreateView):
    model = Worker
    form_class = WorkerCreationForm


class WorkerDetailView(generic.DetailView):
    model = Worker


class PositionListView(generic.ListView):
    model = Position
    ordering = ["name"]
    paginate_by = 5
    queryset = Position.objects.prefetch_related("worker_set")


class PositionCreateView(generic.CreateView):
    model = Position
    fields = "__all__"
    success_url = reverse_lazy("task_manager:position-list")


class PositionUpdateView(generic.UpdateView):
    model = Position
    fields = "__all__"
    success_url = reverse_lazy("task_manager:position-list")


class PositionDeleteView(generic.DeleteView):
    model = Position
    success_url = reverse_lazy("task_manager:position-list")
