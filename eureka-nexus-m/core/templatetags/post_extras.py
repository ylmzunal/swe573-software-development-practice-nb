from django import template
import json

register = template.Library()

@register.filter(name='split')
def split(value, arg):
    """Split a string by the given delimiter"""
    return value.split(arg)

@register.filter(name='object_attributes')
def object_attributes(post):
    """Returns a list of all non-empty attributes of a post"""
    if not post:
        return []
        
    attributes = []
    fields = [
        ('size', 'Size'), ('colour', 'Color'), ('shape', 'Shape'),
        ('weight', 'Weight'), ('texture', 'Texture'), ('origin', 'Origin'),
        ('value', 'Value'), ('condition', 'Condition'), ('smell', 'Smell'),
        ('taste', 'Taste'), ('origin_of_acquisition', 'Origin of Acquisition'),
        ('pattern', 'Pattern'), ('functionality', 'Functionality')
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

@register.filter(name='get_custom_value')
def get_custom_value(post, field_name):
    """Returns the custom value for a field if it exists"""
    return getattr(post, f'custom_{field_name}', '')

@register.filter(name='get_custom_field')
def get_custom_field(form, field_name):
    """Returns the custom field for a given field name"""
    custom_field_name = f'custom_{field_name}'
    if hasattr(form, 'fields') and custom_field_name in form.fields:
        return form[custom_field_name]
    return None 

@register.filter
def parse_json(value):
    """
    Parse a JSON string into a Python object.
    If parsing fails, return the original value.
    """
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return value

@register.filter
def get_custom_value_from_json(attribute):
    """
    Get custom value from a JSON-encoded attribute value
    """
    try:
        data = json.loads(attribute.value)
        return data.get('custom_value', '')
    except (json.JSONDecodeError, TypeError, AttributeError):
        return ''