from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from datetime import date
from authentication.models import Profile
from rest_framework_simplejwt.tokens import RefreshToken

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
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Account created successfully. Please check your email to activate your account.')

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

class EmailValidationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
    def test_send_activation_email(self):
        response = self.client.post('/authentication/signup/', {
            'username': 'iron-man',
            'first_name': 'Tony',
            'last_name': 'Stark',
            'email': "tony.stark@stark.com",
            'password': 'Password123!',
            'retyped_password': 'Password123!',
        })
        print(f"Signup Response: {response.data}")  # Debugging output
        self.assertEqual(response.status_code, 201)
    def test_activate_account(self):
        # Create a user with is_active=False
        user = User.objects.create_user(
        username='tony.stark@stark.com', 
        email='tony.stark@stark.com', 
        password='IronMan@3000', 
        is_active=False
        )

        # Generate refresh token for the user
        token = str(RefreshToken.for_user(user))

        # Verify activation URL and response
        response = self.client.get(f'/authentication/activate/{token}/')  # Ensure the URL matches your project's configuration
        print(f"Activation Response: {response.data}")

        # Reload user data and verify activation
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertEqual(response.status_code, 200)



class EditProfileEmailChangeTestCase(TestCase):
    def setUp(self): # to create a user before running the tests
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com', first_name="test", last_name="user")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_email_change_triggers_revalidation(self):
        response = self.client.put('/authentication/edit-profile/', {'email': 'new.email@example.com'})
        self.user.refresh_from_db()
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self.user.is_active)  # Account should be deactivated
        self.assertEqual(self.user.email, 'new.email@example.com')
