from django.contrib import admin
from .models import *


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "headline",
        "phone",
        "location",
    )

    search_fields = (
        "user__username",
        "user__email",
        "headline",
        "skills",
    )

    list_filter = (
        "location",
    )
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "password")

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "company", "location", "salary","job_description", "created_at")
    search_fields = ("title", "company", "location")
    list_filter = ("location", "company")
@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("user", "job", "status")
    search_fields = ("user__email", "job__title")
    list_filter = ("status",)    