console.log('Loading create_post.js...');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
    
    if (typeof attributeConfig === 'undefined') {
        console.error('attributeConfig is not defined!');
        return;
    }

    const attributeSelector = document.getElementById('attributeSelector');
    const selectedAttributes = document.getElementById('selectedAttributes');
    
    if (!attributeSelector || !selectedAttributes) {
        console.error('Required elements not found!');
        return;
    }

    console.log('Initial setup complete');

    let attributeInstanceCounter = {};

    attributeSelector.addEventListener('change', function() {
        const attributeId = this.value;
        console.log('Selected attribute:', attributeId);
        
        if (!attributeId) {
            this.value = '';
            return;
        }

        if (!attributeInstanceCounter[attributeId]) {
            attributeInstanceCounter[attributeId] = 0;
        }
        attributeInstanceCounter[attributeId]++;

        const instanceId = `${attributeId}_${attributeInstanceCounter[attributeId]}`;
        const config = attributeConfig[attributeId];
        console.log('Creating instance:', instanceId);
        
        const container = createAttributeContainer(attributeId, instanceId, config);
        selectedAttributes.appendChild(container);
        this.value = '';
    });

    function createAttributeContainer(attributeId, instanceId, config) {
        console.log('Creating container for:', attributeId, instanceId);
        const container = document.createElement('div');
        container.className = 'attribute-container';
        container.dataset.attributeId = attributeId;
        container.dataset.instanceId = instanceId;

        const header = document.createElement('div');
        header.className = 'd-flex justify-content-between align-items-center mb-2';

        const label = document.createElement('label');
        label.className = 'form-label mb-0';
        label.textContent = `${config.label} ${attributeInstanceCounter[attributeId]}`;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn btn-danger btn-sm';
        removeBtn.textContent = '×';
        removeBtn.addEventListener('click', () => {
            container.remove();
        });

        header.appendChild(label);
        header.appendChild(removeBtn);
        container.appendChild(header);

        const inputSection = document.createElement('div');
        inputSection.className = 'attribute-inputs';

        if (config.type === 'complex') {
            if (attributeId === 'weight') {
                inputSection.appendChild(createWeightInputs(config, instanceId));
            } else if (attributeId === 'size') {
                inputSection.appendChild(createSizeInputs(config, instanceId));
            }
        } else if (config.type === 'location') {
            const locationContainer = document.createElement('div');
            locationContainer.className = 'input-group';
            
            const locationInput = document.createElement('input');
            locationInput.type = 'text';
            locationInput.className = 'form-control';
            locationInput.name = `${attributeId}[${instanceId}]`;
            locationInput.maxLength = config.maxLength;
            locationInput.placeholder = 'Enter location...';
            locationInput.autocomplete = 'off';
            
            const locationButton = document.createElement('button');
            locationButton.type = 'button';
            locationButton.className = 'btn btn-outline-secondary';
            locationButton.innerHTML = '<i class="fas fa-map-marker-alt"></i> Use My Location';
            
            const resultsDiv = document.createElement('div');
            resultsDiv.className = 'location-results position-absolute w-100 bg-white border rounded shadow-sm';
            resultsDiv.style.display = 'none';
            resultsDiv.style.zIndex = '1000';
            resultsDiv.style.maxHeight = '300px';
            resultsDiv.style.overflowY = 'auto';
            
            // Initialize location search functionality
            initializeLocationSearch(locationInput, resultsDiv, locationButton);
            
            locationContainer.appendChild(locationInput);
            locationContainer.appendChild(locationButton);
            locationContainer.appendChild(resultsDiv);
            inputSection.appendChild(locationContainer);
        } else {
            if (config.choices) {
                const select = document.createElement('select');
                select.className = 'form-select';
                select.name = `${attributeId}[${instanceId}]`;
                
                config.choices.forEach(([value, label]) => {
                    const option = document.createElement('option');
                    option.value = value;
                    option.textContent = label;
                    select.appendChild(option);
                });

                inputSection.appendChild(select);

                if (config.customField) {
                    const customInput = document.createElement('input');
                    customInput.type = 'text';
                    customInput.className = 'form-control mt-2';
                    customInput.name = `custom_${attributeId}[${instanceId}]`;
                    customInput.maxLength = config.maxLength;
                    customInput.style.display = 'none';

                    select.addEventListener('change', () => {
                        customInput.style.display = select.value === 'other' ? 'block' : 'none';
                    });

                    inputSection.appendChild(customInput);
                }
            } else {
                const input = document.createElement('input');
                input.type = 'text';
                input.className = 'form-control';
                input.name = `${attributeId}[${instanceId}]`;
                input.maxLength = config.maxLength;
                inputSection.appendChild(input);
            }
        }

        container.appendChild(inputSection);
        return container;
    }

    function createWeightInputs(config, instanceId) {
        const wrapper = document.createElement('div');
        wrapper.className = 'weight-inputs';

        const typeSelect = document.createElement('select');
        typeSelect.className = 'form-select mb-2';
        typeSelect.name = `weight_type[${instanceId}]`;
        config.exactnessChoices.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            typeSelect.appendChild(option);
        });

        const approxSection = document.createElement('div');
        approxSection.className = 'approximate-weight-section';
        const approxSelect = document.createElement('select');
        approxSelect.className = 'form-select mb-2';
        approxSelect.name = `approximate_weight[${instanceId}]`;
        config.approximateChoices.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            approxSelect.appendChild(option);
        });

        const customApproxInput = document.createElement('input');
        customApproxInput.type = 'text';
        customApproxInput.className = 'form-control';
        customApproxInput.name = `custom_approximate_weight[${instanceId}]`;
        customApproxInput.style.display = 'none';
        approxSection.appendChild(approxSelect);
        approxSection.appendChild(customApproxInput);

        const exactSection = document.createElement('div');
        exactSection.className = 'exact-weight-section';
        const exactInput = document.createElement('input');
        exactInput.type = 'number';
        exactInput.className = 'form-control mb-2';
        exactInput.name = `exact_weight[${instanceId}]`;
        exactInput.step = '0.01';

        const unitSelect = document.createElement('select');
        unitSelect.className = 'form-select';
        unitSelect.name = `weight_unit[${instanceId}]`;
        config.units.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            unitSelect.appendChild(option);
        });

        exactSection.appendChild(exactInput);
        exactSection.appendChild(unitSelect);
        exactSection.style.display = 'none';

        typeSelect.addEventListener('change', () => {
            approxSection.style.display = typeSelect.value === 'approximate' ? 'block' : 'none';
            exactSection.style.display = typeSelect.value === 'exact' ? 'block' : 'none';
        });

        approxSelect.addEventListener('change', () => {
            customApproxInput.style.display = approxSelect.value === 'other' ? 'block' : 'none';
        });

        wrapper.appendChild(typeSelect);
        wrapper.appendChild(approxSection);
        wrapper.appendChild(exactSection);

        return wrapper;
    }

    function createSizeInputs(config, instanceId) {
        const wrapper = document.createElement('div');
        wrapper.className = 'size-inputs';

        const typeSelect = document.createElement('select');
        typeSelect.className = 'form-select mb-2';
        typeSelect.name = `size_type[${instanceId}]`;
        config.exactnessChoices.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            typeSelect.appendChild(option);
        });

        const approxSection = document.createElement('div');
        approxSection.className = 'approximate-size-section';
        const approxInput = document.createElement('input');
        approxInput.type = 'text';
        approxInput.className = 'form-control';
        approxInput.name = `approximate_size[${instanceId}]`;
        approxSection.appendChild(approxInput);

        const exactSection = document.createElement('div');
        exactSection.className = 'exact-size-section';
        
        ['width', 'height', 'depth'].forEach(dim => {
            const input = document.createElement('input');
            input.type = 'number';
            input.className = 'form-control mb-2';
            input.name = `${dim}[${instanceId}]`;
            input.placeholder = `${dim.charAt(0).toUpperCase() + dim.slice(1)} (${dim.charAt(0)})`;
            input.step = '0.01';
            exactSection.appendChild(input);
        });

        const unitSelect = document.createElement('select');
        unitSelect.className = 'form-select';
        unitSelect.name = `size_unit[${instanceId}]`;
        config.units.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            unitSelect.appendChild(option);
        });
        exactSection.appendChild(unitSelect);
        exactSection.style.display = 'none';

        typeSelect.addEventListener('change', () => {
            approxSection.style.display = typeSelect.value === 'approximate' ? 'block' : 'none';
            exactSection.style.display = typeSelect.value === 'exact' ? 'block' : 'none';
        });

        wrapper.appendChild(typeSelect);
        wrapper.appendChild(approxSection);
        wrapper.appendChild(exactSection);

        return wrapper;
    }

    function initializeLocationSearch(input, resultsDiv, locationButton) {
        let debounceTimer;

        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                const query = this.value.trim();
                if (query.length >= 2) {
                    searchLocations(query, resultsDiv, input);
                } else {
                    resultsDiv.style.display = 'none';
                }
            }, 300);
        });

        // Close results when clicking outside
        document.addEventListener('click', function(event) {
            if (!input.contains(event.target) && !resultsDiv.contains(event.target)) {
                resultsDiv.style.display = 'none';
            }
        });

        // Handle "Use My Location" button
        locationButton.addEventListener('click', function() {
            if (navigator.geolocation) {
                locationButton.disabled = true;
                locationButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Getting location...';
                
                navigator.geolocation.getCurrentPosition(
                    async function(position) {
                        try {
                            const response = await fetch(
                                `https://nominatim.openstreetmap.org/reverse?lat=${position.coords.latitude}&lon=${position.coords.longitude}&format=json`
                            );
                            const data = await response.json();
                            input.value = data.display_name;
                        } catch (error) {
                            console.error('Error getting location:', error);
                            alert('Failed to get location. Please enter manually.');
                        } finally {
                            locationButton.disabled = false;
                            locationButton.innerHTML = '<i class="fas fa-map-marker-alt"></i> Use My Location';
                        }
                    },
                    function(error) {
                        console.error('Geolocation error:', error);
                        alert('Unable to get location. Please enter manually.');
                        locationButton.disabled = false;
                        locationButton.innerHTML = '<i class="fas fa-map-marker-alt"></i> Use My Location';
                    }
                );
            } else {
                alert('Geolocation is not supported by your browser');
            }
        });
    }

    function searchLocations(query, resultsDiv, input) {
        fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displayLocationResults(data, resultsDiv, input);
            })
            .catch(error => {
                console.error('Error fetching locations:', error);
                resultsDiv.innerHTML = '<div class="p-2 text-danger">Error fetching locations</div>';
                resultsDiv.style.display = 'block';
            });
    }

    function displayLocationResults(results, resultsDiv, input) {
        resultsDiv.innerHTML = '';
        
        if (results.length === 0) {
            resultsDiv.innerHTML = '<div class="p-2">No locations found</div>';
            resultsDiv.style.display = 'block';
            return;
        }

        results.forEach(result => {
            const div = document.createElement('div');
            div.className = 'location-result-item p-2';
            div.innerHTML = `
                <strong>${result.display_name}</strong>
                ${result.type ? `<br><small>${result.type}</small>` : ''}
            `;
            
            div.addEventListener('click', () => {
                input.value = result.display_name;
                resultsDiv.style.display = 'none';
            });
            
            resultsDiv.appendChild(div);
        });
        
        resultsDiv.style.display = 'block';
    }
}); 