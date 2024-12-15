from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxLengthValidator
from django.conf import settings
from django.core.exceptions import ValidationError
import uuid
import os

def get_unique_profile_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('profile_pictures', filename)

def get_unique_post_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('post_images', filename)

def get_unique_multimedia_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('post_multimedia', filename)

class Profile(AbstractUser):
    profile_picture = models.ImageField(
        upload_to=get_unique_profile_path,
        null=True,
        blank=True
    )
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

    MATERIAL_CHOICES = [
        ('metal', 'Metal'),
        ('wood', 'Wood'),
        ('plastic', 'Plastic'),
        ('glass', 'Glass'),
        ('fabric', 'Fabric'),
        ('ceramic', 'Ceramic'),
        ('other', 'Other'),
    ]

    TIME_PERIOD_CHOICES = [
        ('ancient', 'Ancient'),
        ('medieval', 'Medieval'),
        ('modern', 'Modern'),
        ('contemporary', 'Contemporary'),
        ('other', 'Other'),
    ]

    OBJECT_DOMAIN_CHOICES = [
        ('art_design', 'Art and Design'),
        ('technology', 'Technology'),
        ('household', 'Household'),
        ('fashion_accessories', 'Fashion and Accessories'),
        ('tools_equipment', 'Tools and Equipment'),
        ('toys_games', 'Toys and Games'),
        ('historical_cultural', 'Historical and Cultural'),
        ('other', 'Other'),
    ]

    HARDNESS_CHOICES = [
        ('soft', 'Soft'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
        ('other', 'Other'),
    ]

    ELASTICITY_CHOICES = [
        ('elastic', 'Elastic'),
        ('non_elastic', 'Non-elastic'),
        ('semi_elastic', 'Semi-elastic'),
        ('other', 'Other'),
    ]

    TRANSPARENCY_CHOICES = [
        ('transparent', 'Transparent'),
        ('translucent', 'Translucent'),
        ('opaque', 'Opaque'),
        ('other', 'Other'),
    ]

    TEXTURE_CHOICES = [
        ('smooth', 'Smooth'),
        ('rough', 'Rough'),
        ('grainy', 'Grainy'),
        ('polished', 'Polished'),
        ('matte', 'Matte'),
        ('other', 'Other'),
    ]
    
    PATTERN_CHOICES = [
        ('plain', 'Plain'),
        ('patterned', 'Patterned'),
        ('striped', 'Striped'),
        ('checkered', 'Checkered'),
        ('marbled', 'Marbled'),
        ('other', 'Other'),
    ]
    
    TASTE_CHOICES = [
        ('sweet', 'Sweet'),
        ('salty', 'Salty'),
        ('metallic', 'Metallic'),
        ('bitter', 'Bitter'),
        ('sour', 'Sour'),
        ('other', 'Other'),
    ]
    
    SMELL_CHOICES = [
        ('odorless', 'Odorless'),
        ('chemical', 'Chemical'),
        ('earthy', 'Earthy'),
        ('metallic', 'Metallic'),
        ('fragrant', 'Fragrant'),
        ('other', 'Other'),
    ]
    
    FUNCTIONALITY_CHOICES = [
        ('rigid', 'Rigid'),
        ('moving', 'Moving'),
        ('adhesive', 'Adhesive'),
        ('other', 'Other'),
    ]
    
    WEIGHT_UNIT_CHOICES = [
        ('mg', 'Milligram'),
        ('g', 'Gram'),
        ('kg', 'Kilogram'),
        ('t', 'Ton'),
        ('oz', 'Ounce'),
        ('lb', 'Pound'),
        ('st', 'Stone'),
    ]
    
    APPROXIMATE_WEIGHT_CHOICES = [
        ('lightweight', 'Lightweight'),
        ('medium', 'Medium Weight'),
        ('heavy', 'Heavy'),
        ('other', 'Other'),
    ]
    
    SIZE_UNIT_CHOICES = [
        ('mm', 'Millimeter'),
        ('cm', 'Centimeter'),
        ('m', 'Meter'),
        ('km', 'Kilometer'),
        ('in', 'Inch'),
        ('ft', 'Foot'),
        ('yd', 'Yard'),
        ('mi', 'Mile'),
    ]

    LOCATION_CHOICES = [
        ('manual', 'Manual Input'),
        ('current', 'Current Location'),
    ]

    author = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=300)
    description = models.TextField(max_length=1000)
    image = models.ImageField(upload_to=get_unique_post_path, blank=True, null=True)
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
    texture = models.CharField(max_length=20, choices=TEXTURE_CHOICES, blank=True, null=True)
    custom_texture = models.CharField(max_length=300, blank=True, null=True)
    origin = models.CharField(max_length=300, blank=True, null=True)
    value = models.CharField(max_length=50, blank=True, null=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, blank=True, null=True)
    custom_condition = models.CharField(max_length=100, blank=True, null=True)
    smell = models.CharField(max_length=20, choices=SMELL_CHOICES, blank=True, null=True)
    custom_smell = models.CharField(max_length=300, blank=True, null=True)
    taste = models.CharField(max_length=20, choices=TASTE_CHOICES, blank=True, null=True)
    custom_taste = models.CharField(max_length=300, blank=True, null=True)
    origin_of_acquisition = models.CharField(max_length=300, blank=True, null=True)
    pattern = models.CharField(max_length=20, choices=PATTERN_CHOICES, blank=True, null=True)
    custom_pattern = models.CharField(max_length=300, blank=True, null=True)
    functionality = models.CharField(max_length=20, choices=FUNCTIONALITY_CHOICES, blank=True, null=True)
    custom_functionality = models.CharField(max_length=300, blank=True, null=True)
    other_multimedia = models.ImageField(upload_to='post_other_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown')

    # New fields
    material = models.CharField(max_length=20, choices=MATERIAL_CHOICES, blank=True, null=True)
    custom_material = models.CharField(max_length=100, blank=True, null=True)
    image_description = models.TextField(max_length=500, blank=True, null=True)
    icon_description = models.TextField(max_length=500, blank=True, null=True)
    markings = models.TextField(max_length=500, blank=True, null=True)
    print_description = models.TextField(max_length=500, blank=True, null=True)
    brand = models.CharField(max_length=200, blank=True, null=True)
    time_period = models.CharField(max_length=20, choices=TIME_PERIOD_CHOICES, blank=True, null=True)
    custom_time_period = models.CharField(max_length=100, blank=True, null=True)
    object_domain = models.CharField(max_length=30, choices=OBJECT_DOMAIN_CHOICES, blank=True, null=True)
    custom_object_domain = models.CharField(max_length=100, blank=True, null=True)
    hardness = models.CharField(max_length=20, choices=HARDNESS_CHOICES, blank=True, null=True)
    custom_hardness = models.CharField(max_length=100, blank=True, null=True)
    elasticity = models.CharField(max_length=20, choices=ELASTICITY_CHOICES, blank=True, null=True)
    custom_elasticity = models.CharField(max_length=100, blank=True, null=True)
    transparency = models.CharField(max_length=20, choices=TRANSPARENCY_CHOICES, blank=True, null=True)
    custom_transparency = models.CharField(max_length=100, blank=True, null=True)
    weight_type = models.CharField(max_length=20, choices=EXACTNESS_CHOICES, blank=True, null=True)
    approximate_weight = models.CharField(max_length=20, choices=APPROXIMATE_WEIGHT_CHOICES, blank=True, null=True)
    custom_approximate_weight = models.CharField(max_length=100, blank=True, null=True)
    exact_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    weight_unit = models.CharField(max_length=5, choices=WEIGHT_UNIT_CHOICES, blank=True, null=True)
    size_type = models.CharField(max_length=20, choices=EXACTNESS_CHOICES, blank=True, null=True)
    approximate_size = models.CharField(max_length=100, blank=True, null=True)
    width = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    height = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    depth = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    size_unit = models.CharField(max_length=5, choices=SIZE_UNIT_CHOICES, blank=True, null=True)
    location = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return self.title

    def has_answer_comment(self):
        """Check if the post has at least one comment marked as answer"""
        return self.comments.filter(tag='answer').exists()

    def upvote_count(self):
        return self.votes.filter(vote_type='up').count()
    
    def downvote_count(self):
        return self.votes.filter(vote_type='down').count()

