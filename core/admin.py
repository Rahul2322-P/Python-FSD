from django.contrib import admin
from .models import LearningModule, Challenge, UserProfile

@admin.register(LearningModule)
class LearningModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')
    search_fields = ('title',)

@admin.register(Challenge)
class ChallengeAdmin(admin.ModelAdmin):
    list_display = ('title', 'points', 'created_at')
    search_fields = ('title',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_points')
    search_fields = ('user__username',)
