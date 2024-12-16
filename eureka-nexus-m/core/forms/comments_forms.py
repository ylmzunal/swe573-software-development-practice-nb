from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from core.models import *
from django.core.exceptions import ValidationError
import re
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth.hashers import make_password


# a form to create a new comment
class CommentForm(forms.ModelForm):
    def __init__(self, *args, user=None, post=None, instance=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.post = post
        
        choices = [('', 'No tag')] # to set the tag choices based on permissions
        if user and post:
            # regular users can only set question or hint tags when creating
            if not instance:  # tag can be set only when creating a new comment
                choices.extend([
                    ('question', 'Question'),
                    ('hint', 'Hint'),
                ])
            if user == post.author: # post owner can mark as answer anytime
                choices.extend([('answer', 'Answer')])
        
        self.fields['tag'] = forms.ChoiceField(
            choices=choices,
            required=False,
            widget=forms.Select(attrs={'class': 'form-select'})
        )

    def clean_tag(self):
        tag = self.cleaned_data.get('tag')
        if tag == 'answer' and self.user != self.post.author:
            raise forms.ValidationError("Only the post owner can add answer tags.")
        return tag

    class Meta:
        model = Comment
        fields = ['content', 'tag']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment...'
            })
        }
