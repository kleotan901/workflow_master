from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render

from .forms import (
    TaskForm,
    WorkerCreationForm,
    WorkerUpdateForm,
    TaskSearchForm,
    WorkerSearchForm,
    PositionSearchForm,
)
from .models import Position, Worker, Task


@login_required
def index(request):
    """View function for the home page of the site."""

    num_workers = Worker.objects.count()
    num_positions = Position.objects.count()
    num_tasks = Task.objects.count()
    tasks_in_work = Task.objects.filter(is_completed=False)
    completed_tasks = Task.objects.filter(is_completed=True)

    context = {
        "num_workers": num_workers,
        "num_positions": num_positions,
        "num_tasks": num_tasks,
        "tasks_in_work": tasks_in_work.count(),
        "completed_tasks": completed_tasks.count()
    }

    return render(request, "task_manager/index.html", context=context)


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    ordering = ["name"]
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        context["today"] = date.today()
        context["search_form"] = TaskSearchForm(initial={
            "name": self.request.GET.get("name", "")
        })
        return context

    def get_queryset(self):
        queryset = Task.objects.all().prefetch_related("assignees", "task_type")
        form = TaskSearchForm(self.request.GET)
        if form.is_valid():
            return form.search(queryset)
        return queryset


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Task
    form_class = TaskForm


class TaskDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Task
    success_url = reverse_lazy("task_manager:task-list")



class TaskDetailView(LoginRequiredMixin, generic.DetailView):
    model = Task

    def get_context_data(self, **kwargs):
        context = super(TaskDetailView, self).get_context_data(**kwargs)
        context["today"] = date.today()
        return context


class WorkerListView(LoginRequiredMixin, generic.ListView):
    model = Worker
    ordering = ["last_name"]
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(WorkerListView, self).get_context_data(**kwargs)
        number_tasks_in_work = Task.objects.filter(is_completed=False)
        context["number_tasks_in_work"] = number_tasks_in_work
        dict_workers_with_tasks_in_work = {}
        for task in number_tasks_in_work:
            for worker in task.assignees.all():
                if worker in dict_workers_with_tasks_in_work:
                    dict_workers_with_tasks_in_work[worker] += 1
                else:
                    dict_workers_with_tasks_in_work[worker] = 1
        context["dict_workers_with_tasks_in_work"] = dict_workers_with_tasks_in_work
        context["search_form"] = WorkerSearchForm(initial={
            "search_query": self.request.GET.get("search_query", "")

        })
        return context

    def get_queryset(self):
        queryset = Worker.objects.prefetch_related("position")
        form = WorkerSearchForm(self.request.GET)
        if form.is_valid():
            return form.search(queryset)
        return queryset


class WorkerDetailView(LoginRequiredMixin, generic.DetailView):
    model = Worker

    def get_context_data(self, **kwargs):
        context = super(WorkerDetailView, self).get_context_data(**kwargs)
        worker = self.get_object()
        completed_tasks = worker.tasks.filter(is_completed=True)
        tasks_in_work = worker.tasks.filter(is_completed=False)
        context["completed_tasks"] = completed_tasks
        context["tasks_in_work"] = tasks_in_work
        return context


class WorkerCreateView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    form_class = WorkerCreationForm

class WorkerUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    form_class = WorkerUpdateForm


class WorkerDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Worker
    success_url = reverse_lazy("task_manager:worker-list")


class PositionListView(LoginRequiredMixin, generic.ListView):
    model = Position
    ordering = ["name"]
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(PositionListView, self).get_context_data(**kwargs)
        context["search_form"] = PositionSearchForm(initial={
            "name": self.request.GET.get("name", "")
        })
        return context

    def get_queryset(self):
        queryset = Position.objects.prefetch_related("worker_set")
        form = PositionSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                name__icontains=form.cleaned_data["name"],
            )
        return queryset


class PositionCreateView(LoginRequiredMixin, generic.CreateView):
    model = Position
    fields = "__all__"
    success_url = reverse_lazy("task_manager:position-list")


class PositionUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Position
    fields = "__all__"
    success_url = reverse_lazy("task_manager:position-list")


class PositionDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Position
    success_url = reverse_lazy("task_manager:position-list")


@login_required
def toggle_assign_to_task(request, pk):
    worker = Worker.objects.get(id=request.user.id)
    if (
        Task.objects.get(id=pk) in worker.tasks.all()
    ):
        worker.tasks.remove(pk)
    else:
        worker.tasks.add(pk)
    return HttpResponseRedirect(reverse_lazy("task_manager:task-detail", args=[pk]))
