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


# a function to follow a post
@login_required
def toggle_follow_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        try:
            follow = PostFollower.objects.filter(user=request.user, post=post) # to get the follow relationship to check if the user is following the post
            if follow.exists():
                follow.delete() # to delete the follow relationship (to unfollow the post)
                is_following = False
            else:
                PostFollower.objects.create(user=request.user, post=post) # to create the follow relationship (to follow the post)
                is_following = True
            return JsonResponse({
                'status': 'success',
                'is_following': is_following
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)


# a function to follow a user
@login_required
def toggle_follow_user(request, username):
    if request.method == 'POST':
        User = get_user_model()
        user_to_follow = get_object_or_404(User, username=username)
        if request.user == user_to_follow: # to check if the user is not trying to follow themselves
            return JsonResponse({
                'status': 'error',
                'message': 'You cannot follow yourself'
            }, status=400)
        try:
            follow = UserFollower.objects.filter(user=request.user, following=user_to_follow) # to get the follow relationship to check if the user is following the user
            if follow.exists():
                follow.delete() # to delete the follow relationship (to unfollow the user)
                is_following = False
            else:
                UserFollower.objects.create(user=request.user, following=user_to_follow) # to create the follow relationship (to follow the user)
                is_following = True
            followers_count = UserFollower.objects.filter(following=user_to_follow).count()
            return JsonResponse({
                'status': 'success',
                'is_following': is_following,
                'followers_count': followers_count
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)



