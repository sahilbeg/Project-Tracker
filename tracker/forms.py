from django import forms
from .models import Project
from django.contrib.auth.models import User

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'owner']
        
    # Custom validation for owner field if needed
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # You can limit the users who can be selected as owners if needed
        self.fields['owner'].queryset = User.objects.all()  # You can customize the queryset based on your requirements

        
class ProjectAdminForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'owner']  # Define the fields you want in the form

    # Optionally, you can add custom validation or form logic here
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 5:
            raise forms.ValidationError("Project name must be at least 5 characters long.")
        return name