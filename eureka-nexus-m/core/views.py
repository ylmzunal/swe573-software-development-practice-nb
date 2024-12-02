from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import ProfileCreationForm, ProfileChangeForm
from django.contrib import messages
from .models import Profile
from django import forms
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'core/home.html')


def signup_view(request):
    if request.method == 'POST':
        form = ProfileCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('profile')
    else:
        form = ProfileCreationForm()
    return render(request, 'core/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

def profile_view(request):
    return render(request, 'core/profile.html', {"user": request.user})

from django.contrib import messages  # To provide feedback to the user
from django.contrib.auth import update_session_auth_hash

def edit_profile(request):
    if request.method == 'POST':
        form = ProfileChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()  # Save the updated profile and password
            # Keep the user logged in after updating the password
            if form.cleaned_data.get('new_password'):
                update_session_auth_hash(request, user)
            return redirect('profile')  # Redirect to the profile page
    else:
        form = ProfileChangeForm(instance=request.user)

    return render(request, 'core/edit_profile.html', {'form': form})