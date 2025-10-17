document.addEventListener('DOMContentLoaded', function() {
    // Add event listener for business category dropdown
    const businessCategorySelect = document.getElementById('businessCategory');
    const customCategoryInput = document.getElementById('customCategory');
    
    if (businessCategorySelect && customCategoryInput) {
        businessCategorySelect.addEventListener('change', function() {
            if (this.value === 'custom') {
                customCategoryInput.style.display = 'block';
                customCategoryInput.focus();
            } else {
                customCategoryInput.style.display = 'none';
            }
        });
    }
    
    // AI Generation Event Listeners
    const generateServicesBtn = document.getElementById('generateServicesBtn');
    const generateCitiesBtn = document.getElementById('generateCitiesBtn');
    
    if (generateServicesBtn) {
        generateServicesBtn.addEventListener('click', function() {
            generateServices();
        });
    }
    
    if (generateCitiesBtn) {
        generateCitiesBtn.addEventListener('click', function() {
            generateCities();
        });
    }
    
    // Multi-step form navigation
    const form = document.getElementById('businessForm');
    const steps = document.querySelectorAll('.step-content');
    const stepIndicators = document.querySelectorAll('.step');
    const nextButtons = document.querySelectorAll('.btn-next');
    const prevButtons = document.querySelectorAll('.btn-prev');
    const generateBtn = document.getElementById('generateBtn');
    const autofillBtn = document.querySelector('.btn-autofill');
    
    // Next button click handler
    nextButtons.forEach(button => {
        button.addEventListener('click', function() {
            const currentStep = button.closest('.step-content');
            const currentStepNum = parseInt(currentStep.dataset.step);
            const nextStepNum = currentStepNum + 1;
            
            // Validate current step
            if (validateStep(currentStepNum)) {
                // Hide current step
                currentStep.classList.remove('active');
                
                // Show next step
                const nextStep = document.querySelector(`.step-content[data-step="${nextStepNum}"]`);
                nextStep.classList.add('active');
                
                // Update step indicator
                stepIndicators.forEach(step => {
                    if (parseInt(step.dataset.step) === nextStepNum) {
                        step.classList.add('active');
                    } else if (parseInt(step.dataset.step) === currentStepNum) {
                        step.classList.remove('active');
                    }
                });
                
                // If moving to review step, populate review content
                if (nextStepNum === 4) {
                    populateReview();
                }
            }
        });
    });
    
    // Previous button click handler
    prevButtons.forEach(button => {
        button.addEventListener('click', function() {
            const currentStep = button.closest('.step-content');
            const currentStepNum = parseInt(currentStep.dataset.step);
            const prevStepNum = currentStepNum - 1;
            
            // Hide current step
            currentStep.classList.remove('active');
            
            // Show previous step
            const prevStep = document.querySelector(`.step-content[data-step="${prevStepNum}"]`);
            prevStep.classList.add('active');
            
            // Update step indicator
            stepIndicators.forEach(step => {
                if (parseInt(step.dataset.step) === prevStepNum) {
                    step.classList.add('active');
                } else if (parseInt(step.dataset.step) === currentStepNum) {
                    step.classList.remove('active');
                }
            });
        });
    });
    
    // Generate button click handler
    if (generateBtn) {
        generateBtn.addEventListener('click', function() {
            if (validateStep(4)) {
                const formData = collectFormData();
                
                // Show loading state
                generateBtn.textContent = 'Generating...';
                generateBtn.disabled = true;
                
                // Send data to server
                fetch('/submit_business_data', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        alert('Site generation started! You will be redirected to track the progress.');
                        window.location.href = data.redirect_url;
                    } else {
                        alert('Error starting site generation: ' + data.message);
                        generateBtn.textContent = 'Generate Site';
                        generateBtn.disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred while generating the site.');
                    generateBtn.textContent = 'Generate Site';
                    generateBtn.disabled = false;
                });
            }
        });
    }
    
    // Autofill button click handler
    if (autofillBtn) {
        autofillBtn.addEventListener('click', function() {
            // Autofill form with sample data
            document.getElementById('businessName').value = 'ABC Plumbing Services';
            document.getElementById('phoneNumber').value = '(555) 123-4567';
            document.getElementById('email').value = 'contact@abcplumbing.com';
            document.getElementById('address').value = '123 Main Street';
            document.getElementById('city').value = 'Austin';
            document.getElementById('state').value = 'Texas';
            document.getElementById('zipCode').value = '78701';
            document.getElementById('website').value = 'https://abcplumbing.com';
            document.getElementById('primaryKeyword').value = 'Plumber';
            document.getElementById('additionalServices').value = 'Emergency Plumbing, Drain Cleaning, Water Heater Installation, Leak Detection';
            document.getElementById('serviceAreas').value = 'Austin, Round Rock, Cedar Park, Georgetown, Pflugerville';
        });
    }
    
    // Form validation
    function validateStep(stepNum) {
        const stepContent = document.querySelector(`.step-content[data-step="${stepNum}"]`);
        const requiredFields = stepContent.querySelectorAll('[required]');
        let valid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('error');
                valid = false;
            } else {
                field.classList.remove('error');
            }
        });
        
        return valid;
    }
    
    // Collect form data
    function collectFormData() {
        // Get category value - either from dropdown or custom input
        let categoryValue = document.getElementById('businessCategory').value;
        if (categoryValue === 'custom') {
            categoryValue = document.getElementById('customCategory').value;
        }
        
        const formData = {
            business: {
                name: document.getElementById('businessName').value,
                phone: document.getElementById('phoneNumber').value,
                email: document.getElementById('email').value,
                address: document.getElementById('address').value,
                city: document.getElementById('city').value,
                state: document.getElementById('state').value,
                zipCode: document.getElementById('zipCode').value,
                website: document.getElementById('website').value,
                category: categoryValue
            },
            primary_keyword: document.getElementById('primaryKeyword').value,
            additional_services: document.getElementById('additionalServices').value.split(',').map(s => s.trim()).filter(s => s),
            service_areas: document.getElementById('serviceAreas').value.split(',').map(area => {
                const trimmedArea = area.trim();
                return {
                    city: trimmedArea
                };
            }).filter(area => area.city),
            template: document.getElementById('template').value
        };
        
        return formData;
    }
    
    // Populate review step
    function populateReview() {
        const reviewContent = document.getElementById('reviewContent');
        const formData = collectFormData();
        
        // Calculate page count
        const pageCount = 1 + formData.service_areas.length; // 1 index page + location pages
        document.getElementById('pageCount').textContent = pageCount;
        
        // Build review HTML
        let reviewHTML = `
            <div class="review-section">
                <h3>Business Information</h3>
                <div class="review-item">
                    <div class="review-label">Business Name:</div>
                    <div class="review-value">${formData.business.name}</div>
                </div>
                <div class="review-item">
                    <div class="review-label">Contact:</div>
                    <div class="review-value">${formData.business.phone} | ${formData.business.email}</div>
                </div>
                <div class="review-item">
                    <div class="review-label">Address:</div>
                    <div class="review-value">${formData.business.address}, ${formData.business.city}, ${formData.business.state} ${formData.business.zipCode}</div>
                </div>
            </div>
            
            <div class="review-section">
                <h3>Services & Keywords</h3>
                <div class="review-item">
                    <div class="review-label">Primary Keyword:</div>
                    <div class="review-value">${formData.primary_keyword}</div>
                </div>
                <div class="review-item">
                    <div class="review-label">Additional Services:</div>
                    <div class="review-value">${formData.additional_services.join(', ') || 'None'}</div>
                </div>
            </div>
            
            <div class="review-section">
                <h3>Service Areas</h3>
                <div class="review-item">
                    <div class="review-value">${formData.service_areas.map(area => area.state ? `${area.city}, ${area.state}` : area.city).join('<br>')}</div>
                </div>
            </div>
            
            <div class="review-section">
                <h3>Template</h3>
                <div class="review-item">
                    <div class="review-value">${formData.template}</div>
                </div>
            </div>
        `;
        
        reviewContent.innerHTML = reviewHTML;
    }
    
    // Template selection handler
    const templateSelect = document.getElementById('template');
    if (templateSelect) {
        templateSelect.addEventListener('change', function() {
            updateTemplateDetails();
        });
        
        // Initialize template details on page load
        updateTemplateDetails();
    }
    
    // Update template details display
    function updateTemplateDetails() {
        const templateSelect = document.getElementById('template');
        const templateDetails = document.getElementById('templateDetails');
        
        if (templateSelect && templateDetails) {
            const selectedOption = templateSelect.options[templateSelect.selectedIndex];
            const templateName = selectedOption.value;
            const templateText = selectedOption.text;
            
            templateDetails.innerHTML = `
                <p><strong>Template:</strong> ${templateText}</p>
                <p><strong>Description:</strong> Professional template optimized for local businesses</p>
            `;
        }
    }
    
    // AI Generation Functions
    async function generateServices() {
        const generateBtn = document.getElementById('generateServicesBtn');
        const servicesTextarea = document.getElementById('additionalServices');
        const businessCategorySelect = document.getElementById('businessCategory');
        const customCategoryInput = document.getElementById('customCategory');
        const primaryKeywordInput = document.getElementById('primaryKeyword');
        const quantityInput = document.getElementById('servicesQuantity');
        
        // Get business category
        let businessCategory = businessCategorySelect.value;
        if (businessCategory === 'custom') {
            businessCategory = customCategoryInput.value.trim();
        }
        
        const primaryKeyword = primaryKeywordInput.value.trim();
        const quantity = parseInt(quantityInput.value) || 5;
        
        // Validation
        if (!businessCategory || !primaryKeyword) {
            alert('Please fill in Business Category and Primary Keyword first.');
            return;
        }
        
        // Show loading state
        generateBtn.disabled = true;
        generateBtn.classList.add('loading');
        generateBtn.innerHTML = '<span class="ai-icon">🤖</span> Generating...';
        
        try {
            const response = await fetch('/generate_services', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    businessCategory: businessCategory,
                    primaryKeyword: primaryKeyword,
                    quantity: quantity
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Append to existing services or replace if empty
                const currentServices = servicesTextarea.value.trim();
                if (currentServices) {
                    servicesTextarea.value = currentServices + ', ' + data.services;
                } else {
                    servicesTextarea.value = data.services;
                }
                
                // Show success feedback
                showNotification(`Generated ${quantity} services successfully!`, 'success');
            } else {
                showNotification('Error: ' + data.error, 'error');
            }
        } catch (error) {
            showNotification('Network error: ' + error.message, 'error');
        } finally {
            // Reset button state
            generateBtn.disabled = false;
            generateBtn.classList.remove('loading');
            generateBtn.innerHTML = '<span class="ai-icon">🤖</span> AI Generate';
        }
    }
    
    async function generateCities() {
        const generateBtn = document.getElementById('generateCitiesBtn');
        const citiesTextarea = document.getElementById('serviceAreas');
        const cityInput = document.getElementById('city');
        const stateInput = document.getElementById('state');
        const businessCategorySelect = document.getElementById('businessCategory');
        const customCategoryInput = document.getElementById('customCategory');
        const quantityInput = document.getElementById('citiesQuantity');
        
        // Get business category
        let businessCategory = businessCategorySelect.value;
        if (businessCategory === 'custom') {
            businessCategory = customCategoryInput.value.trim();
        }
        
        const city = cityInput.value.trim();
        const state = stateInput.value.trim();
        const quantity = parseInt(quantityInput.value) || 10;
        
        // Validation
        if (!city || !state) {
            alert('Please fill in City and State first.');
            return;
        }
        
        // Show loading state
        generateBtn.disabled = true;
        generateBtn.classList.add('loading');
        generateBtn.innerHTML = '<span class="ai-icon">🤖</span> Generating...';
        
        try {
            const response = await fetch('/generate_cities', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    city: city,
                    state: state,
                    businessCategory: businessCategory,
                    quantity: quantity
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Append to existing cities or replace if empty
                const currentCities = citiesTextarea.value.trim();
                if (currentCities) {
                    citiesTextarea.value = currentCities + ', ' + data.cities;
                } else {
                    citiesTextarea.value = data.cities;
                }
                
                // Show success feedback
                showNotification(`Generated ${quantity} service areas successfully!`, 'success');
            } else {
                showNotification('Error: ' + data.error, 'error');
            }
        } catch (error) {
            showNotification('Network error: ' + error.message, 'error');
        } finally {
            // Reset button state
            generateBtn.disabled = false;
            generateBtn.classList.remove('loading');
            generateBtn.innerHTML = '<span class="ai-icon">🤖</span> AI Generate';
        }
    }
    
    // Notification system
    function showNotification(message, type = 'info') {
        // Remove existing notifications
        const existingNotifications = document.querySelectorAll('.notification');
        existingNotifications.forEach(notification => notification.remove());
        
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add styles
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-weight: 500;
            z-index: 10000;
            max-width: 400px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            animation: slideIn 0.3s ease-out;
        `;
        
        // Set background color based on type
        if (type === 'success') {
            notification.style.backgroundColor = '#28a745';
        } else if (type === 'error') {
            notification.style.backgroundColor = '#dc3545';
        } else {
            notification.style.backgroundColor = '#17a2b8';
        }
        
        // Add animation styles
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
        
        // Add to page
        document.body.appendChild(notification);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            notification.style.animation = 'slideIn 0.3s ease-out reverse';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.remove();
                }
            }, 300);
        }, 5000);
    }
});