# imports
# Django core imports
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django import forms
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import DetailView
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import update_session_auth_hash
# Third-party imports
import requests
import json
import logging
from functools import reduce
from operator import and_, or_
# Local application imports
from core.forms import *
from core.models import *


# logger is used to log messages to the console
logger = logging.getLogger(__name__)


# user is to get the current user
User = get_user_model()



# -- post display functions -- 
# a function to list all posts
def post_list(request):
    post_list = Post.objects.all().prefetch_related('comments')
    search_query = request.GET.get('search', '') # to get the search query from the request
    if search_query: # if the search query is not empty list the posts that contain the search query in the title or description
        post_list = post_list.filter(
            Q(title__icontains=search_query)
        )
    post_list = post_list.order_by('-created_at')
    paginator = Paginator(post_list, 10) # to paginate the posts
    page = request.GET.get('page') 
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    user_votes = {} # to get the user votes for the posts to be displayed in the post list
    if request.user.is_authenticated:
        user_votes = {
            vote.post_id: vote 
            for vote in Vote.objects.filter(user=request.user, post__in=posts)
        }
    context = {
        'posts': posts,
        'search_query': search_query,
        'user_votes': user_votes,
    }
    return render(request, 'core/posts/post_list.html', context)


# a function to display the details of a post
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comment_form = None
    user_vote = None
    comment_votes = {}
    if request.user.is_authenticated:
        comment_form = CommentForm(user=request.user, post=post) # to get the comment form for the post if the user is authenticated
        user_vote = Vote.objects.filter(user=request.user, post=post).first()
        comment_votes = {
            vote.comment_id: vote 
            for vote in Vote.objects.filter(
                user=request.user, 
                comment__in=post.comments.all()
            )
        }
    return render(request, 'core/posts/post_detail.html', {
        'post': post,
        'comment_form': comment_form,
        'user_vote': user_vote,
        'comment_votes': comment_votes
    })


# a class to display the details of a post
class PostDetailView(DetailView):
    model = Post
    template_name = 'core/posts/post_detail.html'
    context_object_name = 'post'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'].semantic_tags.all()
        return context