class PostFollower(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followed_posts')
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='followers')
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} follows {self.post.title}"

class WikidataTag(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='wikidata_tags')
    wikidata_id = models.CharField(max_length=20)
    label = models.CharField(max_length=100)
    link = models.CharField(max_length=300, blank=True, null=True)

    def __str__(self):
        return f"{self.label} ({self.wikidata_id})"

    def save(self, *args, **kwargs):
        if not self.link:
            self.link = f"https://www.wikidata.org/wiki/{self.wikidata_id}"
        super().save(*args, **kwargs)

class PostAttribute(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='attributes')
    name = models.CharField(max_length=100)
    value = models.TextField()
    instance_id = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name', 'instance_id']

class PostMultimedia(models.Model):
    MULTIMEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='multimedia_files')
    file = models.FileField(upload_to=get_unique_multimedia_path)
    file_type = models.CharField(max_length=20, choices=MULTIMEDIA_TYPES)
    title = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', 'uploaded_at']

    def __str__(self):
        return f"{self.get_file_type_display()} for {self.post.title}"

    def get_file_extension(self):
        return self.file.name.split('.')[-1].lower()

    def is_image(self):
        return self.get_file_extension() in ['jpg', 'jpeg', 'png', 'gif', 'webp']

    def is_video(self):
        return self.get_file_extension() in ['mp4', 'webm', 'ogg']

    def is_audio(self):
        return self.get_file_extension() in ['mp3', 'wav', 'ogg']

    def is_document(self):
        return self.get_file_extension() in ['pdf', 'doc', 'docx', 'txt']

