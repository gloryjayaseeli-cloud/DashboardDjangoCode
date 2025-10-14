from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Project, Task, UserProfile

from .TaskSerializer import TaskSerializer





class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the updated Project model.
    """
   
    tasks = TaskSerializer(many=True, read_only=True)
    # owner = serializers.ReadOnlyField(source='owner.username')
    owner = serializers.SlugRelatedField(
        slug_field='username',  
        queryset=User.objects.all()
    )

    class Meta:
        model = Project
      
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'owner', 'tasks']
