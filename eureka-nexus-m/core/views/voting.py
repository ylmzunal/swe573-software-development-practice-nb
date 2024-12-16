# imports
# Django core imports
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django import forms
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import DetailView
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import update_session_auth_hash
# Third-party imports
import requests
import json
import logging
from functools import reduce
from operator import and_, or_
# Local application imports
from core.forms import *
from core.models import *


# logger is used to log messages to the console
logger = logging.getLogger(__name__)


# user is to get the current user
User = get_user_model()


# a function to vote on a post
@login_required
def vote_post(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    vote_type = request.POST.get('vote_type')
    if vote_type not in ['up', 'down']:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    post = get_object_or_404(Post, id=post_id)
    existing_vote = Vote.objects.filter(user=request.user, post=post).first() # to get and check the existing vote if the user has already voted
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            existing_vote.delete() # if the user clicks the same vote type, remove the vote
            action = 'removed'
        else:
            existing_vote.vote_type = vote_type # if the user clicks different vote type, change the vote
            existing_vote.save()
            action = 'changed'
    else:
        Vote.objects.create(user=request.user, post=post, vote_type=vote_type) # to create a new vote
        action = 'added'
    # to get the updated vote counts
    upvotes = Vote.objects.filter(post=post, vote_type='up').count()
    downvotes = Vote.objects.filter(post=post, vote_type='down').count()
    return JsonResponse({
        'status': 'success',
        'action': action,
        'upvotes': upvotes,
        'downvotes': downvotes
    }) 


# a function to vote on a comment
@login_required
def vote_comment(request, comment_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    vote_type = request.POST.get('vote_type')
    if vote_type not in ['up', 'down']:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    comment = get_object_or_404(Comment, id=comment_id)
    existing_vote = Vote.objects.filter(user=request.user, comment=comment).first() # to get and check the existing vote if the user has already voted
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            existing_vote.delete() # if the user clicks the same vote type, remove the vote
            action = 'removed'
        else:
            existing_vote.vote_type = vote_type # if the user clicks different vote type, change the vote
            existing_vote.save()
            action = 'changed'
    else:
        Vote.objects.create(user=request.user, comment=comment, vote_type=vote_type) # to create a new vote
        action = 'added'
    # to get the updated vote counts
    upvotes = comment.upvote_count()
    downvotes = comment.downvote_count()
    return JsonResponse({
        'status': 'success',
        'action': action,
        'upvotes': upvotes,
        'downvotes': downvotes
    }) 