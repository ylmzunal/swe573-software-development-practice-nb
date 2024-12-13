from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import ProfileCreationForm, ProfileChangeForm, PostForm, WikidataTagFormSet, CommentForm
from django.contrib import messages
from .models import Profile, Post, PostAttribute, PostMultimedia, Comment, Vote
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
import requests
from .models import WikidataTag
from django.views.generic import DetailView
import json
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType
from functools import reduce
from operator import and_, or_
import logging
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
logger = logging.getLogger(__name__)

def get_user_votes(user, posts):
    if not user.is_authenticated:
        return {}
    votes = Vote.objects.filter(user=user, content_type=ContentType.objects.get_for_model(Post), 
                              object_id__in=[post.id for post in posts])
    return {vote.object_id: vote.vote_type for vote in votes}

def home(request):
    recent_posts = Post.objects.all().order_by('-created_at')[:6]
    user_votes = get_user_votes(request.user, recent_posts) if request.user.is_authenticated else {}
    
    context = {
        'recent_posts': recent_posts,
        'user_votes': user_votes,
    }
    return render(request, 'core/home.html', context)

# AUTH

def signup_view(request):
    if request.method == 'POST':
        form = ProfileCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('profile')
    else:
        form = ProfileCreationForm()
    return render(request, 'core/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    else:
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'core/profile.html', {"user": request.user})

from django.contrib.auth import update_session_auth_hash

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()  # Save the updated profile and password
            messages.success(request, 'Profile updated successfully!')
            # Keep the user logged in after updating the password
            if form.cleaned_data.get('new_password'):
                update_session_auth_hash(request, user)
            return redirect('profile')  # Redirect to the profile page
    else:
        form = ProfileChangeForm(instance=request.user)

    return render(request, 'core/edit_profile.html', {'form': form})




# POSTS


def post_list(request):
    post_list = Post.objects.all().prefetch_related('comments')
    
    # Handle search query
    search_query = request.GET.get('search', '')
    if search_query:
        post_list = post_list.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    post_list = post_list.order_by('-created_at')
    paginator = Paginator(post_list, 10)  # Show 10 posts per page

    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    # Get user votes for the posts
    user_votes = {}
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
    return render(request, 'core/post_list.html', context)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comment_form = CommentForm(user=request.user, post=post) if request.user.is_authenticated else None
    user_vote = None
    comment_votes = {}
    
    if request.user.is_authenticated:
        user_vote = Vote.objects.filter(user=request.user, post=post).first()
        comment_votes = {
            vote.comment_id: vote 
            for vote in Vote.objects.filter(
                user=request.user, 
                comment__in=post.comments.all()
            )
        }
    
    return render(request, 'core/post_detail.html', {
        'post': post,
        'comment_form': comment_form,
        'user_vote': user_vote,
        'comment_votes': comment_votes
    })

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        formset = WikidataTagFormSet(request.POST, prefix='tags')
        
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user if not request.POST.get('anonymous') else None
            post.save()
            
            # Handle multimedia files
            multimedia_files = request.FILES.getlist('multimedia_files')
            for index, f in enumerate(multimedia_files):
                file_type = 'image' if f.content_type.startswith('image/') else \
                           'video' if f.content_type.startswith('video/') else \
                           'audio' if f.content_type.startswith('audio/') else \
                           'document'
                
                PostMultimedia.objects.create(
                    post=post,
                    file=f,
                    file_type=file_type,
                    order=index
                )
            
            # Now process and save attributes
            attributes_to_create = []
            size_data = {}  # Dictionary to collect size-related fields by instance
            weight_data = {}  # Dictionary to collect weight-related fields by instance
            
            for field_name, field_value in request.POST.items():
                if '[' in field_name and ']' in field_name:
                    base_name, instance_id = field_name.split('[')
                    instance_id = instance_id.rstrip(']')
                    
                    # Handle size fields
                    if base_name.startswith('size_') or base_name in ['width', 'height', 'depth']:
                        if instance_id not in size_data:
                            size_data[instance_id] = {}
                        size_data[instance_id][base_name] = field_value
                        continue
                        
                    # Handle weight fields
                    if base_name.startswith('weight_') or base_name == 'exact_weight':
                        if instance_id not in weight_data:
                            weight_data[instance_id] = {}
                        weight_data[instance_id][base_name] = field_value
                        continue
                    
                    # Handle regular attributes
                    if not base_name.startswith('custom_'):
                        attribute_data = {
                            'value': field_value
                        }
                        
                        # Check for custom value if this is an 'other' selection
                        custom_field_name = f'custom_{base_name}[{instance_id}]'
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
            
            # Process collected size data
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
            
            # Process collected weight data
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
            
            # Bulk create all attributes
            if attributes_to_create:
                PostAttribute.objects.bulk_create(attributes_to_create)
            
            formset.instance = post
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
    
    return render(request, 'core/create_post.html', context)

