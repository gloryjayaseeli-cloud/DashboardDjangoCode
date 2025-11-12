



    
from myprojectdashboard import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User, Group
from ..models import Project, Task
from ..serializers.TaskSerializer import TaskSerializer
from rest_framework.views import APIView
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from ..permissions import IsAdminUser
from django.contrib.auth import get_user_model

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def task_list_create(request, project_pk):
    """
    List tasks for a project, or create a new task.
    - GET: Admins/Project Owners see all. Others see only their own tasks.
    - POST: Only Admins/Project Owners can create tasks.
    """
    try:
        project = Project.objects.get(pk=project_pk)
    except Project.DoesNotExist:
        return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    user = request.user
    
    is_admin = user.groups.filter(name='Admin').exists()
    is_project_owner = (project.owner == user)

    if request.method == 'GET':
        tasks = Task.objects.none()
        can_view_project_tasks = (
            is_admin or 
            is_project_owner or
            user.groups.filter(name__in=['TaskCreator', 'Viewer']).exists()
        )
        
        if not can_view_project_tasks:
             return Response(
                {'detail': 'You do not have permission to access these tasks.'},
                status=status.HTTP_403_FORBIDDEN
             )

        if is_admin or is_project_owner:
            tasks = Task.objects.filter(project=project)
        else:
            tasks = Task.objects.filter(project=project, owner=user)

        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not (is_admin or is_project_owner):
            return Response(
                {'detail': 'You do not have permission to create tasks for this project.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer_context = {
            'request': request,
            'project': project
        }
        
        serializer = TaskSerializer(data=request.data, context=serializer_context)
        
        if serializer.is_valid():
            serializer.save() 
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def task_detail_update_delete(request, project_pk, task_pk):
    """
    Retrieve, update or delete a task instance based on group permissions.
    - Admin: Can do anything.
    - TaskCreator (Project Owner): Can do anything.
    - TaskCreator (Task Owner only): Can GET, PUT.
    - Viewer (Task Owner only): Can GET, PUT.
    """
    try:
        project = Project.objects.get(pk=project_pk)
        task = Task.objects.get(pk=task_pk, project=project)
    except (Project.DoesNotExist, Task.DoesNotExist):
        return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

    user = request.user

    is_admin = user.groups.filter(name='Admin').exists()
    is_task_creator = user.groups.filter(name='TaskCreator').exists()
    is_viewer = user.groups.filter(name='Viewer').exists()
    
    is_project_owner = (project.owner == user)
    is_task_owner = (task.owner == user)

    if request.method == 'GET':
        can_view = False
        if is_admin:
            can_view = True
        elif is_task_creator and (is_project_owner or is_task_owner):
            can_view = True
        elif is_viewer and is_task_owner:
            can_view = True

        if not can_view:
            return Response(
                {'detail': 'You do not have permission to view this task.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method == 'PUT':
        can_update = False
        if is_admin:
            can_update = True
        elif is_task_creator and (is_project_owner or is_task_owner):
            can_update = True
        elif is_viewer and is_task_owner:
            can_update = True 

        if not can_update:
            return Response(
                {'detail': 'You do not have permission to update this task.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = TaskSerializer(task, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        can_delete = False
        if is_admin:
            can_delete = True
        elif is_task_creator and is_project_owner: 
            can_delete = True

        if not can_delete:
            return Response(
                {'detail': 'You do not have permission to delete this task.'},
                status=status.HTTP_4To03_FORBIDDEN
            )

        task.delete()
        return Response({'message': 'Task deleted successfully.'}, status=status.HTTP_200_OK)
