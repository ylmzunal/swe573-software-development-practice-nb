document.addEventListener('DOMContentLoaded', function() {
    const searchToggle = document.getElementById('searchToggle');
    const searchOverlay = document.querySelector('.search-overlay');
    const searchInput = document.getElementById('searchInput');
    const clearSearch = document.getElementById('clearSearch');
    const searchResults = document.getElementById('searchResults');

    searchToggle.addEventListener('click', function() {
        searchOverlay.classList.toggle('d-none');
        if (!searchOverlay.classList.contains('d-none')) {
            searchInput.focus();
            displayResults([], '');
        }
    });

    clearSearch.addEventListener('click', function() {
        searchInput.value = '';
        searchResults.classList.add('d-none');
        searchOverlay.classList.add('d-none');
    });

    let debounceTimer;
    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const query = this.value.trim();
            if (query.length >= 2) {
                fetchSearchResults(query);
            } else {
                displayResults([], '');
            }
        }, 300);
    });

    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const query = this.value.trim();
            if (query.length >= 2) {
                // Redirect to the full search results page
                window.location.href = `/posts/?search=${encodeURIComponent(query)}`;
            }
        }
    });

    function fetchSearchResults(query) {
        fetch(`/search/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displayResults(data, query);
            });
    }

    function displayResults(results, query) {
        searchResults.innerHTML = '';
        searchResults.classList.remove('d-none');

        if (results.length > 0) {
            results.forEach(post => {
                const div = document.createElement('div');
                div.className = 'search-result-item';
                const highlightedTitle = highlightMatch(post.title, query);
                div.innerHTML = highlightedTitle;
                div.addEventListener('click', () => {
                    window.location.href = `/post/${post.id}/`;
                });
                searchResults.appendChild(div);
            });
        } else if (query) {
            searchResults.innerHTML = '<div class="search-result-item">No results found</div>';
        }
    }

    function highlightMatch(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<span class="highlight">$1</span>');
    }

    // Close search overlay when clicking outside
    document.addEventListener('click', function(event) {
        if (!searchOverlay.contains(event.target) && !searchToggle.contains(event.target)) {
            searchOverlay.classList.add('d-none');
        }
    });
}); 