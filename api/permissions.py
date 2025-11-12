from rest_framework import permissions
class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users (is_staff=True).
    """
    def has_permission(self, request, view):
      
        return request.user and  request.user.groups.filter(name='Admin').exists()