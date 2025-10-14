

from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import Project, Task, UserProfile


class UserSerializer(serializers.ModelSerializer):
  
    groups = serializers.StringRelatedField(many=True)

    class Meta:
        model = User


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
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        UserProfile.objects.filter(user=user).update(**profile_data)
        return user