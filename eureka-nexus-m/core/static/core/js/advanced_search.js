document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('advancedSearchForm');
    const addFieldBtn = document.getElementById('addField');
    const additionalFields = document.getElementById('additionalFields');
    const resetButton = document.getElementById('resetForm');
    
    let fieldCounter = 1;

    // Initialize the first search field
    initializeFirstField();

    function initializeFirstField() {
        const firstField = document.querySelector('.search-field-container');
        if (firstField) {
            const attributeSelect = firstField.querySelector('.attribute-select');
            const searchInput = firstField.querySelector('.search-term');
            const matchSelect = firstField.querySelector('.match-type');

            // Add names to the first field inputs
            attributeSelect.name = 'attribute_1';
            searchInput.name = 'value_1';
            matchSelect.name = 'match_1';

            // Initialize Wikidata search for the first field
            initializeAttributeSelect(attributeSelect, searchInput);
        }
    }

    // Function to initialize attribute select behavior
    function initializeAttributeSelect(selectElement, searchInput) {
        selectElement.addEventListener('change', function() {
            const resultsContainer = searchInput.parentElement.querySelector('.wikidata-results');
            const locationResultsContainer = searchInput.parentElement.querySelector('.location-search-results');

            // Reset and hide all result containers
            resultsContainer.classList.add('d-none');
            locationResultsContainer.classList.add('d-none');

            if (this.value === 'semantic_tag') {
                initializeWikidataSearch(searchInput);
            } else if (this.value === 'location') {
                initializeLocationSearch(searchInput);
            }
        });
    }

    // Add new search field
    addFieldBtn.addEventListener('click', function() {
        fieldCounter++;
        const fieldDiv = document.createElement('div');
        fieldDiv.className = 'search-field-container mb-3';
        fieldDiv.innerHTML = `
            <div class="row align-items-center">
                <div class="col-md-2">
                    <select class="form-select operator-select" name="operator_${fieldCounter}">
                        <option value="AND">AND</option>
                        <option value="OR">OR</option>
                        <option value="NOT">DO NOT INCLUDE</option>
                    </select>
                </div>
                <div class="col-md-3">
                    <select class="form-select attribute-select" name="attribute_${fieldCounter}">
                        ${getAttributeOptions()}
                    </select>
                </div>
                <div class="col-md-3">
                    <div class="search-input-container">
                        <input type="text" class="form-control search-term" 
                               name="value_${fieldCounter}" 
                               placeholder="Enter search term...">
                        <div class="wikidata-results d-none"></div>
                        <input type="hidden" name="semantic_tag_id_${fieldCounter}" class="wikidata-tag-id">
                    </div>
                </div>
                <div class="col-md-3">
                    <select class="form-select match-type" name="match_${fieldCounter}">
                        <option value="include">Include</option>
                        <option value="exact">Exact Match</option>
                    </select>
                </div>
                <div class="col-md-1">
                    <button type="button" class="btn btn-danger btn-sm remove-field">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>`;

        // Add remove functionality
        fieldDiv.querySelector('.remove-field').addEventListener('click', function() {
            fieldDiv.remove();
        });

        // Initialize Wikidata search for the new field
        const attributeSelect = fieldDiv.querySelector('.attribute-select');
        const searchInput = fieldDiv.querySelector('.search-term');
        initializeAttributeSelect(attributeSelect, searchInput);

        additionalFields.appendChild(fieldDiv);
    });

    // Reset form
    resetButton.addEventListener('click', function() {
        form.reset();
        additionalFields.innerHTML = '';
    });

    // Helper function to get attribute options
    function getAttributeOptions() {
        // Get the options from the first attribute select element
        const firstSelect = document.querySelector('.attribute-select');
        const optgroups = firstSelect.querySelectorAll('optgroup');
        
        let optionsHtml = '';
        
        // Add Basic Fields
        const basicFields = optgroups[0];
        optionsHtml += `<optgroup label="Basic Fields">`;
        basicFields.querySelectorAll('option').forEach(option => {
            optionsHtml += `<option value="${option.value}">${option.textContent}</option>`;
        });
        optionsHtml += `</optgroup>`;
        
        // Add Attributes
        const attributes = optgroups[1];
        optionsHtml += `<optgroup label="Attributes">`;
        attributes.querySelectorAll('option').forEach(option => {
            optionsHtml += `<option value="${option.value}">${option.textContent}</option>`;
        });
        optionsHtml += `</optgroup>`;
        
        // Add Semantic Tags
        optionsHtml += `<optgroup label="Semantic Tags">`;
        optionsHtml += `<option value="semantic_tag">Semantic Tag</option>`;
        optionsHtml += `</optgroup>`;
        
        return optionsHtml;
    }

    // Initialize Wikidata search functionality
    function initializeWikidataSearch(input) {
        const resultsContainer = input.parentElement.querySelector('.wikidata-results');
        const hiddenInput = input.parentElement.querySelector('.wikidata-tag-id');
        let debounceTimer;

        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value.trim();
                if (query.length >= 2) {
                    fetch(`/wikidata-search/?q=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            displayWikidataResults(data.results, resultsContainer, input, hiddenInput);
                        });
                } else {
                    resultsContainer.classList.add('d-none');
                }
            }, 300);
        });

        // Close results when clicking outside
        document.addEventListener('click', function(event) {
            if (!input.contains(event.target) && !resultsContainer.contains(event.target)) {
                resultsContainer.classList.add('d-none');
            }
        });
    }

    function displayWikidataResults(results, container, input, hiddenInput) {
        container.innerHTML = '';
        container.classList.remove('d-none');

        results.forEach(result => {
            const div = document.createElement('div');
            div.className = 'wikidata-result-item';
            div.innerHTML = `
                <strong>${result.label}</strong>
                ${result.description ? `<br><small>${result.description}</small>` : ''}
            `;
            div.addEventListener('click', () => {
                input.value = result.label;
                hiddenInput.value = result.id;
                container.classList.add('d-none');
            });
            container.appendChild(div);
        });
    }

    function initializeLocationSearch(input) {
        const resultsContainer = input.parentElement.querySelector('.location-search-results');
        let debounceTimer;

        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value.trim();
                if (query.length >= 2) {
                    // Use OpenStreetMap Nominatim API for location search
                    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`)
                        .then(response => response.json())
                        .then(data => {
                            displayLocationResults(data, resultsContainer, input);
                        })
                        .catch(error => console.error('Error fetching locations:', error));
                } else {
                    resultsContainer.classList.add('d-none');
                }
            }, 300);
        });

        // Close results when clicking outside
        document.addEventListener('click', function(event) {
            if (!input.contains(event.target) && !resultsContainer.contains(event.target)) {
                resultsContainer.classList.add('d-none');
            }
        });
    }

    function displayLocationResults(results, container, input) {
        container.innerHTML = '';
        container.classList.remove('d-none');

        if (results.length === 0) {
            container.innerHTML = '<div class="p-2">No locations found</div>';
            return;
        }

        results.forEach(result => {
            const div = document.createElement('div');
            div.className = 'location-result-item p-2';
            div.innerHTML = `
                <strong>${result.display_name}</strong>
            `;
            div.addEventListener('click', () => {
                input.value = result.display_name;
                container.classList.add('d-none');
            });
            container.appendChild(div);
        });
    }

    // Add styles for location search results
    const style = document.createElement('style');
    style.textContent = `
        .location-search-results {
            position: absolute;
            background: white;
            border: 1px solid #ddd;
            max-height: 200px;
            overflow-y: auto;
            width: 100%;
            z-index: 1000;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .location-result-item {
            cursor: pointer;
            border-bottom: 1px solid #eee;
        }
        .location-result-item:hover {
            background-color: #f5f5f5;
        }
    `;
    document.head.appendChild(style);

    // Initialize the first search field
    const firstField = document.querySelector('.search-field-container');
    if (firstField) {
        const attributeSelect = firstField.querySelector('.attribute-select');
        const searchInput = firstField.querySelector('.search-term');
        initializeAttributeSelect(attributeSelect, searchInput);
    }

    // Handle adding new search fields
    document.getElementById('addField')?.addEventListener('click', function() {
        // ... existing add field code ...
        const newField = document.querySelector('.search-field-container:last-child');
        const attributeSelect = newField.querySelector('.attribute-select');
        const searchInput = newField.querySelector('.search-term');
        initializeAttributeSelect(attributeSelect, searchInput);
    });
}); 