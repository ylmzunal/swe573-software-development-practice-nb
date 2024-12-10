from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import ProfileCreationForm, ProfileChangeForm, PostForm, WikidataTagFormSet
from django.contrib import messages
from .models import Profile, Post, PostAttribute
from django import forms
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
import requests
from .models import WikidataTag
from django.views.generic import DetailView
import json

def home(request):
    recent_posts = Post.objects.all().order_by('-created_at')[:6]  # Get 6 most recent posts
    return render(request, 'core/home.html', {'recent_posts': recent_posts})

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
    post_list = Post.objects.all().order_by('-created_at')
    paginator = Paginator(post_list, 10)  # Show 10 posts per page

    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        posts = paginator.page(paginator.num_pages)

    return render(request, 'core/post_list.html', {'posts': posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    print("Semantic tags:", list(post.wikidata_tags.all()))
    return render(request, 'core/post_detail.html', {'post': post})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        formset = WikidataTagFormSet(request.POST, prefix='tags')
        
        if form.is_valid() and formset.is_valid():
            post = form.save(commit=False)
            post.author = request.user if not request.POST.get('anonymous') else None
            post.save()
            
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
        if new_status in dict(Post.STATUS_CHOICES):
            post.status = new_status
            post.save()
            messages.success(request, 'Post status updated successfully!')
        else:
            messages.error(request, 'Invalid status.')
    return redirect('post_detail', pk=pk)




def post_list(request):
    post_list = Post.objects.all().order_by('-created_at')
    paginator = Paginator(post_list, 10)  # Show 10 posts per page

    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        posts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        posts = paginator.page(paginator.num_pages)

    return render(request, 'core/post_list.html', {'posts': posts})


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
