



from  myprojectdashboard import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from ..models import Project, Task
from ..serializers.TaskSerializer import  TaskSerializer
from rest_framework.views import APIView
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from ..permissions import IsAdminUser
from django.contrib.auth import get_user_model

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_list_create(request, project_pk):
    """
    List all tasks for a given project, or create a new task for that project.
    """
    try:
       
            project = Project.objects.get(pk=project_pk)

    
            is_admin = request.user.is_staff
            is_project_owner = (project.owner == request.user)

            if not (is_admin or is_project_owner):
       
             return Response(
            {'detail': 'You do not have permission to access this project.'},
            status=status.HTTP_403_FORBIDDEN
            )

    except Project.DoesNotExist:
        return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
    

    if request.method == 'GET':
        tasks = Task.objects.filter(project=project)
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
          
            serializer.save(project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def task_detail_update_delete(request, project_pk, task_pk):
    """
    Retrieve, update or delete a task instance.
    The user must be the project owner OR an admin to modify it.
    """
    try:
        project = Project.objects.get(pk=project_pk)
        task = Task.objects.get(pk=task_pk, project=project)
    except (Project.DoesNotExist, Task.DoesNotExist):
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    is_admin = request.user.is_staff
    is_project_owner = (project.owner == request.user)

    if not (is_admin or is_project_owner):
        return Response(
            {'detail': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN
        )
        
   
    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        task.delete()
        return Response({'message': 'Task deleted successfully.'}, status=status.HTTP_200_OK)
    
