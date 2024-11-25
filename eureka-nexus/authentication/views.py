from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from .models import Profile
from django.core.validators import validate_email
import re

# for sending activation email
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash

# editing profile
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

# email validation
from django.core.mail import send_mail
from django.contrib.sites.models import Site
from rest_framework_simplejwt.tokens import RefreshToken

# email activation endpoint
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
import logging
logger = logging.getLogger(__name__)



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


def send_activation_email(user): # to send an activation email to the user after signing up
    # Generate refresh token
    refresh = RefreshToken.for_user(user)
    activation_path = reverse('activate-account', kwargs={'token': str(refresh)})

    # Construct activation link
    current_site = Site.objects.get_current()
    activation_link = f"http://{current_site.domain}{activation_path}"
    print(f"Generated activation link: {activation_link}")

    # Send email
    send_mail(
        subject="Activate your Eureka Nexus account",
        message=f"Hi {user.first_name},\n\nClick the link below to activate your account:\n{activation_link}\n\nThank you!",
        from_email="noreply@eurekanexus.com",
        recipient_list=[user.email],
    )


class ActivateAccountView(APIView):  # to activate the user's account after clicking the activation link in the email
    permission_classes = [AllowAny]

    def get(self, request, token):
        print(f"Token received: {token}")
        try:
            # Decode refresh token to get user ID
            refresh = RefreshToken(token)
            user_id = refresh.get("user_id")
            user = User.objects.get(id=user_id)

            if user.is_active:
                return Response({'error': 'Account is already activated.'}, status=status.HTTP_400_BAD_REQUEST)

            # Activate the user's account
            user.is_active = True
            user.save()

            # Generate access and refresh tokens for login
            new_refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Account activated successfully.',
                'access': str(new_refresh.access_token),
                'refresh': str(new_refresh),
            }, status=status.HTTP_200_OK)
        except (User.DoesNotExist, TokenError) as e:
            logger.error(f"Activation error: {e}")
            return Response({'error': 'Invalid or expired token.'}, status=status.HTTP_400_BAD_REQUEST)



class SignupView(APIView): # to create a new user using the signup form on the frontend
    def post(self, request):
        try:
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
            if User.objects.filter(email=email.lower()).exists():
                return Response({'error': 'Email already in use.'}, status=status.HTTP_400_BAD_REQUEST)

            # Validating passwords
            if password != retyped_password:
                return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

            # Validating password criteria
            is_valid, error_msg = validate_password(password)
            if not is_valid:
                return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)

            # Create user and profile
            user = User.objects.create_user(username=username, password=password,  email=email.lower(), first_name=first_name, last_name=last_name)
            
            # send activation email to the user
            send_activation_email(user)
            logger.info(f"Signup successful for user {email}")
            return Response({'message': 'Account created successfully. Please check your email to activate your account.'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Unexpected error in signup: {e}")
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        if new_email.lower() != user.email.lower() and User.objects.filter(email=new_email).exists():
            return Response({'error': 'Email already in use.'}, status=status.HTTP_400_BAD_REQUEST)
        elif new_email.lower() != user.email.lower() and new_email:
            user.email = new_email.lower()
            user.is_active = False
            user.save()
            send_activation_email(user)
            return Response({'message': 'Profile updated successfully. Please check your new email to reactivate your account.'}, status=status.HTTP_200_OK)
        

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



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        profile = user.profile

        return Response({
            'name': user.first_name,
            'surname': user.last_name,
            'email': user.email,
            'bio': profile.bio,
            'birthday': profile.birthday,
            'profile_picture': profile.profile_picture.url
        }, status=status.HTTP_200_OK)