class Comment(models.Model):
    TAG_CHOICES = [
        ('question', 'Question'),
        ('hint', 'Hint'),
        ('answer', 'Answer'),
    ]

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    tag = models.CharField(max_length=10, choices=TAG_CHOICES, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.post.title}'

    def get_replies(self):
        return Comment.objects.filter(parent=self).order_by('created_at')

    def can_tag_as_answer(self, user):
        """Check if user can tag this comment as an answer"""
        return user == self.post.author

    def can_edit_tag(self, user):
        """Check if user can edit the tag of this comment"""
        return user == self.post.author and not self.is_deleted

    def save(self, *args, **kwargs):
        # Check if this is an existing comment being modified
        if self.pk:
            old_instance = Comment.objects.get(pk=self.pk)
            had_answer = old_instance.tag == 'answer'
        else:
            had_answer = False

        super().save(*args, **kwargs)

        # Check if answer status changed and update post status if needed
        if had_answer != (self.tag == 'answer') or self.is_deleted:
            self.update_post_status()

    def update_post_status(self):
        """Update post status based on answer comments"""
        if self.post.status == 'solved' and not self.post.has_answer_comment():
            # Only return True if the status actually changed
            old_status = self.post.status
            self.post.status = 'unknown'
            self.post.save()
            return old_status != 'unknown'  # Return True only if status changed
        return False

    def delete(self, *args, **kwargs):
        post = self.post
        had_answer = self.tag == 'answer'
        super().delete(*args, **kwargs)
        if had_answer and not post.has_answer_comment():
            post.status = 'unknown'
            post.save()

    def upvote_count(self):
        return self.votes.filter(vote_type='up').count()
    
    def downvote_count(self):
        return self.votes.filter(vote_type='down').count()

class Vote(models.Model):
    VOTE_CHOICES = [
        ('up', 'Upvote'),
        ('down', 'Downvote'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE, related_name='votes', null=True, blank=True)
    vote_type = models.CharField(max_length=4, choices=VOTE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            ('user', 'post'),
            ('user', 'comment')
        ]
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(post__isnull=False, comment__isnull=True) |
                    models.Q(post__isnull=True, comment__isnull=False)
                ),
                name='vote_only_on_post_or_comment'
            )
        ]

    def clean(self):
        if self.vote_type not in ['up', 'down']:
            raise ValidationError('Invalid vote type')
        if bool(self.post) == bool(self.comment):
            raise ValidationError('Vote must be either on a post or a comment, not both or neither')
