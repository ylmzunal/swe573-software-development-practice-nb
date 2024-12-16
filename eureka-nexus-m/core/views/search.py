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
