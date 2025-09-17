# yourapp/permissions.py
from rest_framework.permissions import BasePermission

class IsAdminUser(BasePermission):
    """
    Custom permission to only allow users in the 'Admin' group.
    """
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        # Check if the user is authenticated and is a member of the target group.
        return request.user and request.user.groups.filter(name='Admin').exists()