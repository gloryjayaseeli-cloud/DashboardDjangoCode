
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from .ProjectModal import Project



class Task(models.Model):
    """
    Represents a task with a status and its own owner.
    """
    STATUS_CHOICES = (
        ('not_started', 'Not Started'),
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('blocked', 'Blocked'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    description = models.TextField()
    due_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.description[:50]
