from django import template
from django.utils.safestring import mark_safe
import json
import re

register = template.Library()


# a filter to get an item from a dictionary using bracket notation
@register.filter
def get_item(dictionary, key):
    if dictionary is None:
        return None
    return dictionary.get(str(key)) 


# a filter to check if a user is following a post
@register.filter
def is_following(post, user):
    if not user.is_authenticated:
        return False
    return post.followers.filter(user=user).exists() 


# a filter to split a string by the given delimiter
@register.filter(name='split')
def split(value, arg):
    return value.split(arg)


# a filter to get the all of the non-empty attributes of a post
@register.filter(name='object_attributes')
def object_attributes(post):
    if not post:
        return []
    attributes = []
    fields = [
        ('size', 'Size'), ('colour', 'Color'), ('shape', 'Shape'),
        ('weight', 'Weight'), ('texture', 'Texture'), ('origin', 'Origin'),
        ('value', 'Value'), ('condition', 'Condition'), ('smell', 'Smell'),
        ('taste', 'Taste'), ('origin_of_acquisition', 'Origin of Acquisition'),
        ('pattern', 'Pattern'), ('functionality', 'Functionality'),
        ('material', 'Material'), ('time_period', 'Time Period'),
        ('object_domain', 'Object Domain'), ('hardness', 'Hardness'),
        ('transparency', 'Transparency'), ('elasticity', 'Elasticity'),
    ]
    
    for field_name, label in fields:
        value = getattr(post, field_name, None)
        if value:
            exactness = None
            if field_name in ['size', 'weight']:
                exactness = getattr(post, f'{field_name}_exactness', None)
            
            attributes.append({
                'name': field_name,
                'label': label,
                'value': value,
                'exactness': exactness
            })
    
    return attributes


# a filter to get the custom value for a field
@register.filter(name='get_custom_value')
def get_custom_value(post, field_name):
    return getattr(post, f'custom_{field_name}', '')


# a filter to get the custom field for a given field name
@register.filter(name='get_custom_field')
def get_custom_field(form, field_name):
    custom_field_name = f'custom_{field_name}'
    if hasattr(form, 'fields') and custom_field_name in form.fields:
        return form[custom_field_name]
    return None 


# a filter to parse a JSON string into a Python object
@register.filter
def parse_json(value):
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value


# a filter to get the custom value from a JSON-encoded attribute value
@register.filter
def get_custom_value_from_json(attribute):
    try:
        data = json.loads(attribute.value)
        return data.get('custom_value', '')
    except (json.JSONDecodeError, TypeError, AttributeError):
        return ''


# a filter to add a CSS class to a form field
@register.filter(name='add_class')
def add_class(field, css_class):
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    return field


@register.filter(name='add_attrs')
def add_attrs(field, attrs):
    attr_name, attr_value = attrs.split(':')
    return field.as_widget(attrs={attr_name: attr_value})