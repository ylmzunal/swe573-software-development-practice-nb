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
            if (this.value === 'semantic_tag') {
                initializeWikidataSearch(searchInput);
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
                        <option value="">Select attribute...</option>
                        <optgroup label="Basic Fields">
                            <option value="title">Title</option>
                            <option value="description">Description</option>
                        </optgroup>
                        <optgroup label="Attributes">
                            ${getAttributeOptions()}
                        </optgroup>
                        <optgroup label="Semantic Tags">
                            <option value="semantic_tag">Semantic Tag</option>
                        </optgroup>
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
        const availableAttributes = [
            {name: 'color', display_name: 'Color'},
            {name: 'size', display_name: 'Size'},
            {name: 'weight', display_name: 'Weight'},
            {name: 'condition', display_name: 'Condition'},
            {name: 'material', display_name: 'Material'},
            {name: 'shape', display_name: 'Shape'}
        ];
        
        return availableAttributes.map(attr => 
            `<option value="${attr.name}">${attr.display_name}</option>`
        ).join('');
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
}); 