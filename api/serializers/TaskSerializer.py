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
    def create(self, validated_data):
        """
        Override the create method to inject the project
        from the view's context.
        """
        project = self.context['project']

        user = self.context['request'].user

        validated_data['project'] = project
        
        if 'owner' not in validated_data:
            validated_data['owner'] = user

        return Task.objects.create(**validated_data)