from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth.models import Group

class MyCustomAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
       
        user = super().save_user(request, sociallogin, form)

        if sociallogin.is_existing:
            return user 
        
        try:
            default_group = Group.objects.get(name='Viewers')
            user.groups.add(default_group)
        except Group.DoesNotExist:
           pass
            
        return user