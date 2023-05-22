from datetime import date

from django.views import generic
from django.shortcuts import render

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = date.today()
        return context


class TaskDetailView(generic.DetailView):
    model = Task
    #queryset = Task.objects.all().prefetch_related("tasks__type")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["today"] = date.today()
        return context


class WorkerListView(generic.ListView):
    model = Worker
    ordering = ["last_name"]
    paginate_by = 5


class PositionListView(generic.ListView):
    model = Position
    ordering = ["name"]
    paginate_by = 5
