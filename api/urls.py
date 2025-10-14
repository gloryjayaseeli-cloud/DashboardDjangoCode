# myprojectdashboard/api/urls.py

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import UserView, ProjectView, TaskView
from .views.UserView import (
    GitHubLogin, 
    UserProfileView, 
    
)

urlpatterns = [
    # Authentication
    path('signup/', UserView.signup, name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('auth/github/', UserView.GitHubLogin.as_view(), name='github_login'),
    
    # User 
    path('users/me/', UserView.UserProfileView.as_view(), name='user-profile'),
    path('users/<int:user_id>/set-role/', UserView.change_user_role, name='change-user-role'),
    path('users/', UserView.user_list, name='user-list'),
    path('me/', UserView.user_detail_me, name='user-detail-me'),

    # Project URLs
    path('projects/', ProjectView.project_list_create, name='project-list-create'),
    path('projects/<int:pk>/', ProjectView.project_detail_update_delete, name='project-detail-update-delete'),

    path('projects/<int:project_pk>/tasks/', TaskView.task_list_create, name='task-list-create'),
    path('projects/<int:project_pk>/tasks/<int:task_pk>/', TaskView.task_detail_update_delete, name='task-detail-update-delete'),
]
