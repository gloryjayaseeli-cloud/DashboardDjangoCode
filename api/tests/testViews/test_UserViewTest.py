from unittest.mock import patch, Mock
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

class test_UserViewsTest(APITestCase):

    def setUp(self):
        """Set up initial users for testing permissions."""
        self.normal_user = User.objects.create_user(
            username='member', password='password123', email='member@example.com'
        )
        self.admin_user = User.objects.create_superuser(
            username='admin', password='password123', email='admin@example.com'
        )
        
        self.signup_url = reverse('signup')
        self.user_list_url = reverse('user-list')
        self.profile_url = reverse('user-profile')
        self.github_login_url = reverse('github_login')

   
    def test_signup_success(self):
        """Tests that a new user can be created successfully."""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpassword123"
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3) 

    def test_signup_fails_with_existing_username(self):
        """Tests that signup fails if the username is already taken."""
        data = {
            "username": "member", 
            "email": "another@example.com",
            "password": "password123"
        }
        response = self.client.post(self.signup_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_get_profile_unauthenticated(self):
        """Tests that unauthenticated users cannot access the profile view."""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_profile_authenticated(self):
        """Tests that an authenticated user can retrieve their own profile."""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.normal_user.username)

    def test_user_list_fails_for_normal_user(self):
        """Tests that a non-admin user cannot list all users."""
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_user_list_succeeds_for_admin_user(self):
        """Tests that an admin user can list all users."""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.user_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) 

    def test_change_role_succeeds_for_admin(self):
        """Tests that an admin can promote a normal user."""
        self.assertFalse(self.normal_user.is_staff)
        url = reverse('change-user-role', args=[self.normal_user.id])
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(url, {"role": "admin"})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
       
        self.normal_user.refresh_from_db()
        self.assertTrue(self.normal_user.is_staff)

    def test_admin_cannot_change_own_role(self):
        """Tests that an admin cannot change their own role via this endpoint."""
        url = reverse('change-user-role', args=[self.admin_user.id])
        
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.patch(url, {"role": "member"})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cannot change their own role', response.data['error'])

    @patch('api.views.UserView.requests.get')
    @patch('api.views.UserView.requests.post')
    def test_github_login_for_existing_user(self, mock_post, mock_get):
        """Tests a successful login via GitHub for a user who already exists."""
 
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {'access_token': 'fake_github_token'}

        mock_user_data = Mock(ok=True)
        mock_user_data.json.return_value = {'login': 'member', 'name': 'Test Member'}
        mock_email_data = Mock(ok=True)
        
        mock_email_data.json.return_value = [{'email': self.normal_user.email, 'primary': True}]
        mock_get.side_effect = [mock_user_data, mock_email_data]


        response = self.client.post(self.github_login_url, {'code': 'fake_code'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)
 
        self.assertEqual(User.objects.count(), 2)
        
    @patch('api.views.UserView.requests.get')
    @patch('api.views.UserView.requests.post')
    def test_github_login_for_new_user(self, mock_post, mock_get):
        """Tests a successful signup and login via GitHub for a new user."""
      
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {'access_token': 'fake_github_token'}

        mock_user_data = Mock(ok=True)
        mock_user_data.json.return_value = {'login': 'new_github_user', 'name': 'New User'}
        mock_email_data = Mock(ok=True)
        mock_email_data.json.return_value = [{'email': 'new_github_user@example.com', 'primary': True}]
        mock_get.side_effect = [mock_user_data, mock_email_data]

        response = self.client.post(self.github_login_url, {'code': 'fake_code'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertEqual(User.objects.count(), 3)
        self.assertTrue(User.objects.filter(email='new_github_user@example.com').exists())