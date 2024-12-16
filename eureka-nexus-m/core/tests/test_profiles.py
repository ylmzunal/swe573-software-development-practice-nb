from django.test import TestCase
from core.forms import *
from core.models import Profile
from django.urls import reverse
from django.contrib.auth import get_user_model


# to access the user model
User = get_user_model()

# unit tests for profile view
class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='StrongPass1!')
        self.client.login(username='testuser', password='StrongPass1!')

    def test_profile_view(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'testuser')  # Check if username is in the response


# unit tests for profile change form
class ProfileChangeFormTest(TestCase):
    def setUp(self):
        self.user = Profile.objects.create(username='testuser', email='test@example.com', password='StrongPass1!', bio='This is a bio.')

    def test_valid_change_form(self):
        form_data = {
            'email': 'updated@example.com',
            'bio': 'Updated bio.'
        }
        form = ProfileChangeForm(data=form_data, instance=self.user)
        if not form.is_valid():
            print(form.errors)
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        form_data = {
            'email': 'updated@example.com',
            'new_password': 'NewStrongPass1!',
            'confirm_password': 'DifferentPass1!',
        }
        form = ProfileChangeForm(data=form_data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertIn('The new passwords do not match.', form.errors['__all__'])
