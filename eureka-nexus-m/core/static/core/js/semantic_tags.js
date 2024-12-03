let currentTagType = null;
let selectedTags = new Map();
let searchTimeout = null;

document.addEventListener('DOMContentLoaded', function() {
    const tagsContainer = document.getElementById('selectedTags');
    
    // If we're on the detail page (viewing tags)
    if (tagsContainer && tagsContainer.dataset.tags) {
        console.log('Found tags data:', tagsContainer.dataset.tags);
        try {
            const tags = JSON.parse(tagsContainer.dataset.tags);
            displaySemanticTags(tags);
        } catch (e) {
            console.error('Error parsing tags:', e);
        }
        return; // Exit early since we don't need the create functionality
    }

    // If we're on the create page
    const tagTypeSelector = document.getElementById('tagTypeSelector');
    if (!tagTypeSelector) return; // Exit if we're not on the create page

    const searchContainer = document.querySelector('.wikidata-search');
    const searchInput = document.getElementById('wikidataSearch');
    const resultsContainer = document.querySelector('.wikidata-results');
    const selectedTagsContainer = document.getElementById('selectedTags');
    const formsetContainer = document.getElementById('tagFormset');
    const totalFormsInput = document.querySelector('[name$="-TOTAL_FORMS"]');

    // Handle tag type selection
    tagTypeSelector.addEventListener('change', function() {
        currentTagType = this.value;
        if (currentTagType) {
            searchContainer.style.display = 'block';
            searchInput.value = '';
            searchInput.focus();
        } else {
            searchContainer.style.display = 'none';
        }
    });

    // Handle search input
    searchInput.addEventListener('input', function() {
        clearTimeout(searchTimeout);
        const query = this.value.trim();
        
        if (query.length < 2) {
            resultsContainer.style.display = 'none';
            return;
        }

        searchTimeout = setTimeout(() => {
            fetch(`/wikidata-search/?q=${encodeURIComponent(query)}`)
                .then(response => response.json())
                .then(data => {
                    resultsContainer.innerHTML = '';
                    
                    data.results.forEach(item => {
                        const resultDiv = document.createElement('div');
                        resultDiv.className = 'wikidata-result';
                        resultDiv.innerHTML = `
                            <div class="title">${item.label}</div>
                            <div class="description">${item.description || 'No description available'}</div>
                        `;
                        
                        resultDiv.addEventListener('click', () => {
                            addTag({
                                type: currentTagType,
                                id: item.id,
                                label: item.label,
                                link: `https://www.wikidata.org/entity/${item.id}`
                            });
                            searchInput.value = '';
                            resultsContainer.style.display = 'none';
                            tagTypeSelector.value = '';
                            searchContainer.style.display = 'none';
                        });
                        
                        resultsContainer.appendChild(resultDiv);
                    });
                    
                    resultsContainer.style.display = data.results.length ? 'block' : 'none';
                });
        }, 300);
    });

    // Close results when clicking outside
    document.addEventListener('click', function(e) {
        if (!searchContainer.contains(e.target)) {
            resultsContainer.style.display = 'none';
        }
    });

    function addTag(tag) {
        const tagId = `${tag.type}-${tag.id}`;
        if (selectedTags.has(tagId)) return;

        console.log("Adding tag:", tag);  // Debug log

        // Store the full tag information
        selectedTags.set(tagId, {
            type: tag.type,
            id: tag.id,
            label: tag.label,
            link: `https://www.wikidata.org/entity/${tag.id}`
        });

        // Create visual tag element
        const tagElement = document.createElement('div');
        tagElement.className = 'selected-tag';
        tagElement.innerHTML = `
            <span>${tag.label}</span>
            <a href="${tag.link}" target="_blank" class="ms-2">
                <i class="fas fa-external-link-alt"></i>
            </a>
            <button type="button" class="remove-tag">&times;</button>
        `;

        // Add remove functionality
        tagElement.querySelector('.remove-tag').addEventListener('click', () => {
            selectedTags.delete(tagId);
            tagElement.remove();
            updateFormset();
        });

        selectedTagsContainer.appendChild(tagElement);
        
        // Update hidden formset
        updateFormset();
        
        // Debug log the current state
        console.log("Current tags:", Array.from(selectedTags.values()));
    }

    function updateFormset() {
        console.log("Updating formset with tags:", Array.from(selectedTags.values()));
        
        // Clear existing forms except the empty form template
        const formTemplate = formsetContainer.querySelector('.formset-form');
        formsetContainer.innerHTML = '';
        formsetContainer.appendChild(formTemplate.cloneNode(true));

        // Create new forms for each tag
        let index = 0;
        selectedTags.forEach((tag, tagId) => {
            console.log("Creating form for tag:", tag);
            const form = formTemplate.cloneNode(true);
            
            // Update all form field names and ids
            form.querySelectorAll('input').forEach(input => {
                const oldName = input.name;
                const newName = oldName.replace('__prefix__', index.toString());
                input.name = newName;
                input.id = input.id.replace('__prefix__', index.toString());
                
                // Set the appropriate value based on the field name
                if (newName.endsWith('-tag_type')) {
                    input.value = tag.type;
                } else if (newName.endsWith('-wikidata_id')) {
                    input.value = tag.id;
                } else if (newName.endsWith('-label')) {
                    input.value = tag.label;
                } else if (newName.endsWith('-link')) {
                    input.value = tag.link;
                }
            });
            
            formsetContainer.appendChild(form);
            index++;
        });

        // Update total forms count
        totalFormsInput.value = selectedTags.size;
        console.log("Final formset HTML:", formsetContainer.innerHTML);
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
    // Debug log before submission
    console.log("Form submission - Total tags:", selectedTags.size);
    console.log("Form submission - Tags data:", Array.from(selectedTags.values()));
    console.log("Form submission - Formset HTML:", formsetContainer.innerHTML);
}); 