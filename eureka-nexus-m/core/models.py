from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static

from django.contrib.auth.models import AbstractUser

class Profile(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(default="Hello, I am a member of this platform.")
    birthday = models.DateField(null=True, blank=True)


#profile_picture = models.ImageField(upload_to='profile_pics/', default='static/img/default_profile_pic.jpg')
