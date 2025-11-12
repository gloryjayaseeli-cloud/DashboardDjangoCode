



from  myprojectdashboard import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from ..models import Project, Task
from ..serializers.ProjectSerializer import  ProjectSerializer
from rest_framework.views import APIView
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from ..permissions import IsAdminUser
from django.contrib.auth import get_user_model
from django.db.models import Q

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def project_list_create(request):
    """
    List all projects based on user group, or create a new one.
    - Admins see all projects.
    - TaskCreators see projects they own OR projects where they have a task.
    - Viewers see projects where they are assigned to a task.
    """
    
    if request.method == 'GET':
        user = request.user

        if user.groups.filter(name='Admin').exists():
            projects = Project.objects.all()
        
        elif user.groups.filter(name='TaskCreator').exists():
            projects = Project.objects.filter(
                Q(owner=user) | Q(tasks__owner=user)
            ).distinct()
        
        elif user.groups.filter(name='Viewer').exists():
            projects = Project.objects.filter(tasks__owner=user).distinct()
        
        else:
            projects = Project.objects.none()

        serializer = ProjectSerializer(projects, many=True, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'POST':
        user = request.user 
        is_admin = user.groups.filter(name='Admin').exists()
        is_task_creator = user.groups.filter(name='TaskCreator').exists()
        
        if not (is_admin or is_task_creator):
            return Response(
                {'error': 'You do not have permission to create projects.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer_context = {'request': request}
        serializer = ProjectSerializer(data=request.data, context=serializer_context)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        owner_to_be = None

        if is_admin:
            owner_to_be = serializer.validated_data.get('owner', user)
        
        elif is_task_creator:
            owner_to_be = user

        
        is_owner_admin = owner_to_be.groups.filter(name='Admin').exists()
        is_owner_task_creator = owner_to_be.groups.filter(name='TaskCreator').exists()

        if not (is_owner_admin or is_owner_task_creator):
            return Response(
                {'error': 'Only Admin or TaskCreator can be the owner of a project.'}, 
                status=status.HTTP_400_BAD_REQUEST 
            )
        
        serializer.save(owner=owner_to_be)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def project_detail_update_delete(request, pk):
    """
    Retrieve, update or delete a project instance based on its ID.
    Permissions are based on user groups (Admin, TaskCreator, Viewer).
    """
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response(
            {"detail": "Not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    user = request.user
    
    is_admin = user.groups.filter(name='Admin').exists()
    is_task_creator = user.groups.filter(name='TaskCreator').exists()
    is_viewer = user.groups.filter(name='Viewer').exists()

    if request.method == 'GET':
        can_view = False
        
        if is_admin:
            can_view = True
        elif is_task_creator:
            if project.owner == user or project.tasks.filter(owner=user).exists():
                can_view = True
        elif is_viewer:
            if project.tasks.filter(owner=user).exists():
                can_view = True

        if not can_view:
            return Response(
                {"detail": "You do not have permission to view this project."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ProjectSerializer(project, context={'request': request})
        return Response({"data": serializer.data}) 

    elif request.method == 'PUT':
        
        can_initiate_update = False
        if is_admin:
            can_initiate_update = True
        elif is_task_creator and project.owner == user:
            can_initiate_update = True

        if not can_initiate_update:
            return Response(
                {"detail": "You do not have permission to update this project."},
                status=status.HTTP_403_FORBIDDEN  
            )

        serializer_context = {'request': request}
        serializer = ProjectSerializer(
            project, 
            data=request.data, 
            partial=True, 
            context=serializer_context
        )
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        final_owner = project.owner
        new_owner_from_request = serializer.validated_data.get('owner')

        if new_owner_from_request:
            if is_admin:
                final_owner = new_owner_from_request
            elif is_task_creator and new_owner_from_request != user:
                return Response(
                    {'error': 'You do not have permission to change the project owner.'}, 
                    status=status.HTTP_403_FORBIDDEN
                )
            elif is_task_creator:
                final_owner = user
            
        is_owner_admin = final_owner.groups.filter(name='Admin').exists()
        is_owner_task_creator = final_owner.groups.filter(name='TaskCreator').exists()

        if not (is_owner_admin or is_owner_task_creator):
            return Response(
                {'error': 'Only Admin or TaskCreator can be the owner of a project.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer.save(owner=final_owner)
        return Response(serializer.data)
    
    elif request.method == 'DELETE':
        if not is_admin:
            return Response(
                {'error': 'You do not have permission to perform this action.'}, 
                status=status.HTTP_403_FORBIDDEN
            )

        project.delete()
        return Response(
            {'message': 'Project deleted successfully.'}, 
            status=status.HTTP_200_OK
        )