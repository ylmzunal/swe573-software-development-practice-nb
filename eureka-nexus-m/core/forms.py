from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Profile
from django.core.exceptions import ValidationError
import re

class ProfileCreationForm(UserCreationForm):
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)
    email = forms.EmailField(max_length=254, required=True)
    username = forms.CharField(max_length=30, required=True)

    class Meta:
        model = Profile
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

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

class ProfileChangeForm(UserChangeForm):
    class Meta:
        model = Profile
        fields = ('username', 'email', 'password', 'first_name', 'last_name', 'profile_picture', 'birthday', 'bio')


from django.contrib.auth.hashers import make_password

class ProfileChangeForm(forms.ModelForm):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput,
        required=False,
        help_text="Enter a new password if you want to change it."
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        required=False,
        help_text="Re-enter the new password to confirm."
    )

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'email', 'profile_picture', 'birthday', 'bio')

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if new_password or confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("The new passwords do not match.")
            if not self._validate_password_strength(new_password):
                raise forms.ValidationError(
                    "Password must be at least 8 characters long, include numbers, letters, and special characters."
                )
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            user.password = make_password(new_password)  # Hash and save the new password
        if commit:
            user.save()
        return user

    def _validate_password_strength(self, password):
        import re
        return re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*?&.,])[A-Za-z\d@$!%*?&.,]{8,}$', password)

