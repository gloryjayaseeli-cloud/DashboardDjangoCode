from django.test import TestCase
from django.contrib.auth.models import User
from ...models.ProjectModal import Project

class test_ProjectModelTest(TestCase):

    def setUp(self):
        """
        Set up a user that will act as the owner for projects in our tests.
        This method runs before each test function.
        """
        self.owner = User.objects.create_user(
            username='project_owner', 
            password='password123'
        )
        self.project = Project.objects.create(
            owner=self.owner,
            name="Test Project Alpha",
            description="A sample project for testing.",
            start_date="2025-10-15",
            end_date="2025-11-15"
        )

    def test_project_creation(self):
        """
        Tests that a Project instance can be created with all required fields.
        """
        self.assertIsInstance(self.project, Project)
        self.assertEqual(Project.objects.count(), 1)
        
        self.assertEqual(self.project.name, "Test Project Alpha")
        self.assertEqual(self.project.owner.username, "project_owner")

    def test_str_method_returns_project_name(self):
        """
        Tests the __str__ method to ensure it returns the project's name.
        """
       
        self.assertEqual(str(self.project), "Test Project Alpha")

    def test_project_owner_relationship(self):
        """
        Tests the reverse relationship from the User model to the Project model.
        The `related_name='projects'` allows us to do `user.projects.all()`.
        """
        Project.objects.create(
            owner=self.owner,
            name="Test Project Bravo",
            start_date="2026-01-01",
            end_date="2026-02-01"
        )

        owner_projects = self.owner.projects.all()

        self.assertEqual(owner_projects.count(), 2)
        
        self.assertIn(self.project, owner_projects)