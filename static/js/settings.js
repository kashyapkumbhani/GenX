document.addEventListener('DOMContentLoaded', function() {
    let apiKeyCounter = 0;
    const apiKeyContainer = document.getElementById('apiKeyContainer');
    const addApiKeyBtn = document.getElementById('addApiKeyBtn');
    const apiKeyForm = document.getElementById('apiKeyForm');

    // Load existing API keys on page load
    loadExistingApiKeys();

    // Add new API key
    addApiKeyBtn.addEventListener('click', function() {
        addApiKeyField();
    });

    // Form submission
    apiKeyForm.addEventListener('submit', function(e) {
        e.preventDefault();
        saveApiKeys();
    });

    function loadExistingApiKeys() {
        // Get existing API keys from the server
        fetch('/get_api_keys')
            .then(response => response.json())
            .then(data => {
                if (data.api_keys && data.api_keys.length > 0) {
                    data.api_keys.forEach((key, index) => {
                        if (key && key.trim() !== '') {
                            addApiKeyField(key, index === 0);
                        }
                    });
                }
                // Always ensure at least one API key field exists
                if (apiKeyCounter === 0) {
                    addApiKeyField('', true);
                }
            })
            .catch(error => {
                console.error('Error loading API keys:', error);
                // Add at least one field if loading fails
                addApiKeyField('', true);
            });
    }

    function addApiKeyField(value = '', isPrimary = false) {
        apiKeyCounter++;
        const keyId = `apiKey${apiKeyCounter}`;
        
        const formGroup = document.createElement('div');
        formGroup.className = 'form-group api-key-group';
        formGroup.dataset.keyId = keyId;
        
        formGroup.innerHTML = `
            <label for="${keyId}">API Key ${apiKeyCounter}${isPrimary ? ' (Primary)' : ''}</label>
            <div class="api-key-input">
                <input type="password" id="${keyId}" name="${keyId}" 
                       value="${value}" 
                       placeholder="${isPrimary ? 'Enter your primary Gemini API key' : 'Enter additional API key'}">
                <button type="button" class="btn-toggle-visibility" data-target="${keyId}">Show</button>
                <button type="button" class="btn-test-key" data-key-id="${keyId}">Test</button>
                ${!isPrimary ? '<button type="button" class="btn-delete-key" data-key-id="' + keyId + '">×</button>' : ''}
            </div>
            <div class="api-key-status" id="${keyId}Status"></div>
        `;
        
        apiKeyContainer.appendChild(formGroup);
        
        // Add event listeners for the new buttons
        const toggleBtn = formGroup.querySelector('.btn-toggle-visibility');
        const testBtn = formGroup.querySelector('.btn-test-key');
        const deleteBtn = formGroup.querySelector('.btn-delete-key');
        
        toggleBtn.addEventListener('click', function() {
            toggleApiKeyVisibility(keyId);
        });
        
        testBtn.addEventListener('click', function() {
            testApiKey(keyId);
        });
        
        if (deleteBtn) {
            deleteBtn.addEventListener('click', function() {
                deleteApiKey(keyId);
            });
        }
    }

    function deleteApiKey(keyId) {
        const formGroup = document.querySelector(`[data-key-id="${keyId}"]`).closest('.api-key-group');
        if (formGroup) {
            formGroup.remove();
            // Renumber remaining keys
            renumberApiKeys();
        }
    }

    function renumberApiKeys() {
        const apiKeyGroups = apiKeyContainer.querySelectorAll('.api-key-group');
        apiKeyGroups.forEach((group, index) => {
            const label = group.querySelector('label');
            const isPrimary = index === 0;
            label.textContent = `API Key ${index + 1}${isPrimary ? ' (Primary)' : ''}`;
            
            const input = group.querySelector('input');
            if (isPrimary) {
                input.placeholder = 'Enter your primary Gemini API key';
            } else {
                input.placeholder = 'Enter additional API key';
            }
        });
    }

    function toggleApiKeyVisibility(keyId) {
        const input = document.getElementById(keyId);
        const button = document.querySelector(`[data-target="${keyId}"]`);
        
        if (input.type === 'password') {
            input.type = 'text';
            button.textContent = 'Hide';
        } else {
            input.type = 'password';
            button.textContent = 'Show';
        }
    }

    function testApiKey(keyId) {
        const input = document.getElementById(keyId);
        const statusDiv = document.getElementById(`${keyId}Status`);
        const testBtn = document.querySelector(`[data-key-id="${keyId}"].btn-test-key`);
        
        const apiKey = input.value.trim();
        if (!apiKey) {
            statusDiv.textContent = 'Please enter an API key first';
            statusDiv.className = 'api-key-status error';
            return;
        }
        
        testBtn.disabled = true;
        testBtn.textContent = 'Testing...';
        statusDiv.textContent = 'Testing API key...';
        statusDiv.className = 'api-key-status';
        
        fetch('/test_api_key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ api_key: apiKey })
        })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                statusDiv.textContent = 'API key is valid ✓';
                statusDiv.className = 'api-key-status success';
            } else {
                statusDiv.textContent = `API key is invalid: ${data.error}`;
                statusDiv.className = 'api-key-status error';
            }
        })
        .catch(error => {
            statusDiv.textContent = `Error testing API key: ${error.message}`;
            statusDiv.className = 'api-key-status error';
        })
        .finally(() => {
            testBtn.disabled = false;
            testBtn.textContent = 'Test';
        });
    }

    function saveApiKeys() {
        const apiKeys = [];
        const inputs = apiKeyContainer.querySelectorAll('input[type="password"], input[type="text"]');
        
        inputs.forEach(input => {
            const value = input.value.trim();
            if (value) {
                apiKeys.push(value);
            }
        });
        
        if (apiKeys.length === 0) {
            alert('Please add at least one API key');
            return;
        }
        
        const saveBtn = document.querySelector('.btn-save');
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
        
        fetch('/save_api_keys', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ api_keys: apiKeys })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('API keys saved successfully!');
                // Clear status messages
                const statusDivs = document.querySelectorAll('.api-key-status');
                statusDivs.forEach(div => {
                    div.textContent = '';
                    div.className = 'api-key-status';
                });
            } else {
                alert(`Error saving API keys: ${data.error}`);
            }
        })
        .catch(error => {
            alert(`Error saving API keys: ${error.message}`);
        })
        .finally(() => {
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save API Keys';
        });
    }
});