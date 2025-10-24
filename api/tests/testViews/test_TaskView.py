from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ...models.ProjectModal import Project
from ...models.TaskModal import Task


class test_TaskViewsTest(APITestCase):

    def setUp(self):
        """Set up users, projects, and tasks for all tests."""
        self.admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password123')
        self.project_owner = User.objects.create_user('owner', 'owner@example.com', 'password123')
        self.other_user = User.objects.create_user('member', 'member@example.com', 'password123')

        self.project = Project.objects.create(
            name="Test Project", 
            owner=self.project_owner,
            start_date="2025-10-15",
            end_date="2025-11-15"
        )
        self.task = Task.objects.create(
            project=self.project, 
            description="A key task", 
            owner=self.project_owner, 
            due_date="2025-11-15",
            status="new"
        )
  

    def test_list_tasks_as_project_owner(self):
        """
        Ensures the project owner can list tasks in their project.
        """
        self.client.force_authenticate(user=self.project_owner)
        url = reverse('task-list-create', kwargs={'project_pk': self.project.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['description'], self.task.description)

    def test_list_tasks_as_admin(self):
        """
        Ensures an admin can list tasks in any project.
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('task-list-create', kwargs={'project_pk': self.project.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_tasks_permission_denied_for_other_user(self):
        """
        Ensures a user who is not the owner or an admin cannot list tasks.
        """
        self.client.force_authenticate(user=self.other_user)
        url = reverse('task-list-create', kwargs={'project_pk': self.project.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_task_as_project_owner(self):
        """
        Ensures the project owner can create a new task in their project.
        """
        self.client.force_authenticate(user=self.project_owner)
        url = reverse('task-list-create', kwargs={'project_pk': self.project.pk})
        data = {'description': 'New task by owner', 'owner': self.project_owner.username, 'status': 'in_progress', 'due_date': '2025-12-31'}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 2)

    def test_create_task_fails_for_nonexistent_project(self):
        """
        Ensures creating a task for a project that does not exist returns a 404.
        """
        self.client.force_authenticate(user=self.project_owner)
        url = reverse('task-list-create', kwargs={'project_pk': 999})
        data = {'description': 'New task', 'owner': self.project_owner.username, 'status': 'in_progress', 'due_date': '2025-12-31'}
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_task_detail_as_owner(self):
        """
        Ensures the task owner can retrieve the task details.
        """
        self.client.force_authenticate(user=self.project_owner)
        url = reverse('task-detail-update-delete', kwargs={'project_pk': self.project.pk, 'task_pk': self.task.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['description'], self.task.description)

    def test_get_task_detail_permission_denied(self):
        """
        Ensures a non-owner/non-admin cannot retrieve task details.
        """
        self.client.force_authenticate(user=self.other_user)
        url = reverse('task-detail-update-delete', kwargs={'project_pk': self.project.pk, 'task_pk': self.task.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_task_as_owner(self):
        """
        Ensures the task owner can update their task.
        """
        self.client.force_authenticate(user=self.project_owner)
        url = reverse('task-detail-update-delete', kwargs={'project_pk': self.project.pk, 'task_pk': self.task.pk})
        data = {'description': 'Updated description', 'status': 'in_progress', 'due_date': '2025-12-31' }
        
        response = self.client.put(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.task.refresh_from_db()
        self.assertEqual(self.task.description, 'Updated description')
        self.assertEqual(self.task.status, 'in_progress')
    
    def test_update_task_by_admin_fails_if_not_task_owner(self):
        """
        Tests the confusing logic where an admin who is not the task owner gets a 404.
        This is based on the `get(..., owner=request.user)` check in the view.
        """
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('task-detail-update-delete', kwargs={'project_pk': self.project.pk, 'task_pk': self.task.pk})
        data = {'description': 'Admin trying to update'}

        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    def test_delete_task_as_owner(self):
        """
        Ensures the task owner can delete their task.
        """
        self.client.force_authenticate(user=self.project_owner)
        url = reverse('task-detail-update-delete', kwargs={'project_pk': self.project.pk, 'task_pk': self.task.pk})
        
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.count(), 0)