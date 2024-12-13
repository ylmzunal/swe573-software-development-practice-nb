document.addEventListener('DOMContentLoaded', function() {
    // Toggle reply forms
    document.querySelectorAll('.reply-toggle').forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            const replyForm = document.getElementById(`reply-form-${commentId}`);
            replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
        });
    });

    // Handle comment deletion
    document.querySelectorAll('.delete-comment').forEach(button => {
        button.addEventListener('click', async function() {
            if (confirm('Are you sure you want to delete this comment?')) {
                const commentId = this.dataset.commentId;
                try {
                    const response = await fetch(`/comment/${commentId}/delete/`, {
                        method: 'POST',
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    });
                    
                    if (response.ok) {
                        const comment = document.querySelector(`#comment-${commentId} .comment-text`);
                        comment.innerHTML = '<em class="text-muted">[Deleted]</em>';
                        this.remove();
                    }
                } catch (error) {
                    console.error('Error deleting comment:', error);
                }
            }
        });
    });

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Handle tag changes
    document.querySelectorAll('.change-tag').forEach(link => {
        link.addEventListener('click', async function(e) {
            e.preventDefault();
            const commentId = this.closest('.comment').id.replace('comment-', '');
            const newTag = this.dataset.tag;
            
            try {
                console.log('Sending tag update request:', commentId, newTag); // Debug log
                const response = await fetch(`/comment/${commentId}/edit-tag/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `tag=${newTag}`
                });
                
                const data = await response.json();
                console.log('Server response:', data); // Debug log

                if (response.ok && data.status === 'success') {
                    const commentElement = this.closest('.comment');
                    let badge = commentElement.querySelector('.tag-badge');
                    const header = commentElement.querySelector('.comment-header');
                    const dropdown = header.querySelector('.dropdown');

                    // Remove existing badge if it exists
                    if (badge) {
                        badge.remove();
                    }

                    // Add new badge if there's a tag
                    if (newTag) {
                        badge = document.createElement('span');
                        badge.className = 'badge tag-badge bg-success ms-2';
                        badge.textContent = 'Answer';  // Since post owner can only set answer tag
                        
                        // Insert before the dropdown button
                        if (dropdown) {
                            header.insertBefore(badge, dropdown);
                        } else {
                            header.appendChild(badge);
                        }
                    }
                } else {
                    console.error('Error response:', data); // Debug log
                    alert(data.message || 'Error updating tag');
                }
            } catch (error) {
                console.error('Error updating tag:', error);
                alert('Error updating tag');
            }
        });
    });
}); 