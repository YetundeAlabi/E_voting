from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from accounts.models import User
from api.models import Poll, Candidate, Vote, Voter
# Register your models here.


class UserAdmin(BaseUserAdmin):
    ordering = ["id"]
    list_display = ["email", "first_name",
                    "last_name", "is_active", "is_verified"]
    list_filter = ["is_staff"]

    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        ("Personal info", {"fields": [
         "first_name", "last_name", "phone_number"]}),
        ("Permissions", {"fields": ["is_active", "is_staff", "is_verified"]}),
        (None, {"fields": ["is_deleted"]}),
        ("Dates", {"fields": ["last_login",]})
    ]

    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "first_name", "last_name", "phone_number", "password1", "password2"],
            },
        ),
    ]


search_fields = ("email",)
ordering = ("email",)

admin.site.register(User, UserAdmin)
admin.site.register(Poll)
admin.site.register(Candidate)
admin.site.register(Vote)
admin.site.register(Voter)
