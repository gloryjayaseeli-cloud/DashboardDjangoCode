



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


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def project_list_create(request):
    """
    List all projects for the authenticated user, or create a new one.
    """
    if request.method == 'GET':
      
        if request.user.is_staff:
           
            projects = Project.objects.all()
        else:
            
            projects = Project.objects.filter(owner=request.user)
        
        
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
           
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def project_detail_update_delete(request, pk):
    """
    Retrieve, update or delete a project instance based on its ID.
    The user must be the owner of the project.
    """
    try:
      
        project = Project.objects.get(pk=pk)
        print("project",project,request.user.is_staff or project.owner == request.user,request.user.is_staff , project.owner == request.user)

        if not (request.user.is_staff or project.owner == request.user):
          
            return Response(
                {"detail": "You do not have permission to view this project."},
                status=status.HTTP_403_FORBIDDEN
            )

    except Project.DoesNotExist:
       
        return Response(
            {"detail": "Not found."},
            status=status.HTTP_404_NOT_FOUND
        )
    if request.method == 'GET':
        serializer = ProjectSerializer(project)
        return Response({"data":serializer.data})

    elif request.method == 'PUT':
        serializer = ProjectSerializer(project, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
    elif request.method == 'DELETE': 
           if not request.user.is_staff:
            return Response({'error': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

          
           project.delete()
           return Response({'message': 'Project deleted successfully.'}, status=status.HTTP_200_OK)

