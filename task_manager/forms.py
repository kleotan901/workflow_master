import datetime

from django.contrib.auth import get_user_model
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils.text import slugify

from task_manager.models import Task, Worker, Tag


class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.CheckboxSelectMultiple,
    )
    deadline = forms.DateTimeField(widget=forms.DateInput(attrs={"type": "date"}))
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(), widget=forms.CheckboxSelectMultiple, required=False
    )
    slug = forms.SlugField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Task
        fields = (
            "name",
            "description",
            "deadline",
            "is_completed",
            "priority",
            "task_type",
            "assignees",
            "tags",
            "slug",
        )

    def clean(self):
        cleaned_data = super().clean()
        deadline = cleaned_data.get("deadline")
        is_completed = cleaned_data.get("is_completed")
        if deadline.date() < datetime.date.today() and not is_completed:
            raise ValidationError("Deadline cannot be in the past!")

        name = cleaned_data.get("name")
        if name:
            slug = slugify(name)
            cleaned_data["slug"] = slug

        return cleaned_data


class WorkerCreationForm(UserCreationForm):
    slug = forms.SlugField(required=False, widget=forms.HiddenInput())

    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + (
            "position",
            "first_name",
            "last_name",
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.username)
        if commit:
            instance.save()
        return instance


class WorkerUpdateForm(forms.ModelForm):
    slug = forms.SlugField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Worker
        fields = (
            "username",
            "position",
            "first_name",
            "last_name",
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.username)
        if commit:
            instance.save()
        return instance


class TaskSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search task..."}),
    )

    def search(self, queryset):
        search_query = self.cleaned_data.get("search_query")
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | Q(tags__name__icontains=search_query)
            )
        return queryset


class WorkerSearchForm(forms.Form):
    search_query = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search worker..."}),
    )

    def search(self, queryset):
        search_query = self.cleaned_data.get("search_query")
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query)
                | Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
            )
        return queryset


class PositionSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search position..."}),
    )


class TaskTypeSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search type..."}),
    )


class TagSearchForm(forms.Form):
    name = forms.CharField(
        max_length=255,
        required=False,
        label="",
        widget=forms.TextInput(attrs={"placeholder": "Search tag..."}),
    )
