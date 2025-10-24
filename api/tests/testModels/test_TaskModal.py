from django.test import TestCase
from django.contrib.auth.models import User
from ...models.ProjectModal import Project
from ...models.TaskModal import Task

class test_TaskModelTest(TestCase):

    def setUp(self):
        """
        Set up the necessary User and Project instances that are prerequisites for a Task.
        This method runs before each individual test.
        """
        self.owner = User.objects.create_user(username='task_owner', password='password123')
        self.project = Project.objects.create(
            owner=self.owner,
            name="Main Test Project",
            start_date="2025-10-15",
            end_date="2025-11-15"
        )
        self.task = Task.objects.create(
            project=self.project,
            owner=self.owner,
            description="This is the first test task.",
            status='in_progress',
            due_date='2025-10-14'
        )

    def test_task_creation(self):
        """
        Tests that a Task instance can be created successfully with all required fields.
        """
        self.assertIsInstance(self.task, Task)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(self.task.description, "This is the first test task.")
        self.assertEqual(self.task.status, 'in_progress')
        self.assertEqual(self.task.project, self.project)
        self.assertEqual(self.task.owner, self.owner)

    def test_default_status_is_new(self):
        """
        Tests that if no status is provided, it defaults to 'new'.
        """
        task_with_default_status = Task.objects.create(
            project=self.project,
            owner=self.owner,
            description="A task with default status."
        )
        
        self.assertEqual(task_with_default_status.status, 'new')

    def test_str_method_returns_shortened_description(self):
        """
        Tests the __str__ method to ensure it returns the first 50 characters of the description.
        """
        long_description = "This is a very long description designed to be more than fifty characters to properly test the slicing in the __str__ method."
        long_task = Task.objects.create(
            project=self.project,
            owner=self.owner,
            description=long_description
        )

        self.assertEqual(str(long_task), long_description[:50])
        self.assertEqual(str(self.task), self.task.description)
        
    def test_relationships_to_project_and_user(self):
        """
        Tests the reverse relationships from Project and User back to Task,
        using the `related_name='tasks'`.
        """
        Task.objects.create(
            project=self.project,
            owner=self.owner,
            description="This is the second test task."
        )

        project_tasks = self.project.tasks.all()
        user_tasks = self.owner.tasks.all()

        self.assertEqual(project_tasks.count(), 2)
        self.assertEqual(user_tasks.count(), 2)
        
        self.assertIn(self.task, project_tasks)
        self.assertIn(self.task, user_tasks)