

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver



class UserProfile(models.Model):
    """
    Extends the default User model to include a role.
    """
    ROLE_CHOICES = (
        ('member', 'Member'),
        ('admin', 'Admin'),
        ('guest', 'Guest'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')

    def __str__(self):
        return f"{self.user.username}'s Profile"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()



class Project(models.Model):
    """
    Represents a project with a start and end date.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

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
