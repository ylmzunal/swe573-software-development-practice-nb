from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static

def default_profile_picture():
    return static('img/profile_picture.png')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    birthday = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default=default_profile_picture, max_length=255)
    bio = models.TextField(default="Hello, I am a member of this platform.")
    # wikidata tags may be added here

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
# default user model contains username, first_name, last_name, email, password, groups, user_permissions, is_staff, is_active, is_superuser, last_login, date_joined