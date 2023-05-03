from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User
from e_voting.models import Poll, Candidate, Vote
# Register your models here.

class UserAdmin(BaseUserAdmin):
    ordering = ["id"]
    list_display = ["email", "first_name", "last_name"]
    list_filter = ["is_staff"]

    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["first_name", "last_name", "phone_number"]}),
        ("Permissions", {"fields": ["is_active", "is_admin"]}),
    ]
    
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "first_name", "last_name", "phone_number" "password1", "password2"],
            },
        ),
    ]
    

admin.site.register(User, UserAdmin)

admin.site.register(Poll)
admin.site.register(Candidate)
admin.site.register(Vote)
