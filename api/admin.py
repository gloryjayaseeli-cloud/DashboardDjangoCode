

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Project, Task

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)



admin.site.unregister(User)

admin.site.register(User, CustomUserAdmin)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
   
    list_display = ('name', 'owner', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    list_filter = ('owner',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
  
    list_display = ('description', 'project', 'status', 'due_date', 'owner')
    search_fields = ('description',)

    list_filter = ('project', 'status', 'owner')

