

from rest_framework import serializers
from django.contrib.auth.models import User, Group
from ..models import Project, Task, UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['role']

class UserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        queryset=Group.objects.all(),
        slug_field='name',  
        required=False      
    )

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password',  'groups']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        groups_data = validated_data.pop('groups', None)

        user = User.objects.create_user(**validated_data)

        if groups_data:
            user.groups.set(groups_data)

        return user