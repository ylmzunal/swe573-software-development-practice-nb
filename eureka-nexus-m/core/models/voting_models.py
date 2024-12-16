from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
import os


# a model to vote on a post or a comment with the following fields:
# user: the user who is voting
# post: the post that the user is voting on
# comment: the comment that the user is voting on
# vote_type: the type of vote (up or down)
# created_at: the date and time when the vote was created
# the relationship is unique between user and post and one user can vote multiple times on a post and one post can have multiple votes but only one vote per user per post
# the relationship is unique between user and comment and one user can vote multiple times on a comment and one comment can have multiple votes but only one vote per user per comment
class Vote(models.Model):
    VOTE_CHOICES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ('user', 'post'),
            ('user', 'comment')
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(post__isnull=False, comment__isnull=True) |
                    models.Q(post__isnull=True, comment__isnull=False)
                ),
                name='vote_only_on_post_or_comment'
            )
        ]

    def clean(self):
        if self.vote_type not in ['up', 'down']:
            raise ValidationError('Invalid vote type')
        if bool(self.post) == bool(self.comment):
            raise ValidationError('Vote must be either on a post or a comment, not both or neither')

