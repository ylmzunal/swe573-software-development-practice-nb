from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from datetime import date
from authentication.models import Profile

class AuthenticationTestCase(TestCase):
    def setUp(self): # to create a user before running the tests
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com', first_name="test", last_name="user")
        # No need to manually create a Profile, the signal will handle it

    def test_signup(self): # to test the signup endpoint with a new user
        response = self.client.post('/authentication/signup/', {
            "username": "iron-man",
            'first_name': 'Tony',
            'last_name': 'Stark',
            'email': 'tony.stark@stark.com',
            'password': 'Password123!',
            'retyped_password': 'Password123!',
        })
        if response.status_code != 201:
            print(response.content)  # Print the response content for debugging
        self.assertEqual(response.status_code, 201)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Account created successfully.')

    def test_login(self): # to test the login endpoint with an existing user
        response = self.client.post('/authentication/login/', {'username': 'testuser', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Logged in successfully')

    def test_logout(self): # to test the logout endpoint with an authenticated user
        self.client.post('/authentication/login/', {'username': 'testuser', 'password': 'testpassword'})
        response = self.client.post('/authentication/logout/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Logged out successfully')

    def test_edit_profile(self): # to test the edit profile endpoint with an authenticated user
        user = User.objects.create_user(username='iron-man', email='tony.stark@stark.com', password='Password123!')
        # No need to manually create a Profile, the signal will handle it
        self.client.force_authenticate(user=user)

        response = self.client.put('/authentication/edit-profile/', {
            'bio': 'This is my new bio.',
            'birthday': date.today().isoformat(),
            'first_name': 'Antony',
            'last_name': 'Spark'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Profile updated successfully.')