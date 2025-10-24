from django.test import TestCase
from django.contrib.auth.models import User
from ...models.UserModal import UserProfile

class test_UserProfileModelTest(TestCase):

    def test_profile_is_created_automatically_on_user_creation(self):
        """
        Tests that the `create_user_profile` post_save signal works correctly.
        When a new User is created, a UserProfile should be created for it.
        """
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(UserProfile.objects.count(), 0)
        
        user = User.objects.create_user(username='testuser', password='password123')

        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 1)
        
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)
        self.assertEqual(user.profile.user, user)

    def test_default_role_is_member(self):
        """
        Tests that a newly created UserProfile defaults to the 'member' role.
        """
        user = User.objects.create_user(username='new_member', password='password123')

        self.assertEqual(user.profile.role, 'member')

    def test_str_method_returns_correct_format(self):
        """
        Tests the __str__ method of the UserProfile model.
        """
        user = User.objects.create_user(username='str_test_user', password='password123')
        
        self.assertEqual(str(user.profile), "str_test_user's Profile")
        
    def test_saving_user_also_saves_profile(self):
        """
        Tests that the `save_user_profile` signal correctly handles updates.
        This ensures that saving the User model doesn't break or delete the profile.
        """
        user = User.objects.create_user(username='update_test', password='password123')
        
        self.assertEqual(user.profile.role, 'member')
        
        user.email = "new_email@example.com"
        user.save()
        
        user.profile.refresh_from_db()
        self.assertEqual(user.profile.role, 'member')