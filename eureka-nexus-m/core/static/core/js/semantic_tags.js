document.addEventListener('DOMContentLoaded', function() {
    console.log('Semantic tags JS loaded');
    
    const searchInput = document.getElementById('wikidataSearch');
    const resultsContainer = document.querySelector('.wikidata-results');
    const selectedTagsContainer = document.getElementById('selectedTags');
    const formsetContainer = document.getElementById('tagFormset');
    
    // Track selected tags
    const selectedTags = new Map();
    let tagCounter = 0;

    // Initialize formset if needed
    initializeFormset();

    // Handle search input with debounce
    let searchTimeout = null;
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            resultsContainer.style.display = 'none';
            return;
        }

        searchTimeout = setTimeout(() => {
            console.log('Searching for:', query);  // Debug log
            fetch(`/wikidata-search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    console.log('Search results:', data);  // Debug log
                    resultsContainer.innerHTML = '';
                    
                    if (data.results && data.results.length > 0) {
                        data.results.forEach(item => {
                            const resultDiv = document.createElement('div');
                            resultDiv.className = 'wikidata-result';
                            resultDiv.innerHTML = `
                                <div class="title">${item.label || item.id}</div>
                                <div class="description">${item.description || 'No description available'}</div>
                            `;
                            
                            resultDiv.addEventListener('click', () => {
                                addTag(item);
                                searchInput.value = '';
                                resultsContainer.style.display = 'none';
                            });
                            
                            resultsContainer.appendChild(resultDiv);
                        });
                        resultsContainer.style.display = 'block';
                    } else {
                        resultsContainer.style.display = 'none';
                    }
                })
                .catch(error => {
                    console.error('Search error:', error);
                    resultsContainer.innerHTML = '<div class="p-2">Error searching Wikidata</div>';
                    resultsContainer.style.display = 'block';
                });
        }, 300);
    });

    // Add new function to add tags
    function addTag(item) {
        console.log('Adding tag:', item);
        
        if (selectedTags.has(item.id)) {
            console.log('Tag already exists');
            return;
        }

        // Create tag element
        const tagElement = document.createElement('div');
        tagElement.className = 'selected-tag';
        tagElement.innerHTML = `
            <span>${item.label || item.id}</span>
            <button type="button" class="remove-tag">×</button>
        `;

        // Add remove functionality
        const removeButton = tagElement.querySelector('.remove-tag');
        removeButton.addEventListener('click', () => {
            removeTag(item.id);
            tagElement.remove();
        });

        // Add to selected tags container
        selectedTagsContainer.appendChild(tagElement);

        // Store tag data
        selectedTags.set(item.id, {
            id: item.id,
            label: item.label || item.id,
            link: `https://www.wikidata.org/wiki/${item.id}`
        });

        // Update formset
        updateFormset();
    }

    function removeTag(tagId) {
        console.log('Removing tag:', tagId);
        selectedTags.delete(tagId);
        updateFormset();
    }

    function initializeFormset() {
        if (!document.querySelector('[name="tags-TOTAL_FORMS"]')) {
            formsetContainer.innerHTML = `
                <input type="hidden" name="tags-TOTAL_FORMS" value="0">
                <input type="hidden" name="tags-INITIAL_FORMS" value="0">
                <input type="hidden" name="tags-MIN_NUM_FORMS" value="0">
                <input type="hidden" name="tags-MAX_NUM_FORMS" value="1000">
            `;
        }
    }

    function updateFormset() {
        // Clear existing formset fields
        formsetContainer.innerHTML = '';
        
        // Re-initialize management form
        initializeFormset();

        // Add fields for each selected tag
        let index = 0;
        selectedTags.forEach((tag) => {
            formsetContainer.innerHTML += `
                <div style="display: none;">
                    <input type="hidden" name="tags-${index}-wikidata_id" value="${tag.id}">
                    <input type="hidden" name="tags-${index}-label" value="${tag.label}">
                    <input type="hidden" name="tags-${index}-link" value="${tag.link}">
                    <input type="hidden" name="tags-${index}-id" value="">
                </div>
            `;
            index++;
        });

        // Update total forms count
        document.querySelector('[name="tags-TOTAL_FORMS"]').value = selectedTags.size;
    }

    // Load existing tags if any (for edit form)
    const existingTags = selectedTagsContainer.dataset.tags;
    if (existingTags) {
        try {
            const tags = JSON.parse(existingTags);
            tags.forEach(tag => {
                addTag({
                    id: tag.wikidata_id,
                    label: tag.label,
                    link: tag.link
                });
            });
        } catch (e) {
            console.error('Error loading existing tags:', e);
        }
    }
});

function displaySemanticTags(tags) {
    const selectedTagsContainer = document.getElementById('selectedTags');
    if (!selectedTagsContainer) {
        console.error('Tags container not found');
        return;
    }

    console.log('Displaying tags:', tags);
    
    if (!tags || tags.length === 0) {
        console.log('No tags to display');
        return;
    }

    tags.forEach(tag => {
        console.log('Creating tag element for:', tag);
        const tagElement = document.createElement('div');
        tagElement.className = 'selected-tag';
        tagElement.innerHTML = `
            <span>${tag.label}</span>
            <a href="${tag.link}" target="_blank" class="ms-2">
                <i class="fas fa-external-link-alt"></i>
            </a>
        `;
        selectedTagsContainer.appendChild(tagElement);
    });
}

document.getElementById('postForm')?.addEventListener('submit', function(e) {
    console.log('Form submitting...');
    console.log('Selected tags:', Array.from(selectedTags.values()));
    console.log('Formset HTML:', document.getElementById('tagFormset').innerHTML);
    console.log('Total forms:', document.querySelector('[name="tags-TOTAL_FORMS"]').value);
    
    // Debug log before submission
    console.log("Form submission - Total tags:", selectedTags.size);
    console.log("Form submission - Tags data:", Array.from(selectedTags.values()));
    console.log("Form submission - Formset HTML:", formsetContainer.innerHTML);
}); 