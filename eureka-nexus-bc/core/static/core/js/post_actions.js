// Follow/Unfollow functionality
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.follow-btn').forEach(button => {
        button.addEventListener('click', async function(e) {
            e.preventDefault();
            const postId = this.dataset.postId;
            
            try {
                const response = await fetch(`/post/${postId}/follow/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json',
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    
                    // Toggle button appearance
                    this.classList.toggle('btn-outline-warning');
                    this.classList.toggle('btn-warning');
                    
                    // Toggle icon
                    const icon = this.querySelector('i');
                    icon.classList.toggle('fa-bookmark-o');
                    icon.classList.toggle('fa-bookmark');
                    
                    // Toggle text
                    const textSpan = this.querySelector('.follow-text');
                    textSpan.textContent = data.is_following ? 'Unfollow' : 'Follow';
                    
                    // Update data-action
                    this.dataset.action = data.is_following ? 'unfollow' : 'follow';
                } else {
                    console.error('Failed to toggle follow status');
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
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