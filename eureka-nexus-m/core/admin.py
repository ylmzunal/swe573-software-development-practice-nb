from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile
from .forms import ProfileCreationForm, ProfileChangeForm

class ProfileAdmin(UserAdmin):
    add_form = ProfileCreationForm
    form = ProfileChangeForm
    model = Profile
    list_display = ['username', 'email', 'first_name', 'last_name']

admin.site.register(Profile, ProfileAdmin)
