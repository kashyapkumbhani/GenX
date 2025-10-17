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
                        alert('Site generated successfully!');
                        window.location.href = data.preview_url;
                    } else {
                        alert('Error generating site: ' + data.message);
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
});