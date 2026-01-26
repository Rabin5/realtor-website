// Function to generate professional agent modal content with sidebar layout
function generateAgentModalContent(agent) {
    // Generate star rating
    const starRating = generateStarRating(agent.rating);
    
    // Generate expertise items
    const expertiseItems = agent.expertise ? 
        agent.expertise.map((item, index) => {
            const icons = ['fa-home', 'fa-handshake', 'fa-users', 'fa-chart-line', 'fa-shield-alt'];
            return `
                <div class="agent-modal-expertise-item">
                    <div class="agent-modal-expertise-icon">
                        <i class="fas ${icons[index] || 'fa-check'}"></i>
                    </div>
                    <h4 class="agent-modal-expertise-title">${item}</h4>
                    <p class="agent-modal-expertise-desc">Specialized expertise in ${item.toLowerCase()} with proven results</p>
                </div>
            `;
        }).join('') : '';
    
    // Generate why choose items
    const whyChooseItems = agent.why_choose ? 
        agent.why_choose.map(item => `
            <div class="agent-modal-stat-card">
                <div class="agent-modal-stat-number">
                    <i class="fas fa-check-circle"></i>
                </div>
                <div class="agent-modal-stat-label">${item.title}</div>
                <p style="color: #6B7280; font-size: 0.95rem; margin-top: 10px;">${item.description}</p>
            </div>
        `).join('') : '';

    return `
        <!-- Header with Photo and Basic Info Sidebar -->
        <div class="agent-modal-header">
            <!-- Photo Section (Left) -->
            <div class="agent-modal-photo-section">
                <div class="agent-modal-photo-container">
                    <img src="${agent.photo}" alt="${agent.name}" class="agent-modal-photo">
                    <div class="agent-modal-photo-badge">SENIOR AGENT</div>
                </div>
            </div>
            
            <!-- Info Sidebar (Right) -->
            <div class="agent-modal-info-sidebar">
                <h1 class="agent-modal-name">${agent.name}</h1>
                <div class="agent-modal-title">${agent.title}</div>
                
                <!-- Rating Container -->
                <div class="agent-modal-rating-container">
                    <div class="agent-modal-rating-label">
                        <i class="fas fa-star"></i> Client Rating
                    </div>
                    <div class="agent-modal-rating">
                        <div class="agent-modal-rating-stars">
                            ${starRating}
                        </div>
                        <div class="agent-modal-rating-text">
                            ${agent.rating} Rating
                        </div>
                    </div>
                    <div class="agent-modal-rating-subtext">
                        ${agent.review_count} Client Reviews • 98% Satisfaction Rate
                    </div>
                </div>
                
                <!-- Contact Info -->
                <div class="agent-modal-contact-info">
                    <div class="agent-modal-contact-item">
                        <div class="agent-modal-contact-icon">
                            <i class="fas fa-phone-alt"></i>
                        </div>
                        <div class="agent-modal-contact-details">
                            <div class="agent-modal-contact-label">Direct Line</div>
                            <div class="agent-modal-contact-value">${agent.phone}</div>
                        </div>
                    </div>
                    
                    <div class="agent-modal-contact-item">
                        <div class="agent-modal-contact-icon">
                            <i class="fas fa-envelope"></i>
                        </div>
                        <div class="agent-modal-contact-details">
                            <div class="agent-modal-contact-label">Professional Email</div>
                            <div class="agent-modal-contact-value">${agent.email}</div>
                        </div>
                    </div>
                    
                    <div class="agent-modal-contact-item">
                        <div class="agent-modal-contact-icon">
                            <i class="fas fa-clock"></i>
                        </div>
                        <div class="agent-modal-contact-details">
                            <div class="agent-modal-contact-label">Response Time</div>
                            <div class="agent-modal-contact-value">Within 15 minutes</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Main Content -->
        <div class="agent-modal-body">
            <!-- About Section -->
            <div class="agent-modal-section">
                <h2 class="agent-modal-section-title">
                    <i class="fas fa-user-tie"></i>
                    About ${agent.first_name}
                </h2>
                <p class="agent-modal-description">
                    ${agent.description}
                </p>
            </div>
            
            <!-- Expertise Section -->
            <div class="agent-modal-section">
                <h2 class="agent-modal-section-title">
                    <i class="fas fa-award"></i>
                    Areas of Expertise
                </h2>
                <div class="agent-modal-expertise-grid">
                    ${expertiseItems}
                </div>
            </div>
            
            <!-- Performance Stats -->
            <div class="agent-modal-section">
                <h2 class="agent-modal-section-title">
                    <i class="fas fa-chart-line"></i>
                    Performance & Achievements
                </h2>
                <div class="agent-modal-stats-grid">
                    <div class="agent-modal-stat-card">
                        <div class="agent-modal-stat-number">
                            <i class="fas fa-home"></i> ${agent.properties_sold}
                        </div>
                        <div class="agent-modal-stat-label">Properties Sold</div>
                    </div>
                    
                    <div class="agent-modal-stat-card">
                        <div class="agent-modal-stat-number">
                            <i class="fas fa-heart"></i> ${agent.client_satisfaction}
                        </div>
                        <div class="agent-modal-stat-label">Client Satisfaction</div>
                    </div>
                    
                    <div class="agent-modal-stat-card">
                        <div class="agent-modal-stat-number">
                            <i class="fas fa-calendar-alt"></i> ${agent.years_experience}
                        </div>
                        <div class="agent-modal-stat-label">Years of Excellence</div>
                    </div>
                </div>
            </div>
            
            <!-- Why Choose Section -->
            ${whyChooseItems ? `
            <div class="agent-modal-section">
                <h2 class="agent-modal-section-title">
                    <i class="fas fa-check-circle"></i>
                    Why Choose ${agent.first_name}
                </h2>
                <div class="agent-modal-stats-grid">
                    ${whyChooseItems}
                </div>
            </div>
            ` : ''}
            
            <!-- CTA Section -->
            <div class="agent-modal-cta">
                <h3 class="agent-modal-cta-title">Ready to Achieve Your Real Estate Goals?</h3>
                <p class="agent-modal-cta-subtitle">
                    Whether you're buying, selling, or investing, ${agent.first_name} provides personalized guidance 
                    and expert negotiation to ensure you get the best possible outcome.
                </p>
                <div class="agent-modal-cta-buttons">
                    <a href="tel:${agent.phone}" class="agent-modal-cta-button agent-modal-cta-button-primary">
                        <i class="fas fa-phone-alt"></i> Schedule a Call
                    </a>
                    <a href="mailto:${agent.email}" class="agent-modal-cta-button agent-modal-cta-button-secondary">
                        <i class="fas fa-calendar-check"></i> Book Consultation
                    </a>
                </div>
            </div>
        </div>
    `;
}

// Star rating generator function (make sure this exists)
function generateStarRating(rating) {
    const fullStars = Math.floor(rating);
    const halfStar = rating - fullStars >= 0.5;
    const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);
    
    let stars = '';
    for (let i = 0; i < fullStars; i++) {
        stars += '<i class="fas fa-star"></i>';
    }
    if (halfStar) {
        stars += '<i class="fas fa-star-half-alt"></i>';
    }
    for (let i = 0; i < emptyStars; i++) {
        stars += '<i class="far fa-star"></i>';
    }
    return stars;
}