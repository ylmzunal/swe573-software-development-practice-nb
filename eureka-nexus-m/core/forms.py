from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Profile, Post, WikidataTag
from django.core.exceptions import ValidationError
import re
from django.forms import modelformset_factory, inlineformset_factory

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
        # Add Bootstrap classes to all fields
        for field in self.fields.values():
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



from django.contrib.auth.hashers import make_password

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



class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'image', 'size', 'size_exactness', 'colour', 'custom_colour',
                  'shape', 'custom_shape', 'weight', 'weight_exactness', 'texture', 'origin', 'value',
                  'condition', 'custom_condition', 'smell', 'taste', 'origin_of_acquisition', 'pattern',
                  'functionality', 'other_multimedia']
        widgets = {
            'title': forms.TextInput(attrs={'maxlength': 300}),
            'description': forms.Textarea(attrs={'rows': 5, 'maxlength': 1000}),
            'size': forms.TextInput(attrs={'maxlength': 50}),
            'custom_colour': forms.TextInput(attrs={'maxlength': 50}),
            'custom_shape': forms.TextInput(attrs={'maxlength': 300}),
            'weight': forms.TextInput(attrs={'maxlength': 50}),
            'texture': forms.TextInput(attrs={'maxlength': 300}),
            'origin': forms.TextInput(attrs={'maxlength': 300}),
            'value': forms.TextInput(attrs={'maxlength': 50}),
            'custom_condition': forms.TextInput(attrs={'maxlength': 100}),
            'smell': forms.TextInput(attrs={'maxlength': 300}),
            'taste': forms.TextInput(attrs={'maxlength': 300}),
            'origin_of_acquisition': forms.TextInput(attrs={'maxlength': 300}),
            'pattern': forms.TextInput(attrs={'maxlength': 300}),
            'functionality': forms.TextInput(attrs={'maxlength': 300}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['image'].widget.attrs.update({
            'accept': 'image/gif,image/jpeg,image/png,image/svg+xml,image/webp,image/heic'
        })
        # Make required fields
        self.fields['title'].required = True
        self.fields['description'].required = True
        self.fields['image'].required = True
        
        # Make all other fields optional
        for field in self.fields:
            if field not in ['title', 'description', 'image']:
                self.fields[field].required = False

class WikidataTagForm(forms.ModelForm):
    class Meta:
        model = WikidataTag
        fields = ['wikidata_id', 'label', 'link']

WikidataTagFormSet = inlineformset_factory(
    Post,
    WikidataTag,
    fields=('wikidata_id', 'label', 'link'),
    extra=1,
    can_delete=True,
    validate_min=0
)



