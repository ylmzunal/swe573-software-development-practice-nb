from django import template
import json
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='serialize_tags')
def serialize_tags(tags):
    """Serialize wikidata tags for JSON output"""
    tag_list = [{'wikidata_id': tag.wikidata_id, 
                 'label': tag.label, 
                 'link': tag.link} for tag in tags]
    return mark_safe(json.dumps(tag_list)) 