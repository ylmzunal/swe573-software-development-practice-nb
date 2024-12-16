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


# a function to display the profile of the current user
@login_required
def profile_view(request):
    # getting data related to the current user
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at') # to get the posts of the current user
    voted_posts = Post.objects.filter( # to get the posts the current user has voted on
        votes__user=request.user
    ).select_related('author').prefetch_related('comments').order_by('-votes__created_at') 
    commented_posts = Post.objects.filter( # to get the posts the current user has commented on
        comments__author=request.user
    ).exclude(
        author=request.user
    ).select_related('author').prefetch_related('comments').distinct().order_by('-comments__created_at') 
    followed_posts = Post.objects.filter( # to get the posts the current user is following
        followers__user=request.user
    ).select_related('author').prefetch_related('comments').order_by('-followers__followed_at')
    following_users = User.objects.filter( # to get the users the current user is following
        followers__user=request.user
    ).order_by('-followers__followed_at')
    follower_users = User.objects.filter( # to get the users who follow the current user
        following__following=request.user
    ).order_by('-following__followed_at')
    # to get the posts the current user has voted on
    all_posts = list(user_posts) + list(voted_posts) + list(commented_posts) + list(followed_posts)
    user_votes = {
        vote.post_id: vote 
        for vote in Vote.objects.filter(
            user=request.user, 
            post__in=all_posts
        )
    }
    return render(request, 'core/profile/profile.html', {
        "user": request.user,
        "user_posts": user_posts,
        "voted_posts": voted_posts,
        "commented_posts": commented_posts,
        "followed_posts": followed_posts,
        "following_users": following_users,
        "follower_users": follower_users,
        "user_votes": user_votes,
    })


# a function to edit the profile of the current user
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Profile updated successfully!')
            if form.cleaned_data.get('new_password'): # to keep the user logged in after updating the password
                update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = ProfileChangeForm(instance=request.user)
    return render(request, 'core/profile/edit_profile.html', {'form': form})


# a function to display the profile of a user   
def public_profile_view(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username)
    is_following = False
    user_post_votes = {}
    user_comment_votes = {}
    posts = Post.objects.filter(author=user).order_by('-created_at')
    comments = Comment.objects.filter(author=user).order_by('-created_at')
    followers_count = UserFollower.objects.filter(following=user).count()
    following_count = UserFollower.objects.filter(user=user).count()
    if request.user.is_authenticated: # to show if the current user is following the user
        is_following = UserFollower.objects.filter(
            user=request.user, 
            following=user
        ).exists()
        user_post_votes = {
            vote.post_id: vote 
            for vote in Vote.objects.filter(
                user=request.user, 
                post__in=posts
            )
        }   
        user_comment_votes = {
            vote.comment_id: vote 
            for vote in Vote.objects.filter(
                user=request.user, 
                comment__in=comments
            )
        }
    context = {
        'profile_user': user,
        'posts': posts,
        'comments': comments,
        'is_own_profile': request.user == user if request.user.is_authenticated else False,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'user_post_votes': user_post_votes,
        'user_comment_votes': user_comment_votes,
    }
    return render(request, 'core/profile/public_profile.html', context)