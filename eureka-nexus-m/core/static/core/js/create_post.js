console.log('Loading create_post.js...');

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
    
    if (typeof attributeConfig === 'undefined') {
        console.error('attributeConfig is not defined!');
        return;
    }

    const attributeSelector = document.getElementById('attributeSelector');
    if (!attributeSelector) {
        console.error('Attribute selector not found!');
        return;
    }

    const selectedAttributes = document.getElementById('selectedAttributes');
    if (!selectedAttributes) {
        console.error('Selected attributes container not found!');
        return;
    }

    console.log('Initial setup complete');
    console.log('Attribute Config:', attributeConfig);

    const selectedAttributeIds = new Set();

    attributeSelector.addEventListener('change', function() {
        const attributeId = this.value;
        console.log('Selected attribute:', attributeId);
        if (!attributeId || selectedAttributeIds.has(attributeId)) {
            this.value = '';
            return;
        }

        const config = attributeConfig[attributeId];
        console.log('Config for selected attribute:', config);
        const container = createAttributeContainer(attributeId, config);
        selectedAttributes.appendChild(container);
        selectedAttributeIds.add(attributeId);
        this.value = '';
    });

    function createAttributeContainer(attributeId, config) {
        console.log('Creating container for:', attributeId, config);
        const container = document.createElement('div');
        container.className = 'attribute-container';
        container.dataset.attributeId = attributeId;

        const removeBtn = document.createElement('button');
        removeBtn.type = 'button';
        removeBtn.className = 'btn btn-danger btn-sm remove-attribute';
        removeBtn.textContent = '×';
        removeBtn.addEventListener('click', () => {
            container.remove();
            selectedAttributeIds.delete(attributeId);
        });

        const label = document.createElement('label');
        label.className = 'form-label';
        label.textContent = config.label;

        container.appendChild(removeBtn);
        container.appendChild(label);

        if (config.type === 'complex') {
            if (attributeId === 'weight') {
                container.appendChild(createWeightInputs(config));
            } else if (attributeId === 'size') {
                container.appendChild(createSizeInputs(config));
            }
        } else {
            if (config.choices) {
                console.log('Adding choices for:', attributeId, config.choices);
                // Add dropdown for choices
                const select = document.createElement('select');
                select.className = 'form-select';
                select.name = attributeId;
                
                config.choices.forEach(([value, label]) => {
                    const option = document.createElement('option');
                    option.value = value;
                    option.textContent = label;
                    select.appendChild(option);
                });

                container.appendChild(select);

                if (config.customField) {
                    const customInput = document.createElement('input');
                    customInput.type = 'text';
                    customInput.className = 'form-control';
                    customInput.name = `custom_${attributeId}`;
                    customInput.maxLength = config.maxLength;
                    customInput.style.display = 'none';

                    select.addEventListener('change', () => {
                        customInput.style.display = select.value === 'other' ? 'block' : 'none';
                    });

                    container.appendChild(customInput);
                }
            } else {
                console.log('Adding regular input for:', attributeId);
                // Add regular input field
                const input = document.createElement('input');
                input.type = 'text';
                input.className = 'form-control';
                input.name = attributeId;
                input.maxLength = config.maxLength;
                container.appendChild(input);

                if (config.hasExactness) {
                    const exactnessSelect = document.createElement('select');
                    exactnessSelect.className = 'form-select';
                    exactnessSelect.name = `${attributeId}_exactness`;
                    
                    [['exact', 'Exact'], ['approximate', 'Approximate']].forEach(([value, label]) => {
                        const option = document.createElement('option');
                        option.value = value;
                        option.textContent = label;
                        exactnessSelect.appendChild(option);
                    });

                    container.appendChild(exactnessSelect);
                }
            }
        }

        return container;
    }

    function createWeightInputs(config) {
        const wrapper = document.createElement('div');
        wrapper.className = 'weight-inputs';

        // Type selector (Exact/Approximate)
        const typeSelect = document.createElement('select');
        typeSelect.className = 'form-select mb-2';
        typeSelect.name = 'weight_type';
        config.exactnessChoices.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            typeSelect.appendChild(option);
        });

        // Approximate weight section
        const approxSection = document.createElement('div');
        approxSection.className = 'approximate-weight-section';
        const approxSelect = document.createElement('select');
        approxSelect.className = 'form-select mb-2';
        approxSelect.name = 'approximate_weight';
        config.approximateChoices.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            approxSelect.appendChild(option);
        });

        const customApproxInput = document.createElement('input');
        customApproxInput.type = 'text';
        customApproxInput.className = 'form-control';
        customApproxInput.name = 'custom_approximate_weight';
        customApproxInput.style.display = 'none';
        approxSection.appendChild(approxSelect);
        approxSection.appendChild(customApproxInput);

        // Exact weight section
        const exactSection = document.createElement('div');
        exactSection.className = 'exact-weight-section';
        const exactInput = document.createElement('input');
        exactInput.type = 'number';
        exactInput.className = 'form-control mb-2';
        exactInput.name = 'exact_weight';
        exactInput.step = '0.01';

        const unitSelect = document.createElement('select');
        unitSelect.className = 'form-select';
        unitSelect.name = 'weight_unit';
        config.units.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            unitSelect.appendChild(option);
        });

        exactSection.appendChild(exactInput);
        exactSection.appendChild(unitSelect);
        exactSection.style.display = 'none';

        // Event listeners
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

    function createSizeInputs(config) {
        const wrapper = document.createElement('div');
        wrapper.className = 'size-inputs';

        // Type selector (Exact/Approximate)
        const typeSelect = document.createElement('select');
        typeSelect.className = 'form-select mb-2';
        typeSelect.name = 'size_type';
        config.exactnessChoices.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            typeSelect.appendChild(option);
        });

        // Approximate size section
        const approxSection = document.createElement('div');
        approxSection.className = 'approximate-size-section';
        const approxInput = document.createElement('input');
        approxInput.type = 'text';
        approxInput.className = 'form-control';
        approxInput.name = 'approximate_size';
        approxSection.appendChild(approxInput);

        // Exact size section
        const exactSection = document.createElement('div');
        exactSection.className = 'exact-size-section';
        
        ['width', 'height', 'depth'].forEach(dim => {
            const input = document.createElement('input');
            input.type = 'number';
            input.className = 'form-control mb-2';
            input.name = dim;
            input.placeholder = `${dim.charAt(0).toUpperCase() + dim.slice(1)} (${dim.charAt(0)})`;
            input.step = '0.01';
            exactSection.appendChild(input);
        });

        const unitSelect = document.createElement('select');
        unitSelect.className = 'form-select';
        unitSelect.name = 'size_unit';
        config.units.forEach(([value, label]) => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = label;
            unitSelect.appendChild(option);
        });
        exactSection.appendChild(unitSelect);
        exactSection.style.display = 'none';

        // Event listeners
        typeSelect.addEventListener('change', () => {
            approxSection.style.display = typeSelect.value === 'approximate' ? 'block' : 'none';
            exactSection.style.display = typeSelect.value === 'exact' ? 'block' : 'none';
        });

        wrapper.appendChild(typeSelect);
        wrapper.appendChild(approxSection);
        wrapper.appendChild(exactSection);

        return wrapper;
    }
}); 