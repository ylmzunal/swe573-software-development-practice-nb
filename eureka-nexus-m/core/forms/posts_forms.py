from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from core.models import *
from django.core.exceptions import ValidationError
import re
from django.forms import modelformset_factory, inlineformset_factory
from django.contrib.auth.hashers import make_password


# a form to create a new post
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'image', 'size', 'size_exactness', 'colour', 'custom_colour',
                  'shape', 'custom_shape', 'weight', 'weight_exactness', 'texture', 'origin', 'value',
                  'condition', 'custom_condition', 'smell', 'taste', 'origin_of_acquisition', 'pattern',
                  'functionality', 'other_multimedia', 'material', 'custom_material',
                  'image_description', 'icon_description', 'markings', 'print_description',
                  'brand', 'time_period', 'custom_time_period', 'object_domain', 'custom_object_domain',
                  'hardness', 'custom_hardness', 'elasticity', 'custom_elasticity',
                  'transparency', 'custom_transparency',
                  'texture', 'custom_texture',
                  'pattern', 'custom_pattern',
                  'taste', 'custom_taste',
                  'smell', 'custom_smell',
                  'functionality', 'custom_functionality',
                  'weight_type', 'approximate_weight', 'custom_approximate_weight',
                  'exact_weight', 'weight_unit',
                  'size_type', 'approximate_size',
                  'width', 'height', 'depth', 'size_unit',
        ]
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
            'image_description': forms.Textarea(attrs={'rows': 3, 'maxlength': 500}),
            'icon_description': forms.Textarea(attrs={'rows': 3, 'maxlength': 500}),
            'markings': forms.Textarea(attrs={'rows': 3, 'maxlength': 500}),
            'print_description': forms.Textarea(attrs={'rows': 3, 'maxlength': 500}),
            'brand': forms.TextInput(attrs={'maxlength': 200}),
            'custom_material': forms.TextInput(attrs={'maxlength': 100}),
            'custom_time_period': forms.TextInput(attrs={'maxlength': 100}),
            'custom_object_domain': forms.TextInput(attrs={'maxlength': 100}),
            'custom_hardness': forms.TextInput(attrs={'maxlength': 100}),
            'custom_elasticity': forms.TextInput(attrs={'maxlength': 100}),
            'custom_transparency': forms.TextInput(attrs={'maxlength': 100}),
            'custom_texture': forms.TextInput(attrs={'maxlength': 300}),
            'custom_pattern': forms.TextInput(attrs={'maxlength': 300}),
            'custom_taste': forms.TextInput(attrs={'maxlength': 300}),
            'custom_smell': forms.TextInput(attrs={'maxlength': 300}),
            'custom_functionality': forms.TextInput(attrs={'maxlength': 300}),
            'custom_approximate_weight': forms.TextInput(attrs={'maxlength': 100}),
            'exact_weight': forms.NumberInput(attrs={'step': '0.01'}),
            'approximate_size': forms.TextInput(attrs={'maxlength': 100}),
            'width': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Width (x)'}),
            'height': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Height (y)'}),
            'depth': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'Depth (z)'}),
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

