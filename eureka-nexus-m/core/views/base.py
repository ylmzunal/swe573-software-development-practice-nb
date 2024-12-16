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



# a function to render the home page
def home(request):
    recent_posts = Post.objects.all().order_by('-created_at')[:6] # to get the 6 most recent posts to display on the home page
    user_votes = {} # to get the user's votes
    if request.user.is_authenticated: # to check and display if the user is signed in and has voted on the recent posts
        user_votes = {
            vote.post_id: vote 
            for vote in Vote.objects.filter(user=request.user, post__in=recent_posts)
        }
    return render(request, 'core/home.html', {
        "recent_posts": recent_posts,
        "user_votes": user_votes
    })


# a function to render the signup page
def signup_view(request):
    if request.method == 'POST':
        form = ProfileCreationForm(request.POST)
        if form.is_valid(): # to check if the form is valid and to save the user, log them in and redirect to the profile page
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('profile')
    else:
        form = ProfileCreationForm()
    return render(request, 'core/signup.html', {'form': form})


# a function to render the login page
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid(): # to check if the form is valid and to authenticate the user, log them in and redirect to the home page
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})


# a function to logout the user
@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


# a function to delete the user's account
@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        
        if user is not None: # to check if the user is authenticated and to delete their account
            try: # to get all the user's posts and set the author of the posts to None, making them anonymous, and delete the user's account
                posts = Post.objects.filter(author=user)
                for post in posts: 
                    post.author = None
                    post.save()
                user.delete()         
                messages.success(request, 'Your account has been successfully deleted.')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'An error occurred while deleting your account: {str(e)}')
                return redirect('profile')
        else:
            messages.error(request, 'Invalid password. Please try again.')
            return redirect('profile')
    return redirect('profile')