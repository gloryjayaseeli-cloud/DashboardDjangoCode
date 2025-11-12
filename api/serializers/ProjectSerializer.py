from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Project, Task, UserProfile
from .TaskSerializer import TaskSerializer

class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.
    'tasks' are now filtered based on the request user's role.
    """
    
    tasks = serializers.SerializerMethodField()
    
    owner = serializers.SlugRelatedField(
        slug_field='username',   
        queryset=User.objects.all()
    )

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'owner', 'tasks']

    
    def get_tasks(self, project):
        """
        This method is called by the 'tasks' SerializerMethodField.
        It filters the tasks based on the user's role.
        'project' is the project instance being serialized.
        """
        
        request = self.context.get('request')
        
        if not request or not request.user:
            return [] 
        user = request.user
     
        all_tasks = project.tasks.all()

        if user.groups.filter(name='Admin').exists() or project.owner == user:
            tasks_to_serialize = all_tasks
        
        elif user.groups.filter(name='TaskCreator').exists() or user.groups.filter(name='Viewer').exists():
            tasks_to_serialize = all_tasks.filter(owner=user)
            
        else:
            tasks_to_serialize = all_tasks.none()

        return TaskSerializer(tasks_to_serialize, many=True, context=self.context).data
