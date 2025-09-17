# myprojectdashboard/api/urls.py

from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views
from .views import GitHubLogin
from .views import UserProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # Authentication
    path('signup/', views.signup, name='signup'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('auth/github/', GitHubLogin.as_view(), name='github_login'),
    
    # User 
    path('users/me/', UserProfileView.as_view(), name='user-profile'),
    
    path('users/', views.user_list, name='user-list'),
    path('me/', views.user_detail_me, name='user-detail-me'),

    # Project URLs
    path('projects/', views.project_list_create, name='project-list-create'),
    path('projects/<int:pk>/', views.project_detail_update_delete, name='project-detail-update-delete'),

    path('projects/<int:project_pk>/tasks/', views.task_list_create, name='task-list-create'),
    path('projects/<int:project_pk>/tasks/<int:task_pk>/', views.task_detail_update_delete, name='task-detail-update-delete'),
]
