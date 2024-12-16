from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile, Post, PostFollower, WikidataTag, PostAttribute, PostMultimedia, Comment, Vote, UserFollower
from .forms import ProfileCreationForm, ProfileChangeForm

class ProfileAdmin(UserAdmin):
    model = Profile
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'bio', 'birthday')
    fieldsets = UserAdmin.fieldsets + (  # Add custom fields to the admin interface
        ('Additional Info', {
            'fields': ('profile_picture', 'bio', 'birthday'),
        }),
    )

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post)
admin.site.register(PostFollower)
admin.site.register(WikidataTag)
admin.site.register(PostAttribute)
admin.site.register(PostMultimedia)
admin.site.register(Comment)
admin.site.register(Vote)
admin.site.register(UserFollower)
