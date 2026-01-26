// static/js/reviews.js

class ReviewsManager {
    constructor() {
        this.reviewsGrid = document.querySelector('.reviews-grid');
        this.apiEndpoints = {
            list: '/api/reviews/list/',
            stats: '/api/reviews/stats/',
            helpful: '/api/reviews/helpful/',
            submit: '/api/reviews/submit/'
        };
        this.currentCategory = 'all';
        this.currentPage = 1;
        this.totalPages = 1;
        
        this.init();
    }
    
    init() {
        if (!this.reviewsGrid) return;
        
        this.createFilterButtons();
        this.loadReviews();
        this.setupEventListeners();
        this.loadReviewStats();
    }
    
    // Generate star rating HTML
    generateStarRating(rating) {
        let stars = '';
        for (let i = 1; i <= 5; i++) {
            if (i <= rating) {
                stars += '<i class="fas fa-star"></i>';
            } else {
                stars += '<i class="far fa-star"></i>';
            }
        }
        return stars;
    }
    
    // Format date
    formatDate(dateString) {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'long',
            year: 'numeric'
        });
    }
    
    // Get avatar URL with fallback
    getAvatarUrl(avatarUrl, name) {
        if (avatarUrl) return avatarUrl;
        
        // Generate random avatar based on name
        const names = name.split(' ');
        const firstName = names[0] || 'user';
        const gender = ['men', 'women'][Math.floor(Math.random() * 2)];
        const randomId = Math.floor(Math.random() * 99);
        return `https://randomuser.me/api/portraits/${gender}/${randomId}.jpg`;
    }
    
    // Create a review card HTML
    createReviewCard(review) {
        const avatarUrl = this.getAvatarUrl(review.avatar_url, review.name);
        
        return `
            <div class="review-card" data-review-id="${review.id}">
                <div class="review-header">
                    <div class="reviewer-avatar">
                        <img src="${avatarUrl}" alt="${review.name}" loading="lazy">
                    </div>
                    <div class="reviewer-info">
                        <h4 class="reviewer-name">${review.name}</h4>
                        <div class="reviewer-location">
                            <i class="fas fa-map-marker-alt"></i> ${review.location || 'Texas'}
                        </div>
                    </div>
                    <div class="review-rating">
                        ${review.stars_html || this.generateStarRating(review.rating)}
                    </div>
                </div>
                
                <div class="review-content">
                    <p>"${review.comment}"</p>
                </div>
                
                <div class="review-meta">
                    <span class="review-date">${review.date || this.formatDate(review.created_at)}</span>
                    ${review.category ? `<span class="review-category">• ${review.category}</span>` : ''}
                </div>
                
                ${review.property_related ? `
                <div class="review-property">
                    <small><i class="fas fa-home"></i> ${review.property_related}</small>
                </div>
                ` : ''}
                
                <div class="review-actions">
                    <button class="btn-helpful" data-review-id="${review.id}">
                        <i class="far fa-thumbs-up"></i>
                        Helpful (${review.helpful_count || 0})
                    </button>
                </div>
            </div>
        `;
    }
    
    // Load reviews from API
    async loadReviews() {
        try {
            this.showLoading();
            
            const params = new URLSearchParams({
                category: this.currentCategory,
                page: this.currentPage
            });
            
            const response = await fetch(`${this.apiEndpoints.list}?${params}`);
            const data = await response.json();
            
            this.renderReviews(data.reviews);
            this.updatePagination(data);
            
        } catch (error) {
            console.error('Error loading reviews:', error);
            this.showError('Failed to load reviews. Please try again.');
        }
    }
    
    // Render reviews to the grid
    renderReviews(reviews) {
        if (!reviews || reviews.length === 0) {
            this.reviewsGrid.innerHTML = `
                <div class="no-reviews">
                    <i class="fas fa-comment-slash"></i>
                    <p>No reviews found for this category.</p>
                </div>
            `;
            return;
        }
        
        this.reviewsGrid.innerHTML = reviews.map(review => 
            this.createReviewCard(review)
        ).join('');
        
        this.setupHelpfulButtons();
    }
    
    // Load review statistics
    async loadReviewStats() {
        try {
            const response = await fetch(this.apiEndpoints.stats);
            const stats = await response.json();
            
            this.updateReviewStats(stats);
            
        } catch (error) {
            console.error('Error loading review stats:', error);
        }
    }
    
    // Update review statistics display
    updateReviewStats(stats) {
        // Update total reviews
        const totalElement = document.querySelector('.total-reviews');
        if (totalElement && stats.total_reviews) {
            totalElement.textContent = `${stats.total_reviews}+`;
        }
        
        // Update average rating
        const ratingElement = document.querySelector('.avg-rating');
        if (ratingElement && stats.avg_rating) {
            ratingElement.textContent = `${stats.avg_rating.toFixed(1)}/5.0`;
        }
        
        // Update satisfaction rate
        const satisfactionElement = document.querySelector('.satisfaction-rate');
        if (satisfactionElement && stats.satisfaction_rate) {
            satisfactionElement.textContent = `${stats.satisfaction_rate}%`;
        }
        
        // Update featured count
        const featuredElement = document.querySelector('.featured-reviews');
        if (featuredElement && stats.featured_reviews) {
            featuredElement.textContent = `${stats.featured_reviews}`;
        }
    }
    
    // Create filter buttons
    createFilterButtons() {
        const categories = [
            { id: 'all', name: 'All Reviews' },
            { id: 'home_purchase', name: 'Home Purchase' },
            { id: 'first_time_buyer', name: 'First-Time Buyer' },
            { id: 'property_sale', name: 'Property Sale' },
            { id: 'va_loan', name: 'VA Loan' },
            { id: 'military', name: 'Military Relocation' },
            { id: 'investment', name: 'Investment' }
        ];
        
        const filterContainer = document.createElement('div');
        filterContainer.className = 'reviews-filter';
        filterContainer.innerHTML = `
            <div class="filter-buttons">
                ${categories.map(cat => `
                    <button class="filter-btn ${cat.id === 'all' ? 'active' : ''}" 
                            data-category="${cat.id}">
                        ${cat.name}
                    </button>
                `).join('')}
            </div>
        `;
        
        this.reviewsGrid.parentNode.insertBefore(filterContainer, this.reviewsGrid);
        
        // Add click handlers
        filterContainer.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const category = e.target.dataset.category;
                this.filterByCategory(category);
            });
        });
    }
    
    // Filter reviews by category
    filterByCategory(category) {
        this.currentCategory = category;
        this.currentPage = 1;
        
        // Update active button
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.category === category) {
                btn.classList.add('active');
            }
        });
        
        this.loadReviews();
    }
    
    // Update pagination
    updatePagination(data) {
        this.totalPages = data.total_pages || 1;
        
        const paginationContainer = document.querySelector('.reviews-pagination');
        if (!paginationContainer) return;
        
        let paginationHTML = `
            <button class="pagination-btn ${!data.has_previous ? 'disabled' : ''}" 
                    data-page="${data.current_page - 1}">
                <i class="fas fa-chevron-left"></i> Previous
            </button>
            
            <div class="page-numbers">
        `;
        
        for (let i = 1; i <= this.totalPages; i++) {
            paginationHTML += `
                <button class="page-number ${i === data.current_page ? 'active' : ''}" 
                        data-page="${i}">
                    ${i}
                </button>
            `;
        }
        
        paginationHTML += `
            </div>
            
            <button class="pagination-btn ${!data.has_next ? 'disabled' : ''}" 
                    data-page="${data.current_page + 1}">
                Next <i class="fas fa-chevron-right"></i>
            </button>
        `;
        
        paginationContainer.innerHTML = paginationHTML;
        
        // Add click handlers
        paginationContainer.querySelectorAll('.pagination-btn, .page-number').forEach(btn => {
            if (!btn.classList.contains('disabled')) {
                btn.addEventListener('click', (e) => {
                    const page = parseInt(e.target.dataset.page);
                    if (page && page !== this.currentPage) {
                        this.currentPage = page;
                        this.loadReviews();
                        window.scrollTo({
                            top: this.reviewsGrid.offsetTop - 100,
                            behavior: 'smooth'
                        });
                    }
                });
            }
        });
    }
    
    // Setup helpful buttons
    setupHelpfulButtons() {
        document.querySelectorAll('.btn-helpful').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const reviewId = e.target.closest('.btn-helpful').dataset.reviewId;
                await this.markHelpful(reviewId, e.target.closest('.btn-helpful'));
            });
        });
    }
    
    // Mark review as helpful
    async markHelpful(reviewId, button) {
        try {
            const response = await fetch(this.apiEndpoints.helpful, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken(),
                },
                body: JSON.stringify({ review_id: reviewId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Update button text
                button.innerHTML = `
                    <i class="fas fa-thumbs-up"></i>
                    Helpful (${data.helpful_count})
                `;
                button.classList.add('active');
                
                // Show success message
                this.showToast('Thank you for your feedback!', 'success');
            } else {
                this.showToast(data.message || 'You have already marked this as helpful', 'info');
            }
            
        } catch (error) {
            console.error('Error marking helpful:', error);
            this.showToast('Failed to update. Please try again.', 'error');
        }
    }
    
    // Setup event listeners
    setupEventListeners() {
        // Create pagination container if it doesn't exist
        if (!document.querySelector('.reviews-pagination')) {
            const paginationDiv = document.createElement('div');
            paginationDiv.className = 'reviews-pagination';
            this.reviewsGrid.parentNode.appendChild(paginationDiv);
        }
        
        // Submit review form handler
        const reviewForm = document.getElementById('review-form');
        if (reviewForm) {
            reviewForm.addEventListener('submit', (e) => this.submitReview(e));
        }
    }
    
    // Submit review form
    async submitReview(event) {
        event.preventDefault();
        
        const form = event.target;
        const formData = new FormData(form);
        
        try {
            const response = await fetch(this.apiEndpoints.submit, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showToast('Thank you for your review! It has been submitted.', 'success');
                form.reset();
                
                // Refresh reviews
                this.loadReviews();
                this.loadReviewStats();
            } else {
                // Display errors
                this.showFormErrors(form, data.errors);
            }
            
        } catch (error) {
            console.error('Error submitting review:', error);
            this.showToast('Failed to submit review. Please try again.', 'error');
        }
    }
    
    // Show form errors
    showFormErrors(form, errors) {
        // Clear previous errors
        form.querySelectorAll('.error-message').forEach(el => el.remove());
        form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        
        // Add new errors
        Object.keys(errors).forEach(field => {
            const input = form.querySelector(`[name="${field}"]`);
            if (input) {
                input.classList.add('is-invalid');
                const errorDiv = document.createElement('div');
                errorDiv.className = 'error-message';
                errorDiv.textContent = errors[field][0].message;
                input.parentNode.appendChild(errorDiv);
            }
        });
    }
    
    // Show loading state
    showLoading() {
        this.reviewsGrid.innerHTML = `
            <div class="loading-reviews">
                <div class="spinner"></div>
                <p>Loading reviews...</p>
            </div>
        `;
    }
    
    // Show error message
    showError(message) {
        this.reviewsGrid.innerHTML = `
            <div class="error-reviews">
                <i class="fas fa-exclamation-circle"></i>
                <p>${message}</p>
                <button class="retry-btn">Retry</button>
            </div>
        `;
        
        this.reviewsGrid.querySelector('.retry-btn').addEventListener('click', () => {
            this.loadReviews();
        });
    }
    
    // Show toast notification
    showToast(message, type = 'info') {
        // Create toast container if it doesn't exist
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : 
                                  type === 'error' ? 'exclamation-circle' : 
                                  'info-circle'}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close">&times;</button>
        `;
        
        toastContainer.appendChild(toast);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 300);
        }, 5000);
        
        // Close button
        toast.querySelector('.toast-close').addEventListener('click', () => {
            toast.classList.add('hide');
            setTimeout(() => toast.remove(), 300);
        });
    }
    
    // Get CSRF token
    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.cookie.match(/csrftoken=([^;]+)/)?.[1];
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ReviewsManager();
});