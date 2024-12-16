from django import forms
from django.contrib.auth.models import User
from .models import Account  # Keep this import because it does not cause a circular dependency

# Account Form for standard form usage
class AccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'description', 'owner']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].queryset = User.objects.all()


# Account Admin Form for custom validation logic in the admin panel
class AccountAdminForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['name', 'description', 'owner']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 5:
            raise forms.ValidationError("Account name must be at least 5 characters long.")
        return name


# Project Form for creating or editing projects
class ProjectForm(forms.ModelForm):
    class Meta:
        model = None  # Temporary placeholder

    def __init__(self, *args, **kwargs):
        from .models import Project  # Import the model locally to avoid circular import
        self.Meta.model = Project  # Set the model dynamically
        super().__init__(*args, **kwargs)
        self.fields['participants'].queryset = User.objects.all()
