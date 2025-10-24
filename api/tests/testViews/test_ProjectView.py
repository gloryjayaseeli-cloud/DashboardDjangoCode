from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ...models.ProjectModal import Project

class test_ProjectViewsTest(APITestCase):

    def setUp(self):
        """Set up users and projects to test various permission scenarios."""
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password123')
        self.user_one = User.objects.create_user('user1', 'user1@example.com', 'password123')
        self.user_two = User.objects.create_user('user2', 'user2@example.com', 'password123')

        self.project_one = Project.objects.create(
            name="Project Alpha", 
            owner=self.user_one,
            start_date="2025-01-01",
            end_date="2025-02-01"
        )
        self.project_two = Project.objects.create(
            name="Project Beta", 
            owner=self.user_two,
            start_date="2025-03-01",
            end_date="2025-04-01"
        )
        self.list_create_url = reverse('project-list-create')

    def test_list_projects_as_normal_user_sees_only_own_projects(self):
        """
        Ensures a normal authenticated user can only list their own projects.
        """
        self.client.force_authenticate(user=self.user_one)
        response = self.client.get(self.list_create_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], self.project_one.name)

    def test_list_projects_as_admin_sees_all_projects(self):
        """
        Ensures an admin user can list all projects from all users.
        """
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.list_create_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2) 

    def test_create_project_as_authenticated_user(self):
        """
        Ensures an authenticated user can create a new project.
        """
        self.client.force_authenticate(user=self.user_one)
        data = {
            'name': 'New Project Gamma',
            'owner': self.user_one.username,
            'start_date': '2026-01-01',
            'end_date': '2026-02-01'
        }
        response = self.client.post(self.list_create_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Project.objects.count(), 3)
        
    def test_list_projects_unauthenticated(self):
        """
        Ensures unauthenticated users cannot list projects.
        """
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
  

    def test_get_project_detail_by_owner(self):
        """
        Ensures a project owner can retrieve their project's details.
        """
        self.client.force_authenticate(user=self.user_one)
        url = reverse('project-detail-update-delete', kwargs={'pk': self.project_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['name'], self.project_one.name)

    def test_get_project_detail_by_non_owner_forbidden(self):
        """
        Ensures a user cannot retrieve details of a project they do not own.
        """
        self.client.force_authenticate(user=self.user_two) 
        url = reverse('project-detail-update-delete', kwargs={'pk': self.project_one.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_project_by_owner(self):
        """
        Ensures a project owner can update their project.
        """
        self.client.force_authenticate(user=self.user_one)
        url = reverse('project-detail-update-delete', kwargs={'pk': self.project_one.pk})
        data = {'name': 'Project Alpha Updated'}
        
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.project_one.refresh_from_db()
        self.assertEqual(self.project_one.name, 'Project Alpha Updated')
        
    def test_delete_project_by_owner_is_forbidden(self):
        """
        Tests the specific rule that a non-admin (even the owner) cannot delete a project.
        """
        self.client.force_authenticate(user=self.user_one)
        url = reverse('project-detail-update-delete', kwargs={'pk': self.project_one.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Project.objects.count(), 2) 

    def test_delete_project_by_admin_succeeds(self):
        """
        Tests that an admin user can successfully delete a project.
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('project-detail-update-delete', kwargs={'pk': self.project_one.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Project.objects.count(), 1) 
        
    def test_access_nonexistent_project_returns_404(self):
        """
        Ensures accessing a project with an invalid PK returns a 404 Not Found.
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('project-detail-update-delete', kwargs={'pk': 999})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)