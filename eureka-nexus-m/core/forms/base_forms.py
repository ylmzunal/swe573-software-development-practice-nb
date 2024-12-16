from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from core.models import *
from django.core.exceptions import ValidationError
import re
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth.hashers import make_password


# a form to create a new user
class ProfileCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Must be at least 8 characters long and include numbers, letters, and special characters."
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Enter the same password as above, for verification."
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    username = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Profile
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values(): # to add bootstrap classes to all fields
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Profile.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if Profile.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken. Please choose a different one.")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("The two password fields didn't match.")
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&.,])[A-Za-z\d@$!%*?&.,]{8,}$', password1):
            raise ValidationError(
                "Password must be at least 8 characters long, include numbers, letters, and at least one special character."
            )
        return password2


