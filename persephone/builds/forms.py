from django import forms

from builds.models import Project


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
