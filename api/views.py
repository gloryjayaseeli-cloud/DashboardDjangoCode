

from  myprojectdashboard import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Project, Task
from .serializers import UserSerializer, ProjectSerializer, TaskSerializer
from rest_framework.views import APIView
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from .permissions import IsAdminUser


class UserProfileView(APIView):
    """
    Provides the logged-in user's profile data, including their roles.
    """
    permission_classes = [IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)       

class GitHubLogin(APIView):
    def post(self, request):
        code = request.data.get('code')
        if not code:
            return Response(
                {"error": "Authorization code not provided"},
                status=status.HTTP_400_BAD_REQUEST
            )

        token_params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code
        }
        headers = {"Accept": "application/json"}
        token_response = requests.post(
            "https://github.com/login/oauth/access_token",
            params=token_params,
            headers=headers
        )

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return Response({"error": "Failed to obtain access token"}, status=status.HTTP_400_BAD_REQUEST)

        user_headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        user_response = requests.get("https://api.github.com/user", headers=user_headers)
        user_data = user_response.json()
        
       
        email_response = requests.get("https://api.github.com/user/emails", headers=user_headers)
        emails = email_response.json()
        if not email_response.ok:

         error_details = email_response.json()
         return Response(
        {"error": "Failed to fetch emails from GitHub.", "details": error_details.get("message")},
        status=status.HTTP_400_BAD_REQUEST
         )


        
        primary_email = next((email['email'] for email in emails if email['primary']), None)
        
        if not primary_email:
            return Response({"error": "GitHub email not found or not public"}, status=status.HTTP_400_BAD_REQUEST)

     
        try:
            user = User.objects.get(email=primary_email)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=user_data.get('login'),
                email=primary_email,
                first_name=user_data.get('name', '').split(' ')[0]
              
            )
            user.save()
            
        # 4. Generate JWTs for the user
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh_token': str(refresh),
            'access_token': str(refresh.access_token),
        })

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    profile_data = request.data.get('profile', {'role': 'member'})
    user_data = {
        'username': request.data.get('username'),
        'email': request.data.get('email'),
        'password': request.data.get('password'),
        'profile': profile_data
    }
    serializer = UserSerializer(data=user_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])

def user_list(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail_me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)



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
#     """
#     Retrieve, update or delete a task instance based on its ID.
#     The user must be the owner of the task to modify it.
#     """

#     try:
     
#         Project.objects.get(pk=project_pk, owner=request.user)
#     except Project.DoesNotExist:
#         return Response({'error': 'Project not found.'}, status=status.HTTP_404_NOT_FOUND)
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
        
    try:
        task = Task.objects.get(pk=task_pk, project__pk=project_pk, owner=request.user)
    except Task.DoesNotExist:
        return Response({'error': 'Task not found or you do not have permission.'}, status=status.HTTP_404_NOT_FOUND)

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
        return Response({'message': 'task is deleted successfully.'},status=status.HTTP_200_OK)
