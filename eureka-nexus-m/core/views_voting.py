from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Post, Vote, Comment
from django.shortcuts import get_object_or_404

@login_required
def vote(request, post_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    vote_type = request.POST.get('vote_type')
    if vote_type not in ['up', 'down']:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    
    post = get_object_or_404(Post, id=post_id)
    
    # Check if user has already voted
    existing_vote = Vote.objects.filter(user=request.user, post=post).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # If clicking the same vote type, remove the vote
            existing_vote.delete()
            action = 'removed'
        else:
            # If clicking different vote type, change the vote
            existing_vote.vote_type = vote_type
            existing_vote.save()
            action = 'changed'
    else:
        # Create new vote
        Vote.objects.create(user=request.user, post=post, vote_type=vote_type)
        action = 'added'
    
    # Get updated vote counts
    upvotes = Vote.objects.filter(post=post, vote_type='up').count()
    downvotes = Vote.objects.filter(post=post, vote_type='down').count()
    
    return JsonResponse({
        'status': 'success',
        'action': action,
        'upvotes': upvotes,
        'downvotes': downvotes
    }) 

@login_required
def vote_comment(request, comment_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=400)
    
    vote_type = request.POST.get('vote_type')
    if vote_type not in ['up', 'down']:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    
    comment = get_object_or_404(Comment, id=comment_id)
    
    # Check if user has already voted
    existing_vote = Vote.objects.filter(user=request.user, comment=comment).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # If clicking the same vote type, remove the vote
            existing_vote.delete()
            action = 'removed'
        else:
            # If clicking different vote type, change the vote
            existing_vote.vote_type = vote_type
            existing_vote.save()
            action = 'changed'
    else:
        # Create new vote
        Vote.objects.create(user=request.user, comment=comment, vote_type=vote_type)
        action = 'added'
    
    # Get updated vote counts
    upvotes = comment.upvote_count()
    downvotes = comment.downvote_count()
    
    return JsonResponse({
        'status': 'success',
        'action': action,
        'upvotes': upvotes,
        'downvotes': downvotes
    }) 