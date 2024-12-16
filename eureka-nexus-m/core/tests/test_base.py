from django.test import TestCase
from core.forms import *
from core.models import Profile
from django.urls import reverse
from django.contrib.auth import get_user_model


# to access the user model
User = get_user_model()


# unit tests for profile creation form
class ProfileCreationFormTest(TestCase):
    def test_valid_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'StrongPass1!',
            'password2': 'StrongPass1!',
        }
        form = ProfileCreationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_email_already_exists(self):
        Profile.objects.create(username='testuser', email='test@example.com', password='StrongPass1!')
        form_data = {
            'username': 'newuser',
            'email': 'test@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password1': 'StrongPass1!',
            'password2': 'StrongPass1!',
        }
        form = ProfileCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)


# unit tests for signup view
class SignupViewTest(TestCase):
    def test_signup_view(self):
        response = self.client.post(reverse('signup'), {
            'username': 'testuser',
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': 'StrongPass1!',
            'password2': 'StrongPass1!',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful signup
        self.assertTrue(User.objects.filter(username='testuser').exists())


# unit tests for login view
class LoginViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass1!')

    def test_login_view(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'StrongPass1!',
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful login
        self.assertEqual(response.wsgi_request.user, self.user)
