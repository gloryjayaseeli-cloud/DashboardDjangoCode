from django.test import TestCase
from django.contrib.auth.models import User
from ...models.ProjectModal import Project
from ...models.TaskModal import Task

from ...serializers.ProjectSerializer import ProjectSerializer

class test_ProjectSerializerTest(TestCase):

    def setUp(self):
        """
        Set up the necessary objects for the tests.
        This method is run before each test function.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.project = Project.objects.create(
            name='Main Project',
            description='A project for testing.',
            start_date='2025-10-14',
            end_date='2025-12-31',
            owner=self.user
        )
        Task.objects.create(project=self.project, description='Task 1', owner=self.user)
        Task.objects.create(project=self.project, description='Task 2', owner=self.user)

        self.valid_data_for_create = {
            'name': 'New Project',
            'description': 'A new project from payload.',
            'start_date': '2026-01-01',
            'end_date': '2026-02-01',
            'owner': 'testuser'  
        }

    def test_serialization_output_is_correct(self):
        """
        Tests that serializing a Project instance produces the correct data format,
        including the nested tasks and the owner's username.
        """
        serializer = ProjectSerializer(instance=self.project)
        
        data = serializer.data

        self.assertEqual(data['id'], self.project.id)
        self.assertEqual(data['name'], 'Main Project')

        self.assertEqual(data['owner'], self.user.username)

        self.assertIn('tasks', data)
        self.assertIsInstance(data['tasks'], list)
        self.assertEqual(len(data['tasks']), 2)
        self.assertEqual(data['tasks'][0]['description'], 'Task 1')

    def test_deserialization_with_valid_data(self):
        """
        Tests that the serializer successfully validates correct incoming data.
        """
        serializer = ProjectSerializer(data=self.valid_data_for_create)
        
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_read_only_tasks_field_is_ignored_on_input(self):
        """
        Ensures that if a 'tasks' list is provided during deserialization,
        it is correctly ignored because the field is read-only.
        """
        data_with_tasks = self.valid_data_for_create.copy()
        data_with_tasks['tasks'] = [{'description': 'should be ignored'}]
        
        serializer = ProjectSerializer(data=data_with_tasks)

        self.assertTrue(serializer.is_valid(raise_exception=True))
        
        self.assertNotIn('tasks', serializer.validated_data)
        
    def test_create_method_works_correctly(self):
        """
        Tests that the serializer's .save() method correctly creates a new Project
        when provided with a valid username for the owner.
        """
        serializer = ProjectSerializer(data=self.valid_data_for_create)
        self.assertTrue(serializer.is_valid())
        
        new_project = serializer.save()

        self.assertEqual(Project.objects.count(), 2)
        self.assertEqual(new_project.name, self.valid_data_for_create['name'])
        
        self.assertEqual(new_project.owner, self.user)