# -- post creation functions -- 
# a function to create a post
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        formset = WikidataTagFormSet(request.POST, prefix='tags') # to get the formset for the wikidata tags
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user if not request.POST.get('anonymous') else None
            post.save()
            # to check if the location data is present and if it is, create a location attribute for the post
            location_data = request.POST.get('location') 
            if location_data:
                try:
                    location_json = json.loads(location_data)
                    PostAttribute.objects.create(
                        post=post,
                        name='location',
                        value=json.dumps({
                            'display_name': location_json.get('display_name'),
                            'latitude': location_json.get('lat'),
                            'longitude': location_json.get('lon'),
                            'type': location_json.get('type')
                        })
                    )
                except json.JSONDecodeError:
                    pass
            # to handle the additional multimedia files
            multimedia_files = request.FILES.getlist('multimedia_files')            
            for index, f in enumerate(multimedia_files):
                content_type = f.content_type.lower()
                if content_type.startswith('image/'):
                    file_type = 'image'
                elif content_type.startswith('video/'):
                    file_type = 'video'
                elif content_type.startswith('audio/'):
                    file_type = 'audio'
                else:
                    file_type = 'document'
                try:
                    multimedia = PostMultimedia.objects.create(
                        post=post,
                        file=f,
                        file_type=file_type,
                        order=index
                    )
                except Exception as e:
                    print(f"Error saving file {f.name}: {str(e)}")
            # to collect attributes for the post
            attributes_to_create = []
            size_data = {}  # Dictionary to collect size-related fields by instance
            weight_data = {}  # Dictionary to collect weight-related fields by instance
            for field_name, field_value in request.POST.items():
                if '[' in field_name and ']' in field_name:
                    base_name, instance_id = field_name.split('[')
                    instance_id = instance_id.rstrip(']')
                    # to handle size fields
                    if base_name.startswith('size_') or base_name in ['width', 'height', 'depth']:
                        if instance_id not in size_data:
                            size_data[instance_id] = {}
                        size_data[instance_id][base_name] = field_value
                        continue
                    # to handle weight fields
                    if base_name.startswith('weight_') or base_name == 'exact_weight':
                        if instance_id not in weight_data:
                            weight_data[instance_id] = {}
                        weight_data[instance_id][base_name] = field_value
                        continue
                    # to handle regular attributes which do not have custom values
                    if not base_name.startswith('custom_'):
                        attribute_data = {
                            'value': field_value
                        }
                        custom_field_name = f'custom_{base_name}[{instance_id}]' # to check for custom values ("other") for the attributes
                        if field_value == 'other' and custom_field_name in request.POST:
                            attribute_data['custom_value'] = request.POST[custom_field_name]
                        attributes_to_create.append(
                            PostAttribute(
                                post=post,
                                name=base_name,
                                value=json.dumps(attribute_data),
                                instance_id=instance_id
                            )
                        )
            # to process the collected size data
            for instance_id, data in size_data.items():
                if 'size_type' in data:
                    size_attribute = {
                        'type': data['size_type']
                    }
                    if data['size_type'] == 'approximate':
                        size_attribute['approximate_size'] = data.get('approximate_size', '')
                    else:
                        size_attribute.update({
                            'width': data.get('width', ''),
                            'height': data.get('height', ''),
                            'depth': data.get('depth', ''),
                            'size_unit': data.get('size_unit', '')
                        })
                    attributes_to_create.append(
                        PostAttribute(
                            post=post,
                            name='size',
                            value=json.dumps(size_attribute),
                            instance_id=instance_id
                        )
                    )
            # to process the collected weight data
            for instance_id, data in weight_data.items():
                if 'weight_type' in data:
                    weight_attribute = {
                        'type': data['weight_type']
                    }
                    if data['weight_type'] == 'approximate':
                        weight_attribute.update({
                            'approximate_weight': data.get('approximate_weight', ''),
                            'custom_approximate_weight': data.get('custom_approximate_weight', '')
                        })
                    else:
                        weight_attribute.update({
                            'exact_weight': data.get('exact_weight', ''),
                            'weight_unit': data.get('weight_unit', '')
                        })
                    attributes_to_create.append(
                        PostAttribute(
                            post=post,
                            name='weight',
                            value=json.dumps(weight_attribute),
                            instance_id=instance_id
                        )
                    )
            # to bulk create all attributes
            if attributes_to_create:
                PostAttribute.objects.bulk_create(attributes_to_create)
            formset.instance = post # to save the formset for the wikidata tags 
            formset.save()
            messages.success(request, 'Post created successfully!')
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()
        formset = WikidataTagFormSet(prefix='tags')
    context = {
        'form': form,
        'formset': formset,
        'colour_choices': [list(choice) for choice in Post.COLOUR_CHOICES],
        'shape_choices': [list(choice) for choice in Post.SHAPE_CHOICES],
        'condition_choices': [list(choice) for choice in Post.CONDITION_CHOICES],
    }
    return render(request, 'core/posts/create_post.html', context)


# a function to delete a post
@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author: # only the author of the post can delete it
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('post_detail', pk=pk)
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('post_list')
    return render(request, 'core/posts/delete_post.html', {'post': post})


# a function to update the status of a post as solved or not
@login_required
def update_post_status(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        messages.error(request, 'You do not have permission to update this post status.')
        return redirect('post_detail', pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status == 'solved':
            if not post.has_answer_comment():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Cannot mark as solved: No comment has been marked as an answer yet.'
                })
        if new_status in dict(Post.STATUS_CHOICES):
            post.status = new_status
            post.save()
            return JsonResponse({
                'status': 'success',
                'new_status': new_status,
                'new_status_display': post.get_status_display()
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid status.'
            })  
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


# a function to search for wikidata entities for semantic tagging
def wikidata_search(request):
    query = request.GET.get('q', '')
    if query:
        try:
            url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={query}&language=en&format=json&limit=5&origin=*"
            response = requests.get(url)
            response.raise_for_status() # to raise an exception for bad status codes
            data = response.json()
            results = data.get('search', [])
            return JsonResponse({'results': results})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'results': []})