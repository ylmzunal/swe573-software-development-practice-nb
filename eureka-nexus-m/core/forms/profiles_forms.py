from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from core.models import *
from django.core.exceptions import ValidationError
import re
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth.hashers import make_password


# a form to edit the profile
class ProfileChangeForm(forms.ModelForm):
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Enter a new password if you want to change it."
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Re-enter the new password to confirm."
    )

    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'email', 'profile_picture', 'birthday', 'bio')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'})
        }

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

