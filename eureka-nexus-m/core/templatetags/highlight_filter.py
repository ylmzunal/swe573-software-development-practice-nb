from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter(name='highlight')
def highlight(text, search):
    if not search:
        return text
    search = re.escape(search)
    pattern = re.compile(f'({search})', re.IGNORECASE)
    return mark_safe(pattern.sub(r'<span class="highlight">\1</span>', str(text))) 