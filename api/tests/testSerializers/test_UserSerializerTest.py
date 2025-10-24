from rest_framework.test import APITestCase
from rest_framework import serializers
from django.contrib.auth.models import User
from ...models import UserProfile
from ...serializers.UserSerializer import UserSerializer, UserProfileSerializer

class test_UserSerializerTest(APITestCase):
    
    def setUp(self):
        """Set up the data needed for the tests."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'strongpassword123',
            'profile': {
                'role': 'admin'
            }
        }

    def test_serializer_with_valid_data_is_valid(self):
        """
        Tests that the serializer passes validation with correct and complete data.
        """
        # Arrange
        serializer = UserSerializer(data=self.user_data)
        
        # Act & Assert ✅
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_serializer_fails_without_required_fields(self):
        """
        Tests that the serializer fails validation if required fields like 'username' are missing.
        """
        invalid_data = self.user_data.copy()
        del invalid_data['username']
        
        serializer = UserSerializer(data=invalid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('username', serializer.errors)

    def test_create_method_creates_user_and_profile(self):
        """
        This is the most critical test.
        It ensures the custom .create() method successfully creates both a User
        and its associated UserProfile with the correct role.
        """
        serializer = UserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        user = serializer.save()

        self.assertIsInstance(user, User)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(user.username, self.user_data['username'])

        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertNotEqual(user.password, self.user_data['password'])

        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(UserProfile.objects.count(), 1)
        self.assertEqual(user.profile.role, self.user_data['profile']['role'])
        
    def test_serialization_omits_password(self):
         user = User.objects.create_user(username='test', password='pw')
        
         user.profile.role = 'Admin'
         user.profile.save()

         serializer = UserSerializer(instance=user)
         serialized_data = serializer.data
        

         self.assertIn('profile', serialized_data)
         self.assertEqual(serialized_data['profile']['role'], 'Admin')
         self.assertNotIn('password', serialized_data)