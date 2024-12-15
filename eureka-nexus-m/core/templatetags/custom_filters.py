from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using bracket notation"""
    if dictionary is None:
        return None
    return dictionary.get(str(key)) 

@register.filter
def is_following(post, user):
    """Check if a user is following a post"""
    if not user.is_authenticated:
        return False
    return post.followers.filter(user=user).exists() 