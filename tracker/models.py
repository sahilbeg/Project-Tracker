from django.db import models
from django.contrib.auth.models import User


# Account Model
class Account(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="accounts")

    def __str__(self):
        return self.name


# Project Model
class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="projects")
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="projects")
    participants = models.ManyToManyField(User, related_name="project_participants", blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['account', 'name'], name='unique_project_per_account')
        ]

    def __str__(self):
        return self.name


# Sprint Model
class Sprint(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="sprints")
    name = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['project', 'name'], name='unique_sprint_per_project')
        ]

    def __str__(self):
        return f"{self.project.name} - {self.name}"


# Task Model
class Task(models.Model):
    TO_DO = 'To Do'
    IN_PROGRESS = 'In Progress'
    COMPLETED = 'Completed'
    
    TASK_STATUS_CHOICES = [
        (TO_DO, 'To Do'),
        (IN_PROGRESS, 'In Progress'),
        (COMPLETED, 'Completed'),
    ]
    
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assigned_to = models.ManyToManyField(User)
    due_date = models.DateField()
    status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default=TO_DO)
    comments = models.TextField(blank=True)
    screenshots = models.ImageField(upload_to='task_screenshots/', blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sprint', 'title'], name='unique_task_per_sprint')
        ]

    def __str__(self):
        return f"{self.sprint.name} - {self.title}"

    def reassign_task(self, new_assignee):
        self.assigned_to = new_assignee
        self.save()