@login_required
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        messages.error(request, 'You do not have permission to edit this post.')
        return redirect('post_detail', pk=pk)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        formset = WikidataTagFormSet(request.POST, instance=post)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Post updated successfully!')
            return redirect('post_detail', pk=pk)
    else:
        form = PostForm(instance=post)
        formset = WikidataTagFormSet(instance=post)
    return render(request, 'core/edit_post.html', {'form': form, 'formset': formset, 'post': post})

@login_required
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        messages.error(request, 'You do not have permission to delete this post.')
        return redirect('post_detail', pk=pk)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, 'Post deleted successfully!')
        return redirect('post_list')
    return render(request, 'core/delete_post.html', {'post': post})

@login_required
def update_post_status(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        messages.error(request, 'You do not have permission to update this post status.')
        return redirect('post_detail', pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        # Check if trying to mark as solved
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




def wikidata_search(request):
    query = request.GET.get('q', '')
    if query:
        try:
            url = f"https://www.wikidata.org/w/api.php?action=wbsearchentities&search={query}&language=en&format=json&limit=5&origin=*"
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for bad status codes
            data = response.json()
            results = data.get('search', [])
            #print("Wikidata search results:", results)  # Debug print
            return JsonResponse({'results': results})
        except Exception as e:
            print(f"Wikidata search error: {str(e)}")  # Debug print
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'results': []})

class PostDetailView(DetailView):
    model = Post
    template_name = 'core/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Ensure semantic tags are prefetched
        context['post'].semantic_tags.all()
        return context

@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, user=request.user, post=post)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=post_id)
    return redirect('post_detail', pk=post_id)

@login_required
def add_reply(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id)
    parent_comment = get_object_or_404(Comment, pk=comment_id)
    if request.method == 'POST':
        form = CommentForm(request.POST, user=request.user, post=post)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.post = post
            reply.author = request.user
            reply.parent = parent_comment
            reply.save()
    return redirect('post_detail', pk=post_id)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if request.user == comment.author and request.method == 'POST':
        had_answer = comment.tag == 'answer'
        old_status = comment.post.status
        comment.is_deleted = True
        status_changed = comment.save()
        
        response_data = {'status': 'success'}
        
        # Only add status change info if the status actually changed from solved to unknown
        if had_answer and status_changed and old_status == 'solved':
            response_data.update({
                'post_status_changed': True,
                'new_post_status': 'unknown',
                'new_post_status_display': comment.post.get_status_display(),
                'message': 'Post status changed to Unknown: Answer comment was deleted'
            })
        
        return JsonResponse(response_data)
    return JsonResponse({'status': 'error'}, status=403)

