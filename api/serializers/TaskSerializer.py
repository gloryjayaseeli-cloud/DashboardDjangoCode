from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Project, Task, UserProfile

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the updated Task model.
    """
       
    owner = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )
    
    class Meta:
        model = Task
        fields = ['id', 'project', 'description', 'due_date', 'status', 'owner']
        read_only_fields = ['project']
