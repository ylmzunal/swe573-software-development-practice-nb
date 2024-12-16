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