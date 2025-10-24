
from django.urls import path, reverse
from django.test import override_settings 
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.test import APITestCase
from rest_framework import status
from ..permissions import IsAdminUser

class ProtectedAdminView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        return Response({"message": "Admin access granted."})

urlpatterns = [
    path('protected-admin-route/', ProtectedAdminView.as_view(), name='protected_admin_route'),
]

@override_settings(ROOT_URLCONF='api.tests.test_Permissions')
class IsAdminUserPermissionTest(APITestCase):
    
    def setUp(self):
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password123')
        self.normal_user = User.objects.create_user('member', 'member@example.com', 'password123')
        self.url = reverse('protected_admin_route')
        
    def test_admin_user_has_permission(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_normal_user_is_denied_permission(self):
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_is_denied_permission(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)