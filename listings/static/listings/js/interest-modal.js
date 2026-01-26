// interest-modal.js - Seller/Buyer interest modal functionality

document.addEventListener('DOMContentLoaded', function() {
    const interestModal = document.getElementById('interestModal');
    const interestModalContent = document.getElementById('interestModalContent');
    const interestTriggers = document.querySelectorAll('.open-interest-modal');
    const closeInterestModal = document.querySelector('.close-interest-modal');
    
    if (!interestModal) return;
    
    // Interest form templates
    const interestTemplates = {
        seller: {
            title: 'Ready to Sell Your Property?',
            description: 'Get expert guidance to maximize your home\'s value and achieve a fast, profitable sale.',
            questions: [
                {
                    id: 'property_type',
                    question: 'What type of property are you selling?',
                    options: [
                        { value: 'single_family', label: 'Single Family Home' },
                        { value: 'condo', label: 'Condominium' },
                        { value: 'townhouse', label: 'Townhouse' },
                        { value: 'multi_family', label: 'Multi-Family' },
                        { value: 'land', label: 'Vacant Land' },
                        { value: 'commercial', label: 'Commercial' }
                    ]
                },
                {
                    id: 'timeline',
                    question: 'When are you planning to sell?',
                    options: [
                        { value: 'immediately', label: 'Immediately (within 30 days)' },
                        { value: '1-3_months', label: 'Within 1-3 months' },
                        { value: '3-6_months', label: 'Within 3-6 months' },
                        { value: 'just_exploring', label: 'Just exploring options' }
                    ]
                },
                {
                    id: 'property_value',
                    question: 'Estimated value of your property?',
                    options: [
                        { value: 'under_200k', label: 'Under $200,000' },
                        { value: '200k_300k', label: '$200,000 - $300,000' },
                        { value: '300k_400k', label: '$300,000 - $400,000' },
                        { value: '400k_500k', label: '$400,000 - $500,000' },
                        { value: '500k_plus', label: '$500,000+' }
                    ]
                },
                {
                    id: 'reason',
                    question: 'Primary reason for selling?',
                    options: [
                        { value: 'relocation', label: 'Relocation' },
                        { value: 'upsizing', label: 'Moving to larger home' },
                        { value: 'downsizing', label: 'Downsizing' },
                        { value: 'investment', label: 'Investment property sale' },
                        { value: 'estate', label: 'Estate sale' },
                        { value: 'other', label: 'Other' }
                    ]
                }
            ]
        },
        buyer: {
            title: 'Ready to Find Your Dream Home?',
            description: 'Let me help you navigate the buying process and find the perfect property for your needs.',
            questions: [
                {
                    id: 'timeline',
                    question: 'When are you planning to buy?',
                    options: [
                        { value: 'immediately', label: 'Immediately (within 30 days)' },
                        { value: '1-3_months', label: 'Within 1-3 months' },
                        { value: '3-6_months', label: 'Within 3-6 months' },
                        { value: 'just_browsing', label: 'Just browsing/exploring' }
                    ]
                },
                {
                    id: 'property_type',
                    question: 'What type of property are you looking for?',
                    options: [
                        { value: 'single_family', label: 'Single Family Home' },
                        { value: 'condo', label: 'Condominium' },
                        { value: 'townhouse', label: 'Townhouse' },
                        { value: 'multi_family', label: 'Multi-Family' },
                        { value: 'land', label: 'Vacant Land' },
                        { value: 'commercial', label: 'Commercial' }
                    ]
                },
                {
                    id: 'budget',
                    question: 'What\'s your budget range?',
                    options: [
                        { value: 'under_200k', label: 'Under $200,000' },
                        { value: '200k_300k', label: '$200,000 - $300,000' },
                        { value: '300k_400k', label: '$300,000 - $400,000' },
                        { value: '400k_500k', label: '$400,000 - $500,000' },
                        { value: '500k_plus', label: '$500,000+' }
                    ]
                },
                {
                    id: 'property_status',
                    question: 'Preferred property status?',
                    options: [
                        { value: 'any', label: 'Any' },
                        { value: 'new_construction', label: 'New Construction' },
                        { value: 'recently_updated', label: 'Recently Updated/Renovated' },
                        { value: 'fixer_upper', label: 'Fixer Upper' }
                    ]
                }
            ]
        }
    };
    
    // Open interest modal
    function openInterestModal(interestType) {
        const template = interestTemplates[interestType];
        if (!template) return;
        
        const formHtml = generateInterestForm(interestType, template);
        interestModalContent.innerHTML = formHtml;
        interestModal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // Setup radio button styling
        setupRadioButtons();
        
        // Add form submission handler
        const form = document.getElementById('interestForm');
        if (form) {
            form.addEventListener('submit', handleInterestSubmit);
        }
    }
    
    // Generate interest form HTML
    function generateInterestForm(interestType, template) {
        let questionsHtml = '';
        
        template.questions.forEach(q => {
            questionsHtml += `
                <div class="question-group" style="margin-bottom: 25px;">
                    <label style="display: block; margin-bottom: 10px; color: #374151; font-weight: 600; font-size: 1.1rem;">
                        ${q.question}
                    </label>
                    <div class="options-group" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 10px;">
            `;
            
            q.options.forEach((option, index) => {
                questionsHtml += `
                    <label style="display: flex; align-items: center; padding: 12px; border: 2px solid #E5E7EB; 
                           border-radius: 8px; cursor: pointer; transition: all 0.3s;">
                        <input type="radio" name="${q.id}" value="${option.value}" 
                               ${index === 0 ? 'checked' : ''}
                               style="margin-right: 10px;">
                        ${option.label}
                    </label>
                `;
            });
            
            questionsHtml += `
                    </div>
                </div>
            `;
        });
        
        return `
            <div class="interest-modal-content">
                <h2 style="font-size: 2.2rem; color: #1E3A8A; margin-bottom: 10px; text-align: center;">
                    ${template.title}
                </h2>
                <p style="text-align: center; color: #6B7280; margin-bottom: 30px; font-size: 1.1rem;">
                    ${template.description}
                </p>
                
                <form id="interestForm" data-interest-type="${interestType}">
                    ${questionsHtml}
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 30px;">
                        <div>
                            <label style="display: block; margin-bottom: 8px; color: #374151; font-weight: 600;">
                                Your Name *
                            </label>
                            <input type="text" name="name" required 
                                   style="width: 100%; padding: 12px; border: 2px solid #E5E7EB; border-radius: 8px;">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 8px; color: #374151; font-weight: 600;">
                                Phone Number *
                            </label>
                            <input type="tel" name="phone" required 
                                   style="width: 100%; padding: 12px; border: 2px solid #E5E7EB; border-radius: 8px;">
                        </div>
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <label style="display: block; margin-bottom: 8px; color: #374151; font-weight: 600;">
                            Email Address *
                        </label>
                        <input type="email" name="email" required 
                               style="width: 100%; padding: 12px; border: 2px solid #E5E7EB; border-radius: 8px;">
                    </div>
                    
                    <div style="margin-top: 20px;">
                        <label style="display: block; margin-bottom: 8px; color: #374151; font-weight: 600;">
                            Additional Notes (Optional)
                        </label>
                        <textarea name="notes" rows="3" 
                                  style="width: 100%; padding: 12px; border: 2px solid #E5E7EB; border-radius: 8px;"></textarea>
                    </div>
                    
                    <div style="margin-top: 30px; text-align: center;">
                        <button type="submit" 
                                style="background: #F97316; color: white; border: none; padding: 15px 40px; 
                                       border-radius: 8px; font-size: 1.1rem; cursor: pointer; font-weight: 600;">
                            <i class="fas fa-paper-plane"></i> Submit Information
                        </button>
                    </div>
                    
                    <div id="interestFormMessage" style="margin-top: 20px; text-align: center;"></div>
                </form>
            </div>
        `;
    }
    
    // Setup radio button styling
    function setupRadioButtons() {
        const radioLabels = document.querySelectorAll('.options-group label');
        
        radioLabels.forEach(label => {
            const radio = label.querySelector('input[type="radio"]');
            
            // Update label styling based on radio state
            function updateLabelStyle() {
                const groupName = radio.name;
                document.querySelectorAll(`input[name="${groupName}"]`).forEach(r => {
                    r.parentElement.style.borderColor = '#E5E7EB';
                    r.parentElement.style.background = 'white';
                });
                
                if (radio.checked) {
                    label.style.borderColor = '#1E3A8A';
                    label.style.background = 'rgba(30, 58, 138, 0.05)';
                }
            }
            
            // Initialize style
            updateLabelStyle();
            
            // Update on change
            radio.addEventListener('change', updateLabelStyle);
            
            // Click on label to select radio
            label.addEventListener('click', function() {
                radio.checked = true;
                updateLabelStyle();
            });
        });
    }
    
    // Handle form submission
    async function handleInterestSubmit(e) {
        e.preventDefault();
        
        const form = e.target;
        const formData = new FormData(form);
        const interestType = form.getAttribute('data-interest-type');
        const messageDiv = document.getElementById('interestFormMessage');
        
        // Prepare data
        const data = {
            interest_type: interestType,
            name: formData.get('name'),
            email: formData.get('email'),
            phone: formData.get('phone'),
            notes: formData.get('notes') || ''
        };
        
        // Add question answers
        const questions = form.querySelectorAll('.question-group');
        questions.forEach(q => {
            const radio = q.querySelector('input[type="radio"]:checked');
            if (radio) {
                data[radio.name] = radio.value;
            }
        });
        
        // Show loading
        messageDiv.innerHTML = '<p style="color: #1E3A8A;"><i class="fas fa-spinner fa-spin"></i> Submitting your information...</p>';
        
        try {
            // Use Django's AJAX endpoint if available
            let response;
            if (window.DJANGO_DATA && window.DJANGO_DATA.saveInterestUrl) {
                response = await fetch(window.DJANGO_DATA.saveInterestUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': window.utils.getCSRFToken()
                    },
                    body: JSON.stringify(data)
                });
            } else {
                // Fallback to form action
                response = await fetch(form.action || window.location.href, {
                    method: 'POST',
                    body: JSON.stringify(data)
                });
            }
            
            const result = await response.json();
            
            if (result.success) {
                messageDiv.innerHTML = '<p style="color: #10B981;"><i class="fas fa-check-circle"></i> Thank you! Your information has been submitted successfully. We\'ll contact you shortly.</p>';
                
                // Reset and close after delay
                setTimeout(() => {
                    closeInterestModalFunc();
                    form.reset();
                }, 3000);
            } else {
                messageDiv.innerHTML = `<p style="color: #EF4444;"><i class="fas fa-exclamation-circle"></i> ${result.message || 'There was an error submitting your information.'}</p>`;
            }
        } catch (error) {
            console.error('Error:', error);
            messageDiv.innerHTML = '<p style="color: #EF4444;"><i class="fas fa-exclamation-circle"></i> Network error. Please try again.</p>';
        }
    }
    
    // Close interest modal
    function closeInterestModalFunc() {
        interestModal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
    
    // Event listeners
    if (interestTriggers.length > 0) {
        interestTriggers.forEach(trigger => {
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                const interestType = this.getAttribute('data-interest-type');
                openInterestModal(interestType);
            });
        });
    }
    
    if (closeInterestModal) {
        closeInterestModal.addEventListener('click', closeInterestModalFunc);
    }
    
    interestModal.addEventListener('click', function(e) {
        if (e.target === interestModal) {
            closeInterestModalFunc();
        }
    });
});