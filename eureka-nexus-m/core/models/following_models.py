from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
import os


# a model to follow a post with the following fields:
# user: the user who is following the post
# post: the post that the user is following
# followed_at: the date and time when the user followed the post
# the relationship is unique between user and post and one user can follow multiple posts and one post can have multiple followers
class PostFollower(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed_posts')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} follows {self.post.title}"


# a model to follow a user with the following fields:
# user: the user who is following the user
# following: the user that the user is following
# followed_at: the date and time when the user followed the user
# the relationship is unique between user and following and one user can follow multiple users and one user can have multiple followers
class UserFollower(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', on_delete=models.CASCADE)
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'following')
