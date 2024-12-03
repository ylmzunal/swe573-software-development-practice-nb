from django import template
import json

register = template.Library()

@register.filter(name='serialize_tags')
def serialize_tags(tags):
    serialized_tags = [{
        'type': tag.tag_type,
        'id': tag.wikidata_id,
        'label': tag.label,
        'link': tag.link
    } for tag in tags]
    print("Serializing tags:", serialized_tags)
    return json.dumps(serialized_tags) 