@login_required
def edit_comment_tag(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    
    if request.method == 'POST':
        new_tag = request.POST.get('tag')
        old_tag = comment.tag
        
        # Only post owner can edit tags, and only to mark as answer
        if request.user != comment.post.author:
            return JsonResponse({
                'status': 'error',
                'message': 'Only the post owner can edit comment tags'
            }, status=403)
        
        if new_tag and new_tag != 'answer':
            return JsonResponse({
                'status': 'error',
                'message': 'Post owner can only mark comments as answers'
            }, status=403)
        
        try:
            comment.tag = new_tag
            status_changed = comment.save()
            
            response_data = {
                'status': 'success',
                'tag': new_tag,
                'tag_display': comment.get_tag_display() if new_tag else ''
            }

            # Only add status change info if the post was previously solved
            if old_tag == 'answer' and not new_tag and comment.post.status == 'unknown' and status_changed:
                response_data['post_status_changed'] = True
                response_data['new_post_status'] = 'unknown'
                response_data['new_post_status_display'] = comment.post.get_status_display()
                response_data['message'] = 'Post status changed to Unknown: No answer tags remaining'
            
            return JsonResponse(response_data)
            
        except Exception as e:
            print(f"Error updating comment tag: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Error saving comment tag'
            }, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def search_posts(request):
    query = request.GET.get('q', '')
    if len(query) >= 2:
        posts = Post.objects.filter(
            title__icontains=query
        ).values('id', 'title')[:5]  # Limit to 5 results
        return JsonResponse(list(posts), safe=False)
    return JsonResponse([], safe=False)

def advanced_search(request):
    search_performed = False
    posts = None
    user_votes = {}
    available_attributes = [
        {'name': 'color', 'display_name': 'Color'},
        {'name': 'size', 'display_name': 'Size'},
        {'name': 'weight', 'display_name': 'Weight'},
        {'name': 'condition', 'display_name': 'Condition'},
        {'name': 'material', 'display_name': 'Material'},
        {'name': 'shape', 'display_name': 'Shape'},
    ]

    if request.GET:
        logger.debug(f"Search parameters: {request.GET}")
        search_performed = True
        
        # Group search parameters
        search_fields = []
        
        # Process all parameters to group related fields
        for key, value in request.GET.items():
            if key.startswith('attribute_'):
                field_num = key.split('_')[1]
                if value:  # if attribute is selected
                    field_data = {
                        'attribute': value,
                        'value': request.GET.get(f'value_{field_num}', ''),
                        'operator': request.GET.get(f'operator_{field_num}', 'AND'),
                        'match_type': request.GET.get(f'match_{field_num}', 'include')
                    }
                    
                    # If it's a semantic tag, get the tag ID
                    if value == 'semantic_tag':
                        field_data['tag_id'] = request.GET.get(f'semantic_tag_id_{field_num}')
                    
                    search_fields.append(field_data)

        # Initialize query
        base_query = Post.objects.all()
        
        # Process each search field
        for field in search_fields:
            if not field['value']:  # Skip if no search value
                continue

            attribute = field['attribute']
            value = field['value']
            operator = field['operator']
            match_type = field['match_type']
            
            # Build the condition based on match type
            if attribute == 'semantic_tag':
                # Use the tag_id for semantic tag searches
                tag_id = field.get('tag_id')
                if tag_id:
                    condition = Q(wikidata_tags__wikidata_id=tag_id)
                else:
                    continue  # Skip if no tag_id is provided
            elif attribute == 'title':
                if match_type == 'exact':
                    condition = Q(title__iexact=value)
                else:  # include
                    condition = Q(title__icontains=value)
            elif attribute == 'description':
                if match_type == 'exact':
                    condition = Q(description__exact=value)
                else:  # include
                    condition = Q(description__icontains=value)
            elif attribute == 'color':
                if match_type == 'exact':
                    condition = Q(colour__exact=value)
                else:
                    condition = Q(colour__icontains=value)
            elif attribute == 'size':
                if match_type == 'exact':
                    condition = (
                        Q(size__exact=value) |
                        Q(width__exact=value) |
                        Q(height__exact=value) |
                        Q(depth__exact=value)
                    )
                else:
                    condition = (
                        Q(size__icontains=value) |
                        Q(width__icontains=value) |
                        Q(height__icontains=value) |
                        Q(depth__icontains=value)
                    )
            else:
                if match_type == 'exact':
                    condition = Q(**{f'{attribute}__exact': value})
                else:
                    condition = Q(**{f'{attribute}__icontains': value})

            # Apply the condition based on operator
            if operator == 'NOT':
                base_query = base_query.exclude(condition)
            elif operator == 'OR':
                base_query = base_query | Post.objects.filter(condition)
            else:  # AND
                base_query = base_query.filter(condition)

        # Finalize query
        if search_fields:
            posts = base_query.distinct().order_by('-created_at')
            logger.debug(f"Final query: {str(posts.query)}")
            logger.debug(f"Found {posts.count()} posts")
            
            # Get user votes
            user_votes = get_user_votes(request.user, posts) if request.user.is_authenticated else {}

            # Add pagination
            paginator = Paginator(posts, 10)
            page = request.GET.get('page')
            try:
                posts = paginator.page(page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)
        else:
            posts = Post.objects.none()

    return render(request, 'core/advanced_search.html', {
        'posts': posts,
        'search_performed': search_performed,
        'available_attributes': available_attributes,
        'user_votes': user_votes,
    })
