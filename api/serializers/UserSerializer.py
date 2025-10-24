

from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Project, Task, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'profile']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
     profile_data = validated_data.pop('profile')
     user = User.objects.create_user(**validated_data)
     if profile_data:
        profile = user.profile
        profile.role = profile_data.get('role')
        profile.save()
    
     return user