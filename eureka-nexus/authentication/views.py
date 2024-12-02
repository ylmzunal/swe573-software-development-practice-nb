from django.shortcuts import render

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from .models import Profile
from .serializers import UserSerializer
from django.core.validators import validate_email
import re
from django.templatetags.static import static
from django.core.exceptions import ValidationError

# editing profile
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import TokenError
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


class SignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            # Check if username already exists
            if User.objects.filter(username=request.data.get('username')).exists():
                return Response({'error': 'Username is already taken.'}, 
                              status=status.HTTP_400_BAD_REQUEST)

            # Check if email already exists
            if User.objects.filter(email=request.data.get('email').lower()).exists():
                return Response({'error': 'Email is already registered.'}, 
                              status=status.HTTP_400_BAD_REQUEST)

            # Validate password match
            if request.data.get('password') != request.data.get('retyped_password'):
                return Response({'error': 'Passwords do not match.'}, 
                              status=status.HTTP_400_BAD_REQUEST)

            # Validate password strength
            is_valid, error_msg = validate_password(request.data.get('password'))
            if not is_valid:
                return Response({'error': error_msg}, 
                              status=status.HTTP_400_BAD_REQUEST)

            # Create user with serializer
            serializer = UserSerializer(data={
                'username': request.data.get('username'),
                'email': request.data.get('email').lower(),
                'password': request.data.get('password'),
                'first_name': request.data.get('first_name'),
                'last_name': request.data.get('last_name')
            })
            
            if serializer.is_valid():
                user = serializer.save()
                
                # Create Profile
                Profile.objects.create(user=user)

                # Generate tokens
                refresh = RefreshToken.for_user(user)

                return Response({
                    'message': 'Account created successfully.',
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }, status=status.HTTP_201_CREATED)
            
            return Response({'error': serializer.errors}, 
                          status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error during signup: {e}")
            return Response({'error': str(e)}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        




class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            # Validate input fields
            if not username or not password:
                return Response({'error': 'Username and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

            # Authenticate user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if not user.is_active:
                    return Response({'error': 'This account is inactive.'}, status=status.HTTP_401_UNAUTHORIZED)
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'message': 'Logged in successfully.',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name
                    },
                    'access': str(refresh.access_token),
                    'refresh': str(refresh)
                }, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return Response({'error': 'An unexpected error occurred during login.'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            token = request.data.get('refresh')
            if not token:
                return Response({'error': 'Refresh token is required.'}, 
                              status=status.HTTP_400_BAD_REQUEST)

            # Blacklist the refresh token
            try:
                refresh_token = RefreshToken(token)
                refresh_token.blacklist()
                
                # Log the successful logout
                logger.info(f"User {request.user.username} logged out successfully")
                
                return Response({'message': 'Logged out successfully.'}, 
                              status=status.HTTP_200_OK)
                              
            except TokenError as e:
                logger.warning(f"Invalid token during logout for user {request.user.username}: {e}")
                return Response({'error': 'Invalid refresh token.'}, 
                              status=status.HTTP_400_BAD_REQUEST)
                              
        except Exception as e:
            logger.error(f"Logout failed for user {request.user.username}: {e}")
            return Response({'error': 'An unexpected error occurred during logout.'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EditProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def put(self, request):
        user = request.user
        try:
            profile = user.profile
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Password update
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        retyped_new_password = request.data.get('retyped_new_password')
        
        if any([current_password, new_password, retyped_new_password]):
            if not all([current_password, new_password, retyped_new_password]):
                return Response({'error': 'All password fields are required.'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not user.check_password(current_password):
                return Response({'error': 'Current password is incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
                
            if new_password != retyped_new_password:
                return Response({'error': 'New passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)
                
            try:
                validate_password(new_password)
                user.set_password(new_password)
                update_session_auth_hash(request, user)
            except ValidationError as e:
                return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        # Username update
        new_username = request.data.get('username')
        if new_username and new_username != user.username:
            if User.objects.filter(username=new_username).exists():
                return Response({'error': 'Username already in use.'}, status=status.HTTP_400_BAD_REQUEST)
            user.username = new_username

        # Email update
        new_email = request.data.get('email')
        if new_email and new_email.lower() != user.email.lower():
            if User.objects.filter(email=new_email.lower()).exists():
                return Response({'error': 'Email already in use.'}, status=status.HTTP_400_BAD_REQUEST)
            user.email = new_email.lower()

        # Basic profile updates
        if 'bio' in request.data:
            profile.bio = request.data['bio']
        if 'birthday' in request.data:
            try:
                profile.birthday = request.data['birthday']
            except ValueError:
                return Response({'error': 'Invalid date format.'}, status=status.HTTP_400_BAD_REQUEST)
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']

        # Profile picture update
        if 'profile_picture' in request.FILES:
            profile.profile_picture = request.FILES['profile_picture']

        try:
            user.save()
            profile.save()
            return Response({
                'message': 'Profile updated successfully.',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'bio': profile.bio,
                    'birthday': profile.birthday,
                    'profile_picture': profile.profile_picture.url if profile.profile_picture else None
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            profile = user.profile
            return Response({
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'bio': profile.bio,
                'birthday': profile.birthday,
                'profile_picture': profile.profile_picture.url if profile.profile_picture else static('img/profile_picture.png'),
                'date_joined': user.date_joined,
                'last_login': user.last_login
            }, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            return Response({'error': 'User profile not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
