from datetime import date
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.urls import reverse_lazy
from django.views import generic, View
from django.shortcuts import render, redirect, get_object_or_404

from .forms import (
    TaskForm,
    WorkerCreationForm,
    WorkerUpdateForm,
    TaskSearchForm,
    WorkerSearchForm,
    PositionSearchForm, TaskTypeSearchForm, TagSearchForm
)
from .models import Position, Worker, Task, TaskType, Tag


class RegisterWorker(generic.CreateView):
    def post(self, request, *args, **kwargs):
        form = WorkerCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("task_manager:index")
        else:
            context = {
                "form": form
            }
            return render(request, "task_manager/worker_form.html", context)

    def get(self, request, *args, **kwargs):
        return render(request, "task_manager/worker_form.html", {"form": WorkerCreationForm()})


class HomePage(LoginRequiredMixin, generic.ListView):
    template_name = "task_manager/index.html"
    queryset = Task.objects.all()
    context_object_name = "task_list"

    def get_context_data(self, **kwargs):
        context = super(HomePage, self).get_context_data(**kwargs)
        context["num_workers"] = Worker.objects.count()
        context["num_positions"] = Position.objects.count()
        context["num_tasks"] = self.queryset.count()
        context["tasks_in_work"] = Task.objects.filter(is_completed=False).count()
        context["completed_tasks"] = Task.objects.filter(is_completed=True).count()
        return context


class TaskListView(LoginRequiredMixin, generic.ListView):
    model = Task
    ordering = ["name"]
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(TaskListView, self).get_context_data(**kwargs)
        context["today"] = date.today()
        context["search_form"] = TaskSearchForm(initial={
            "search_query": self.request.GET.get("search_query", "")
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

    def form_valid(self, form):
        form.instance.creator = self.request.user
        return super().form_valid(form)


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
    template_name = "task_manager/worker_update_form.html"


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


class TaskTypeListView(LoginRequiredMixin, generic.ListView):
    model = TaskType
    template_name = "task_manager/task_type_list.html"
    ordering = ["name"]
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(TaskTypeListView, self).get_context_data(**kwargs)
        context["search_form"] = TaskTypeSearchForm(initial={
            "name": self.request.GET.get("name", "")
        })
        return context

    def get_queryset(self):
        queryset = TaskType.objects.prefetch_related("task_set")
        form = TaskTypeSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                name__icontains=form.cleaned_data["name"],
            )
        return queryset


class TaskTypeCreateView(LoginRequiredMixin, generic.CreateView):
    model = TaskType
    fields = "__all__"
    template_name = "task_manager/task_type_form.html"
    success_url = reverse_lazy("task_manager:task-type-list")


class TaskTypeUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = TaskType
    fields = "__all__"
    template_name = "task_manager/task_type_form.html"
    success_url = reverse_lazy("task_manager:task-type-list")


class TaskTypeDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = TaskType
    template_name = "task_manager/task_type_confirm_delete.html"
    success_url = reverse_lazy("task_manager:task-type-list")


class ChangeTaskStatus(generic.View):
    def post(self, request, slug):
        task = get_object_or_404(Task, slug=slug)
        task.is_completed = not task.is_completed
        task.save()
        return HttpResponseRedirect(reverse_lazy("task_manager:task-detail", args=[slug]))

    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest("Invalid request method.")


class TagListView(LoginRequiredMixin, generic.ListView):
    model = Tag
    ordering = ["name"]
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(TagListView, self).get_context_data(**kwargs)
        context["search_form"] = TagSearchForm(initial={
            "name": self.request.GET.get("name", "")
        })
        return context

    def get_queryset(self):
        queryset = Tag.objects.prefetch_related("tasks")
        form = TagSearchForm(self.request.GET)
        if form.is_valid():
            return queryset.filter(
                name__icontains=form.cleaned_data["name"],
            )
        return queryset


class TagCreateView(LoginRequiredMixin, generic.CreateView):
    model = Tag
    fields = "__all__"
    success_url = reverse_lazy("task_manager:tag-list")


class TagUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = Tag
    fields = "__all__"
    success_url = reverse_lazy("task_manager:tag-list")


class TagDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = Tag
    success_url = reverse_lazy("task_manager:tag-list")


class ToggleAssignToTaskView(LoginRequiredMixin, generic.View):
    def post(self, request, slug):
        if request.method == 'POST':
            worker = get_object_or_404(Worker, id=request.user.id)
            task = get_object_or_404(Task, slug=slug)
            if task in worker.tasks.all():
                worker.tasks.remove(task)
            else:
                worker.tasks.add(task)

            return HttpResponseRedirect(reverse_lazy("task_manager:task-detail", args=[slug]))

    def get(self, request, *args, **kwargs):
        return HttpResponseBadRequest("Invalid request method.")
