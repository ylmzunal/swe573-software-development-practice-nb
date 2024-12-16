from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
import os
from core.models.posts_models import Post


# a model to store comments on a post with the following fields:
# post: the post that the comment is on
# author: the user who wrote the comment
# content: the content of the comment
# tag: the tag of the comment (question, hint, answer)
# parent: the parent comment if the comment is a reply
# created_at: the date and time when the comment was created
# is_deleted: a boolean to indicate if the comment is deleted
# the relationship is one to many between post and comment and one post can have multiple comments and one comment can have only one post
# the relationship is one to one between comment and parent and one comment can have only one parent and one parent can have multiple comments
# the relationship is one to many between comment and reply and one comment can have multiple replies and one reply can have only one comment
class Comment(models.Model):
    TAG_CHOICES = [
        ('question', 'Question'),
        ('hint', 'Hint'),
        ('answer', 'Answer'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    tag = models.CharField(max_length=10, choices=TAG_CHOICES, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.post.title}'

    def get_replies(self):
        return Comment.objects.filter(parent=self).order_by('created_at')

    def can_tag_as_answer(self, user): # to check if the user can tag the comment as an answer
        return user == self.post.author

    def can_edit_tag(self, user): # to check if the user can edit the tag of the comment
        return user == self.post.author and not self.is_deleted

    def save(self, *args, **kwargs): # to check if the comment is an answer and update the post status
        if self.pk:
            old_instance = Comment.objects.get(pk=self.pk)
            had_answer = old_instance.tag == 'answer'
        else:
            had_answer = False
        super().save(*args, **kwargs)
        if had_answer != (self.tag == 'answer') or self.is_deleted: # to check if the answer status changed and update the post status if needed
            self.update_post_status()

    def update_post_status(self): # to update the post status based on answer comments
        if self.post.status == 'solved' and not self.post.has_answer_comment(): # true if the post is solved and does not have an answer comment
            old_status = self.post.status
            self.post.status = 'unknown'
            self.post.save()
            return old_status != 'unknown'
        return False

    def delete(self, *args, **kwargs):
        post = self.post
        had_answer = self.tag == 'answer'
        super().delete(*args, **kwargs)
        if had_answer and not post.has_answer_comment():
            post.status = 'unknown'
            post.save()

    def upvote_count(self):
        return self.votes.filter(vote_type='up').count()
    
    def downvote_count(self):
        return self.votes.filter(vote_type='down').count()

