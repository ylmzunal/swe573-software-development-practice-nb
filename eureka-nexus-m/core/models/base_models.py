from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
import os


# a function to get a unique path for the profile picture
def get_unique_profile_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('profile_pictures', filename)


# a model to store the profile of the user with the following fields and the fields in the AbstractUser model:
# username: the username of the user
# email: the email of the user
# first_name: the first name of the user
# last_name: the last name of the user
# password: the password of the user    
# is_active: the active status of the user
# is_staff: the staff status of the user
# is_superuser: the superuser status of the user
# last_login: the last login date and time of the user
# date_joined: the date and time when the user was created
# groups: the groups of the user 
# user_permissions: the permissions of the user
# new created fields:
# profile_picture: the profile picture of the user
# bio: the bio of the user
# birthday: the birthday of the user
# the relationship is one to one between user and profile and one user can have only one profile and one profile can have only one user
class Profile(AbstractUser):
    profile_picture = models.ImageField(
        upload_to=get_unique_profile_path,
        null=True,
        blank=True
    )
    bio = models.TextField(default="Hello, I am a member of this platform.")
    birthday = models.DateField(null=True, blank=True)

