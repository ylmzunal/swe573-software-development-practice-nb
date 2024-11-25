from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from .models import Profile
from django.core.validators import validate_email
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
import re
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash

def validate_password(password): # to validate the password by checking its length, letters, numbers, and special characters
    if len(password) < 8: # to check if the password is at least 8 characters long
        return False, "Password must be at least 8 characters long."
    if not re.search(r'[A-Za-z]', password): # to check if the password includes letters
        return False, "Password must include letters."
    if not re.search(r'[0-9]', password): # to check if the password includes numbers
        return False, "Password must include numbers."
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password): # to check if the password includes special characters
        return False, "Password must include special characters."
    return True, None

class SignupView(APIView): # to create a new user using the signup form on the frontend
    def post(self, request):
        username = request.data.get('username')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        email = request.data.get('email')
        password = request.data.get('password')
        retyped_password = request.data.get('retyped_password')

        # Validating required fields
        if not all([username, first_name, last_name, email, password, retyped_password]):
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

         # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already in use.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email already in use.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validating passwords
        if password != retyped_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validating password criteria
        is_valid, error_msg = validate_password(password)
        if not is_valid:
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

        # Create user and profile
        user = User.objects.create_user(username=username, password=password,  email=email, first_name=first_name, last_name=last_name)
        
        # Log the user in
        login(request, user)

        # Redirect URL to edit profile page
        edit_profile_url = reverse('edit-profile')  # Assuming you have a URL pattern named 'edit-profile'

        return Response({'message': 'Account created successfully.', 'redirect_url': edit_profile_url}, status=status.HTTP_201_CREATED)



class LoginView(APIView): # to authenticate the user using the login form on the frontend
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return Response({'message': 'Logged in successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)



class LogoutView(APIView): # to sign out the user using the logout button on the frontend
    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)



class EditProfileView(APIView): # to edit the user's profile using the edit profile form on the frontend
    permission_classes = [IsAuthenticated] # to ensure that only authenticated users can access this view
    parser_classes = [MultiPartParser] # to enable file uploads

    def put(self, request):
        profile = request.user.profile
        user = request.user

        # Validate current password if provided
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        retyped_new_password = request.data.get('retyped_new_password')
        if current_password and new_password and retyped_new_password:
            if not user.check_password(current_password):
                return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
            if new_password != retyped_new_password:
                return Response({'error': 'New passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                is_valid, error_msg = validate_password(new_password)
                if not is_valid:
                    return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(new_password)
            update_session_auth_hash(request, user)  # to keep the user logged in after changing the password
        elif any([current_password, new_password, retyped_new_password]):
            return Response({'error': 'All password fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate and update username
        new_username = request.data.get('username', user.username)
        if new_username != user.username and User.objects.filter(username=new_username).exists():
            return Response({'error': 'Username already in use.'}, status=status.HTTP_400_BAD_REQUEST)
        user.username = new_username

        # Validate and update email
        new_email = request.data.get('email', user.email)
        if new_email != user.email and User.objects.filter(email=new_email).exists():
            return Response({'error': 'Email already in use.'}, status=status.HTTP_400_BAD_REQUEST)
        user.email = new_email

        # Update other profile fields
        profile.bio = request.data.get('bio', profile.bio)
        profile.birthday = request.data.get('birthday', profile.birthday)
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        # Save changes
        user.save()
        profile.save()

        return Response({'message': 'Profile updated successfully.'}, status=status.HTTP_200_OK)
