from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MinLengthValidator

class LearningModule(models.Model):
    title = models.CharField(max_length=200, validators=[MinLengthValidator(3)])
    description = models.TextField(validators=[MinLengthValidator(10)])
    content = models.TextField(help_text="Detailed content or HTML for the module")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class Challenge(models.Model):
    title = models.CharField(max_length=200, validators=[MinLengthValidator(3)])
    description = models.TextField(validators=[MinLengthValidator(10)])
    points = models.IntegerField(default=10, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    completed_modules = models.ManyToManyField(LearningModule, blank=True)
    completed_challenges = models.ManyToManyField(Challenge, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    avatar_url = models.URLField(blank=True, help_text="Link to a profile picture")

    @property
    def total_points(self):
        return sum(challenge.points for challenge in self.completed_challenges.all())

    def __str__(self):
        return f"{self.user.username} Profile"

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'userprofile'):
            instance.userprofile.save()
        else:
            UserProfile.objects.create(user=instance)
