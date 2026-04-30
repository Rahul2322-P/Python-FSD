from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MinLengthValidator, URLValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class LearningModule(models.Model):
    """Educational content module for sustainability learning"""
    
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)],
        unique=True,
        db_index=True
    )
    description = models.TextField(
        validators=[MinLengthValidator(10)],
        help_text="Brief summary of the module content"
    )
    content = models.TextField(
        help_text="Detailed content with HTML formatting support"
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    estimated_time = models.IntegerField(
        default=15,
        validators=[MinValueValidator(1)],
        help_text="Estimated time to complete in minutes"
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active', '-created_at']),
        ]
        verbose_name = 'Learning Module'
        verbose_name_plural = 'Learning Modules'
    
    def __str__(self):
        return f"{self.title} ({self.get_difficulty_level_display()})"
    
    def get_completion_rate(self):
        """Calculate module completion rate among users"""
        total_users = User.objects.filter(is_active=True).count()
        if total_users == 0:
            return 0
        completed = self.userprofile_set.filter(completed_modules=self).count()
        return round((completed / total_users) * 100, 2)


class Challenge(models.Model):
    """Eco-friendly practice challenges for users"""
    
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(3)],
        unique=True,
        db_index=True
    )
    description = models.TextField(
        validators=[MinLengthValidator(10)],
        help_text="What does this challenge involve?"
    )
    points = models.IntegerField(
        default=10,
        validators=[MinValueValidator(1)],
        help_text="Reward points for completing this challenge"
    )
    difficulty = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
        ],
        default='easy'
    )
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    repeatable = models.BooleanField(
        default=False,
        help_text="Can users complete this challenge multiple times?"
    )
    
    class Meta:
        ordering = ['-points', '-created_at']
        indexes = [
            models.Index(fields=['-points']),
            models.Index(fields=['is_active', '-points']),
        ]
        verbose_name = 'Challenge'
        verbose_name_plural = 'Challenges'
    
    def __str__(self):
        return f"{self.title} ({self.points} pts)"
    
    def get_completion_count(self):
        """Get number of users who completed this challenge"""
        return self.userprofile_set.filter(completed_challenges=self).count()


class UserProfile(models.Model):
    """Extended user profile for platform features"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='userprofile',
        db_index=True
    )
    completed_modules = models.ManyToManyField(
        LearningModule,
        blank=True,
        related_name='completed_by_users'
    )
    completed_challenges = models.ManyToManyField(
        Challenge,
        blank=True,
        related_name='completed_by_users'
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Tell other users about yourself"
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text="Your city or region"
    )
    avatar_url = models.URLField(
        blank=True,
        help_text="Link to your profile picture"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def total_points(self):
        """Calculate total points from completed challenges (optimized)"""
        return sum(
            challenge.points 
            for challenge in self.completed_challenges.all()
        ) or 0
    
    def get_completed_modules_count(self):
        """Get count of completed modules"""
        return self.completed_modules.count()
    
    def get_completed_challenges_count(self):
        """Get count of completed challenges"""
        return self.completed_challenges.count()
    
    def get_profile_completion(self):
        """Get completion percentage of user profile fields"""
        fields_filled = 0
        total_fields = 3  # bio, location, avatar_url
        
        if self.bio:
            fields_filled += 1
        if self.location:
            fields_filled += 1
        if self.avatar_url:
            fields_filled += 1
            
        return round((fields_filled / total_fields) * 100)


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    """Signal handler to create/update UserProfile on User save"""
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()
        else:
            UserProfile.objects.create(user=instance)
