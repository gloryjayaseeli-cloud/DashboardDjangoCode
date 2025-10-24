


from  myprojectdashboard import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from ..models import Project, Task
from ..serializers.UserSerializer import UserSerializer
from rest_framework.views import APIView
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from ..permissions import IsAdminUser
from django.contrib.auth import get_user_model


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

        if not token_response.ok:
            return Response({"error": "Failed to obtain access token from GitHub"}, status=status.HTTP_400_BAD_REQUEST)

        token_data = token_response.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return Response({"error": "Access token not in response from GitHub"}, status=status.HTTP_400_BAD_REQUEST)

        user_headers = {
            "Authorization": f"token {access_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        user_response = requests.get("https://api.github.com/user", headers=user_headers)
        if not user_response.ok:
            return Response({"error": "Failed to fetch user data from GitHub"}, status=status.HTTP_400_BAD_REQUEST)
        
        user_data = user_response.json()
        
        email_response = requests.get("https://api.github.com/user/emails", headers=user_headers)
        if not email_response.ok:
            return Response({"error": "Failed to fetch emails from GitHub."}, status=status.HTTP_400_BAD_REQUEST)

        emails = email_response.json()
        primary_email = next((email['email'] for email in emails if email['primary']), None)
        
        if not primary_email:
            return Response({"error": "Primary GitHub email not found or not public"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=primary_email)
        except User.DoesNotExist:
          
            full_name = user_data.get('name') 
            first_name = ""
            last_name = ""
            if full_name:
                name_parts = full_name.split()
                first_name = name_parts[0]
                if len(name_parts) > 1:
                    last_name = " ".join(name_parts[1:]) 
            username = user_data.get('login')
            if User.objects.filter(username=username).exists():
       
                import uuid
                username = f"{username}_{uuid.uuid4().hex[:4]}"

            user = User.objects.create_user(
                username=username,
                email=primary_email,
                first_name=first_name,
                last_name=last_name,
                password=None 
            )

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
@permission_classes([IsAdminUser]) 
def user_list(request):
    """
    Returns a list of all users.
    """
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail_me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)



@api_view(['PATCH'])
@permission_classes([IsAdminUser])
def change_user_role(request, user_id):
    """
    Allows an admin user to change another user's role.
    Expects a JSON body with a "role" key: {"role": "admin"} or {"role": "member"}.
    """
    try:
        user_to_modify = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found.'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    new_role = request.data.get('role')

    if new_role not in ['admin', 'member']:
        return Response(
            {'error': 'Invalid role. Please specify "admin" or "member".'},
            status=status.HTTP_400_BAD_REQUEST
        )
        
    if request.user.id == user_to_modify.id:
        return Response(
            {'error': 'Admins cannot change their own role through this endpoint.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    profile = user_to_modify.profile


    profile.role = new_role
    profile.save(update_fields=['role'])

    user_to_modify.is_staff = (new_role == 'admin')
    user_to_modify.save(update_fields=['is_staff'])


    if new_role == 'admin':
        message = f"User '{user_to_modify.username}' has been promoted to admin."
    else: 
        message = f"User '{user_to_modify.username}' has been demoted to member."

    serializer = UserSerializer(user_to_modify)
    return Response(
        {
            'message': message,
            'user': serializer.data
        },
        status=status.HTTP_200_OK
    )
