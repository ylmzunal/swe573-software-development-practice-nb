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



## BASE
# a function to render the home page
def home(request):
    recent_posts = Post.objects.all().order_by('-created_at')[:6] # to get the 6 most recent posts to display on the home page
    user_votes = {} # to get the user's votes
    if request.user.is_authenticated: # to check and display if the user is signed in and has voted on the recent posts
        user_votes = {
            vote.post_id: vote 
            for vote in Vote.objects.filter(user=request.user, post__in=recent_posts)
        }
    return render(request, 'core/home.html', {
        "recent_posts": recent_posts,
        "user_votes": user_votes
    })


# a function to render the signup page
def signup_view(request):
    if request.method == 'POST':
        form = ProfileCreationForm(request.POST)
        if form.is_valid(): # to check if the form is valid and to save the user, log them in and redirect to the profile page
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('profile')
    else:
        form = ProfileCreationForm()
    return render(request, 'core/signup.html', {'form': form})


# a function to render the login page
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid(): # to check if the form is valid and to authenticate the user, log them in and redirect to the home page
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


# a function to logout the user
@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


# a function to delete the user's account
@login_required
def delete_account(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        user = authenticate(username=request.user.username, password=password)
        
        if user is not None: # to check if the user is authenticated and to delete their account
            try: # to get all the user's posts and set the author of the posts to None, making them anonymous, and delete the user's account
                posts = Post.objects.filter(author=user)
                for post in posts: 
                    post.author = None
                    post.save()
                user.delete()         
                messages.success(request, 'Your account has been successfully deleted.')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'An error occurred while deleting your account: {str(e)}')
                return redirect('profile')
        else:
            messages.error(request, 'Invalid password. Please try again.')
            return redirect('profile')
    return redirect('profile')



## COMMENTS
# a function to add a comment to a post
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id) # to get the post to add the comment to or to redirect to the post detail page if the form is not valid
    if request.method == 'POST':
        form = CommentForm(request.POST, user=request.user, post=post)
        if form.is_valid(): # to check if the form is valid and to save the comment
            comment = form.save(commit=False) 
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=post_id)
    return redirect('post_detail', pk=post_id)


# a function to add a reply to a comment for threaded comments
@login_required
def add_reply(request, post_id, comment_id):
    post = get_object_or_404(Post, pk=post_id) # to get the post to add the reply to or to redirect to the post detail page if the form is not valid
    parent_comment = get_object_or_404(Comment, pk=comment_id) # to get the parent comment to add the reply to
    if request.method == 'POST':
        form = CommentForm(request.POST, user=request.user, post=post)
        if form.is_valid(): # to check if the form is valid and to save the reply   
            reply = form.save(commit=False)
            reply.post = post
            reply.author = request.user
            reply.parent = parent_comment
            reply.save()
    return redirect('post_detail', pk=post_id)


# a function to delete a comment
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id) # to get the comment to delete or to redirect to the post detail page if the comment is not deleted
    if request.user == comment.author and request.method == 'POST': # to check if the user is the author of the comment and if the request method is POST
        had_answer = comment.tag == 'answer' # to check if the comment is an answer
        old_status = comment.post.status # to get the old status of the post
        comment.is_deleted = True # to set the comment to deleted. if it should be completely deleted, this is not recommended as it will not delete the comment completely but only set it to deleted
        status_changed = comment.save() # to save the comment
        response_data = {'status': 'success'}
        if had_answer and status_changed and old_status == 'solved': # to check if the comment was an answer and if the status of the post changed and if the old status was solved
            response_data.update({
                'post_status_changed': True,
                'new_post_status': 'unknown',
                'new_post_status_display': comment.post.get_status_display(),
                'message': 'Post status changed to Unknown: Answer comment was deleted'
            })
        return JsonResponse(response_data)
    return JsonResponse({'status': 'error'}, status=403)


# a function to edit the tag of a comment as answer
@login_required
def edit_comment_tag(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id) # to get the comment to edit the tag of or to redirect to the post detail page if the comment is not edited
    if request.method == 'POST':
        new_tag = request.POST.get('tag')
        old_tag = comment.tag
        if request.user != comment.post.author: # to check if the user is the author of the post as only the post owner can tag a comment as answer
            return JsonResponse({
                'status': 'error',
                'message': 'Only the post owner can edit comment tags'
            }, status=403)
        if new_tag and new_tag != 'answer': # to check if the new tag is not an answer as post owner can only mark comments as answers
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
            if old_tag == 'answer' and not new_tag and comment.post.status == 'unknown' and status_changed: # to check if the old tag was an answer and if the new tag is not an answer and if the status of the post is unknown and if the status of the post changed
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



