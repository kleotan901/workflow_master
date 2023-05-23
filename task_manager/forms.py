import datetime

from django.contrib.auth import get_user_model
from django import forms

from task_manager.models import Task


class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    deadline = forms.DateTimeField(
        widget=forms.DateInput(attrs={'type': 'date'}))


    class Meta:
        model = Task
        fields = "__all__"
        exclude =  ('is_completed',)

