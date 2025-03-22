from django.contrib import admin
from .models import UserProfile, FireAlert, Verification

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'guardian_points', 'created_at']
    search_fields = ['user__username']

@admin.register(FireAlert)
class FireAlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'reporter', 'status', 'votes_yes', 'votes_no', 'created_at']
    list_filter = ['status']
    search_fields = ['reporter__username']

@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ['alert', 'verifier', 'vote', 'created_at']
    list_filter = ['vote']
    search_fields = ['verifier__username', 'alert__id']