## FOLLOWING
# a function to follow a post
@login_required
def toggle_follow_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=post_id)
        try:
            follow = PostFollower.objects.filter(user=request.user, post=post) # to get the follow relationship to check if the user is following the post
            if follow.exists():
                follow.delete() # to delete the follow relationship (to unfollow the post)
                is_following = False
            else:
                PostFollower.objects.create(user=request.user, post=post) # to create the follow relationship (to follow the post)
                is_following = True
            return JsonResponse({
                'status': 'success',
                'is_following': is_following
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)


# a function to follow a user
@login_required
def toggle_follow_user(request, username):
    if request.method == 'POST':
        User = get_user_model()
        user_to_follow = get_object_or_404(User, username=username)
        if request.user == user_to_follow: # to check if the user is not trying to follow themselves
            return JsonResponse({
                'status': 'error',
                'message': 'You cannot follow yourself'
            }, status=400)
        try:
            follow = UserFollower.objects.filter(user=request.user, following=user_to_follow) # to get the follow relationship to check if the user is following the user
            if follow.exists():
                follow.delete() # to delete the follow relationship (to unfollow the user)
                is_following = False
            else:
                UserFollower.objects.create(user=request.user, following=user_to_follow) # to create the follow relationship (to follow the user)
                is_following = True
            followers_count = UserFollower.objects.filter(following=user_to_follow).count()
            return JsonResponse({
                'status': 'success',
                'is_following': is_following,
                'followers_count': followers_count
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=400)



## POSTS
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



## PROFILES
# a function to display the profile of the current user
@login_required
def profile_view(request):
    # getting data related to the current user
    user_posts = Post.objects.filter(author=request.user).order_by('-created_at') # to get the posts of the current user
    voted_posts = Post.objects.filter( # to get the posts the current user has voted on
        votes__user=request.user
    ).select_related('author').prefetch_related('comments').order_by('-votes__created_at') 
    commented_posts = Post.objects.filter( # to get the posts the current user has commented on
        comments__author=request.user
    ).exclude(
        author=request.user
    ).select_related('author').prefetch_related('comments').distinct().order_by('-comments__created_at') 
    followed_posts = Post.objects.filter( # to get the posts the current user is following
        followers__user=request.user
    ).select_related('author').prefetch_related('comments').order_by('-followers__followed_at')
    following_users = User.objects.filter( # to get the users the current user is following
        followers__user=request.user
    ).order_by('-followers__followed_at')
    follower_users = User.objects.filter( # to get the users who follow the current user
        following__following=request.user
    ).order_by('-following__followed_at')
    # to get the posts the current user has voted on
    all_posts = list(user_posts) + list(voted_posts) + list(commented_posts) + list(followed_posts)
    user_votes = {
        vote.post_id: vote 
        for vote in Vote.objects.filter(
            user=request.user, 
            post__in=all_posts
        )
    }
    return render(request, 'core/profile/profile.html', {
        "user": request.user,
        "user_posts": user_posts,
        "voted_posts": voted_posts,
        "commented_posts": commented_posts,
        "followed_posts": followed_posts,
        "following_users": following_users,
        "follower_users": follower_users,
        "user_votes": user_votes,
    })


# a function to edit the profile of the current user
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Profile updated successfully!')
            if form.cleaned_data.get('new_password'): # to keep the user logged in after updating the password
                update_session_auth_hash(request, user)
            return redirect('profile')
    else:
        form = ProfileChangeForm(instance=request.user)
    return render(request, 'core/profile/edit_profile.html', {'form': form})


# a function to display the profile of a user   
def public_profile_view(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username)
    is_following = False
    user_post_votes = {}
    user_comment_votes = {}
    posts = Post.objects.filter(author=user).order_by('-created_at')
    comments = Comment.objects.filter(author=user).order_by('-created_at')
    followers_count = UserFollower.objects.filter(following=user).count()
    following_count = UserFollower.objects.filter(user=user).count()
    if request.user.is_authenticated: # to show if the current user is following the user
        is_following = UserFollower.objects.filter(
            user=request.user, 
            following=user
        ).exists()
        user_post_votes = {
            vote.post_id: vote 
            for vote in Vote.objects.filter(
                user=request.user, 
                post__in=posts
            )
        }   
        user_comment_votes = {
            vote.comment_id: vote 
            for vote in Vote.objects.filter(
                user=request.user, 
                comment__in=comments
            )
        }
    context = {
        'profile_user': user,
        'posts': posts,
        'comments': comments,
        'is_own_profile': request.user == user if request.user.is_authenticated else False,
        'is_following': is_following,
        'followers_count': followers_count,
        'following_count': following_count,
        'user_post_votes': user_post_votes,
        'user_comment_votes': user_comment_votes,
    }
    return render(request, 'core/profile/public_profile.html', context)




## SEARCH
# a function to search for posts on navbar search bar
def search_posts(request):
    query = request.GET.get('q', '')
    if len(query) >= 2:
        posts = Post.objects.filter(
            title__icontains=query
        ).values('id', 'title')[:5]  # Limit to 5 results
        return JsonResponse(list(posts), safe=False)
    return JsonResponse([], safe=False)


# a function to perform an advanced search for posts
def advanced_search(request):
    search_performed = False
    posts = None
    user_votes = {}
    # to get the available attributes for the advanced search
    available_attributes = [
        {'name': 'title', 'display_name': 'Title'},
        {'name': 'description', 'display_name': 'Description'},
        {'name': 'age', 'display_name': 'Age'},
        {'name': 'brand', 'display_name': 'Brand'},
        {'name': 'color', 'display_name': 'Color', 'choices': Post.COLOUR_CHOICES},
        {'name': 'condition', 'display_name': 'Condition', 'choices': Post.CONDITION_CHOICES},
        {'name': 'location', 'display_name': 'Location'},
        {'name': 'manufacturer', 'display_name': 'Manufacturer'},
        {'name': 'markings', 'display_name': 'Markings'},
        {'name': 'material', 'display_name': 'Material'},
        {'name': 'origin', 'display_name': 'Origin'},
        {'name': 'pattern', 'display_name': 'Pattern'},
        {'name': 'semantic_tag', 'display_name': 'Semantic Tag'},
        {'name': 'shape', 'display_name': 'Shape', 'choices': Post.SHAPE_CHOICES},
        {'name': 'size', 'display_name': 'Size'},
        {'name': 'texture', 'display_name': 'Texture'},
        {'name': 'weight', 'display_name': 'Weight'},
    ]
    if request.GET:
        logger.debug(f"Search parameters: {request.GET}")
        search_performed = True
        base_query = Post.objects.all()
        for key, value in request.GET.items(): # to get the search parameters
            if key.startswith('attribute_') and value:
                field_num = key.split('_')[1]
                attribute = value
                search_value = request.GET.get(f'value_{field_num}', '')
                operator = request.GET.get(f'operator_{field_num}', 'AND')
                match_type = request.GET.get(f'match_{field_num}', 'include')
                if not search_value: # to handle the case where the search value is empty
                    continue
                # to handle different types of attributes
                if attribute in ['title', 'description', 'color', 'shape', 'condition']:
                    field_name = 'colour' if attribute == 'color' else attribute
                    if match_type == 'exact':
                        condition = Q(**{f'{field_name}__exact': search_value})
                    else:
                        condition = Q(**{f'{field_name}__icontains': search_value})
                # to handle the semantic tag search
                elif attribute == 'semantic_tag':
                    tag_id = request.GET.get(f'semantic_tag_id_{field_num}')
                    if tag_id:
                        condition = Q(wikidata_tags__wikidata_id=tag_id)
                    else:
                        continue
                # to handle the PostAttribute fields
                else:
                    if match_type == 'exact':
                        condition = Q(
                            attributes__name=attribute,
                            attributes__value__icontains=f'"{search_value}"'
                        )
                    else:
                        condition = Q(
                            attributes__name=attribute,
                            attributes__value__icontains=search_value
                        )
                # to apply the condition based on the operator
                if operator == 'NOT': # do not include
                    base_query = base_query.exclude(condition)
                elif operator == 'OR':
                    base_query = base_query | Post.objects.filter(condition)
                else: # AND
                    base_query = base_query.filter(condition)
        # finalizing the query
        if any(key.startswith('attribute_') for key in request.GET):
            posts = base_query.distinct().order_by('-created_at')
            logger.debug(f"Final query: {str(posts.query)}")
            logger.debug(f"Found {posts.count()} posts")
            paginator = Paginator(posts, 10) # to add pagination
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



## VOTING
# a function to vote on a post
@login_required
def vote_post(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    vote_type = request.POST.get('vote_type')
    if vote_type not in ['up', 'down']:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    post = get_object_or_404(Post, id=post_id)
    existing_vote = Vote.objects.filter(user=request.user, post=post).first() # to get and check the existing vote if the user has already voted
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            existing_vote.delete() # if the user clicks the same vote type, remove the vote
            action = 'removed'
        else:
            existing_vote.vote_type = vote_type # if the user clicks different vote type, change the vote
            existing_vote.save()
            action = 'changed'
    else:
        Vote.objects.create(user=request.user, post=post, vote_type=vote_type) # to create a new vote
        action = 'added'
    # to get the updated vote counts
    upvotes = Vote.objects.filter(post=post, vote_type='up').count()
    downvotes = Vote.objects.filter(post=post, vote_type='down').count()
    return JsonResponse({
        'status': 'success',
        'action': action,
        'upvotes': upvotes,
        'downvotes': downvotes
    }) 


# a function to vote on a comment
@login_required
def vote_comment(request, comment_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    vote_type = request.POST.get('vote_type')
    if vote_type not in ['up', 'down']:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    comment = get_object_or_404(Comment, id=comment_id)
    existing_vote = Vote.objects.filter(user=request.user, comment=comment).first() # to get and check the existing vote if the user has already voted
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            existing_vote.delete() # if the user clicks the same vote type, remove the vote
            action = 'removed'
        else:
            existing_vote.vote_type = vote_type # if the user clicks different vote type, change the vote
            existing_vote.save()
            action = 'changed'
    else:
        Vote.objects.create(user=request.user, comment=comment, vote_type=vote_type) # to create a new vote
        action = 'added'
    # to get the updated vote counts
    upvotes = comment.upvote_count()
    downvotes = comment.downvote_count()
    return JsonResponse({
        'status': 'success',
        'action': action,
        'upvotes': upvotes,
        'downvotes': downvotes
    }) 