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

        const inputGroup = document.createElement('div');
        inputGroup.className = 'input-group';

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

            inputGroup.appendChild(select);

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

                inputGroup.appendChild(customInput);
            }
        } else {
            console.log('Adding regular input for:', attributeId);
            // Add regular input field
            const input = document.createElement('input');
            input.type = 'text';
            input.className = 'form-control';
            input.name = attributeId;
            input.maxLength = config.maxLength;
            inputGroup.appendChild(input);

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

                inputGroup.appendChild(exactnessSelect);
            }
        }

        container.appendChild(removeBtn);
        container.appendChild(label);
        container.appendChild(inputGroup);

        return container;
    }
}); 