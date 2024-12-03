from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator
from django.conf import settings

class Profile(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(default="Hello, I am a member of this platform.")
    birthday = models.DateField(null=True, blank=True)


#profile_picture = models.ImageField(upload_to='profile_pics/', default='static/img/default_profile_pic.jpg')


class Post(models.Model):
    EXACTNESS_CHOICES = [
        ('exact', 'Exact'),
        ('approximate', 'Approximate'),
    ]
    
    COLOUR_CHOICES = [
        ('red', 'Red'),
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('yellow', 'Yellow'),
        ('black', 'Black'),
        ('white', 'White'),
        ('brown', 'Brown'),
        ('grey', 'Grey'),
        ('other', 'Other'),
    ]
    
    SHAPE_CHOICES = [
        ('round', 'Round'),
        ('square', 'Square'),
        ('rectangular', 'Rectangular'),
        ('triangular', 'Triangular'),
        ('oval', 'Oval'),
        ('irregular', 'Irregular'),
        ('other', 'Other'),
    ]
    
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('like_new', 'Like New'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('unknown', 'Unknown'),
        ('solved', 'Solved'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    description = models.TextField(max_length=1000)
    image = models.ImageField(upload_to='post_pics/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Optional fields
    size = models.CharField(max_length=50, blank=True, null=True)
    size_exactness = models.CharField(max_length=20, choices=EXACTNESS_CHOICES, blank=True, null=True)
    colour = models.CharField(max_length=20, choices=COLOUR_CHOICES, blank=True, null=True)
    custom_colour = models.CharField(max_length=50, blank=True, null=True)
    shape = models.CharField(max_length=20, choices=SHAPE_CHOICES, blank=True, null=True)
    custom_shape = models.CharField(max_length=300, blank=True, null=True)
    weight = models.CharField(max_length=50, blank=True, null=True)
    weight_exactness = models.CharField(max_length=20, choices=EXACTNESS_CHOICES, blank=True, null=True)
    texture = models.CharField(max_length=300, blank=True, null=True)
    origin = models.CharField(max_length=300, blank=True, null=True)
    value = models.CharField(max_length=50, blank=True, null=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, blank=True, null=True)
    custom_condition = models.CharField(max_length=100, blank=True, null=True)
    smell = models.CharField(max_length=300, blank=True, null=True)
    taste = models.CharField(max_length=300, blank=True, null=True)
    origin_of_acquisition = models.CharField(max_length=300, blank=True, null=True)
    pattern = models.CharField(max_length=300, blank=True, null=True)
    functionality = models.CharField(max_length=300, blank=True, null=True)
    other_multimedia = models.ImageField(upload_to='post_other_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')

    def __str__(self):
        return self.title

class WikidataTag(models.Model):
    TAG_TYPES = [
        ('images', 'Images'),
        ('icons', 'Icons'),
        ('markings', 'Markings'),
        ('print', 'Print'),
        ('brand', 'Brand'),
        ('time_period', 'Time Period'),
        ('object_domain', 'Object Domain'),
        ('other', 'Other'),
    ]
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='wikidata_tags')
    tag_type = models.CharField(max_length=20, choices=TAG_TYPES)
    wikidata_id = models.CharField(max_length=20)  # Store Wikidata Q-number
    label = models.CharField(max_length=100)  # Store human-readable label
    link = models.CharField(max_length=300, blank=True, null=True) # Store link to Wikidata item

    def __str__(self):
        return f"{self.tag_type}: {self.label}"
