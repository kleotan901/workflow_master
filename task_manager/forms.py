import datetime

from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import UserCreationForm

from task_manager.models import Task, Worker


class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    deadline = forms.DateTimeField(
        widget=forms.DateInput(attrs={"type": "date"}))


    class Meta:
        model = Task
        fields = "__all__"
        exclude =  ("is_completed",)

        
class WorkerCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "position",
            "first_name",
            "last_name",
        )
