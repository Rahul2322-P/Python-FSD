from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MinLengthValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import secrets


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
        verbose_name = 'Learning Module'
        verbose_name_plural = 'Learning Modules'
    
    def __str__(self):
        return f"{self.title} ({self.get_difficulty_level_display()})"


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
        verbose_name = 'Challenge'
        verbose_name_plural = 'Challenges'
    
    def __str__(self):
        return f"{self.title} ({self.points} pts)"


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
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def total_points(self):
        """Calculate total points from completed challenges"""
        return sum(
            challenge.points 
            for challenge in self.completed_challenges.all()
        ) or 0


class EmailVerification(models.Model):
    """Track email verification codes"""
    
    VERIFICATION_TYPE_CHOICES = [
        ('registration', 'Registration'),
        ('login', 'Login'),
        ('admin_login', 'Admin Login'),
    ]
    
    email = models.EmailField(db_index=True)
    verification_code = models.CharField(max_length=6, unique=True, db_index=True)
    verification_type = models.CharField(
        max_length=20,
        choices=VERIFICATION_TYPE_CHOICES
    )
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'verification_type']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.verification_type}"
    
    def is_valid(self):
        """Check if verification code is still valid"""
        return not self.is_verified and timezone.now() < self.expires_at
    
    def is_expired(self):
        """Check if verification code has expired"""
        return timezone.now() > self.expires_at
    
    @staticmethod
    def generate_code():
        """Generate a 6-digit verification code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])


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
