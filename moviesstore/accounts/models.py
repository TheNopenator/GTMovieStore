from django.db import models, OperationalError
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    RATING_CHOICES = [
        ('G', 'G - General Audiences'),
        ('PG', 'PG - Parental Guidance'),
        ('PG-13', 'PG-13 - Parents Strongly Cautioned'),
        ('R', 'R - Restricted'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    max_content_rating = models.CharField(max_length=5, choices=RATING_CHOICES, default='R')
    
    def __str__(self):
        return f'{self.user.username} Profile'
    
    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            try:
                Profile.objects.create(user=instance)
            except OperationalError:
                # Table doesn't exist yet - migrations haven't been run
                pass
    
    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        try:
            if hasattr(instance, 'profile'):
                instance.profile.save()
            else:
                Profile.objects.create(user=instance)
        except OperationalError:
            # Table doesn't exist yet - migrations haven't been run
            pass
