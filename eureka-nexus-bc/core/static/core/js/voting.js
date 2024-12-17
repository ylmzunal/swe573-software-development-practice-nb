document.addEventListener('DOMContentLoaded', function() {
    // Handle both post and comment vote buttons
    document.querySelectorAll('.vote-buttons').forEach(container => {
        const postId = container.dataset.postId;
        const commentId = container.dataset.commentId;
        const upvoteBtn = container.querySelector('.upvote');
        const downvoteBtn = container.querySelector('.downvote');

        [upvoteBtn, downvoteBtn].forEach(btn => {
            if (btn) {
                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    if (btn.disabled) return;

                    const voteType = btn.classList.contains('upvote') ? 'up' : 'down';
                    const formData = new FormData();
                    formData.append('vote_type', voteType);

                    const url = commentId 
                        ? `/comment/${commentId}/vote/`
                        : `/post/${postId}/vote/`;

                    fetch(url, {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': getCookie('csrftoken')
                        }
                    })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            // Update vote counts
                            container.querySelector('.upvote-count').textContent = data.upvotes;
                            container.querySelector('.downvote-count').textContent = data.downvotes;

                            // Update active states
                            if (data.action === 'removed') {
                                btn.classList.remove('active');
                            } else if (data.action === 'changed') {
                                upvoteBtn.classList.toggle('active');
                                downvoteBtn.classList.toggle('active');
                            } else if (data.action === 'added') {
                                btn.classList.add('active');
                                if (voteType === 'up') {
                                    downvoteBtn.classList.remove('active');
                                } else {
                                    upvoteBtn.classList.remove('active');
                                }
                            }
                        }
                    })
                    .catch(error => console.error('Error:', error));
                });
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
}); 