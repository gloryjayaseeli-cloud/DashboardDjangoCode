from django.test import TestCase
from django.contrib.auth.models import User
from ...models.ProjectModal import Project
from ...models.TaskModal import Task

from ...serializers.TaskSerializer import TaskSerializer

class test_TaskSerializerTest(TestCase):

    def setUp(self):
        """
        Create the necessary User, Project, and Task instances for our tests.
        This method runs before each individual test.
        """
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.project = Project.objects.create(
        name='Test Project',
        owner=self.user,
        start_date='2025-10-15',
        end_date='2025-11-15'  
    )
        self.task = Task.objects.create(
            project=self.project,
            description='A test task',
            status='new',
            owner=self.user,
            due_date='2025-10-14', 
            )
        self.valid_data = {
            'description': 'A new task from payload',
            'status': 'new',
            'owner': 'testuser'
        }

    def test_serialization_output_contains_expected_fields(self):
        """
        Tests that serializing a Task object produces the correct output format.
        Focuses on ensuring the 'owner' is correctly represented by their username.
        """
        serializer = TaskSerializer(instance=self.task)
        
        data = serializer.data

        self.assertEqual(data['id'], self.task.id)
        self.assertEqual(data['description'], 'A test task')
        self.assertEqual(data['status'], 'new')
        
        self.assertEqual(data['owner'], self.user.username)
        
        self.assertEqual(data['project'], self.project.id)

    def test_deserialization_with_valid_data_is_valid(self):
        """
        Tests that the serializer successfully validates correct incoming data.
        """
        serializer = TaskSerializer(data=self.valid_data)
                
        self.assertTrue(serializer.is_valid(raise_exception=True))
        
    def test_read_only_project_field_is_ignored_on_input(self):
        """
        Ensures that if a 'project' field is included in the input data,
        it is correctly ignored because it's a read-only field.
        """
        data_with_project = self.valid_data.copy()
        data_with_project['project'] = 999 
        serializer = TaskSerializer(data=data_with_project)

        self.assertTrue(serializer.is_valid(raise_exception=True))
        
        self.assertNotIn('project', serializer.validated_data)

    def test_create_method_correctly_assigns_project_from_context(self):
        """
        This is a key test. It verifies that a task can be created when the
        'project' is passed into the .save() method, simulating what a view would do.
        """
        serializer = TaskSerializer(data=self.valid_data)
        
        self.assertTrue(serializer.is_valid(raise_exception=True))

        new_task = serializer.save(project=self.project)

        self.assertEqual(Task.objects.count(), 2)
        self.assertEqual(new_task.description, self.valid_data['description'])
        self.assertEqual(new_task.owner, self.user)
        
        self.assertEqual(new_task.project, self.project)