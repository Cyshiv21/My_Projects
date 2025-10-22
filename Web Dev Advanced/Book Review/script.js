// API Base URL
const API_URL = 'http://localhost:8000/api';

// State management
let currentUser = null;
let allReviews = [];

// DOM Elements
const authSection = document.getElementById('authSection');
const mainSection = document.getElementById('mainSection');
const loginForm = document.getElementById('loginFormElement');
const registerForm = document.getElementById('registerFormElement');
const addReviewForm = document.getElementById('addReviewForm');
const reviewsList = document.getElementById('reviewsList');
const searchInput = document.getElementById('searchInput');
const filterRating = document.getElementById('filterRating');
const messageToast = document.getElementById('messageToast');

// Navigation elements
const loginLink = document.getElementById('loginLink');
const registerLink = document.getElementById('registerLink');
const logoutLink = document.getElementById('logoutLink');
const homeLink = document.getElementById('homeLink');
const myReviewsLink = document.getElementById('myReviewsLink');

// Check if user is logged in on page load
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('token');
    const user = localStorage.getItem('user');
    
    if (token && user) {
        currentUser = JSON.parse(user);
        showMainSection();
        loadReviews();
    }
});

// Show/Hide forms
document.getElementById('showRegister').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
});

document.getElementById('showLogin').addEventListener('click', (e) => {
    e.preventDefault();
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
});

// Navigation clicks
loginLink.addEventListener('click', (e) => {
    e.preventDefault();
    showAuthSection();
    document.getElementById('loginForm').style.display = 'block';
    document.getElementById('registerForm').style.display = 'none';
});

registerLink.addEventListener('click', (e) => {
    e.preventDefault();
    showAuthSection();
    document.getElementById('registerForm').style.display = 'block';
    document.getElementById('loginForm').style.display = 'none';
});

logoutLink.addEventListener('click', (e) => {
    e.preventDefault();
    logout();
});

homeLink.addEventListener('click', (e) => {
    e.preventDefault();
    if (currentUser) {
        loadReviews();
    }
});

myReviewsLink.addEventListener('click', (e) => {
    e.preventDefault();
    if (currentUser) {
        loadMyReviews();
    }
});

// Register
registerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/register/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Registration successful! Please login.');
            document.getElementById('showLogin').click();
            registerForm.reset();
        } else {
            showMessage(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server', 'error');
    }
});

// Login
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_URL}/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            currentUser = data.user;
            showMessage('Login successful!');
            showMainSection();
            loadReviews();
            loginForm.reset();
        } else {
            showMessage(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server', 'error');
    }
});

// Add Review
addReviewForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const title = document.getElementById('bookTitle').value;
    const author = document.getElementById('bookAuthor').value;
    const rating = document.getElementById('bookRating').value;
    const review = document.getElementById('bookReview').value;
    
    try {
        const response = await fetch(`${API_URL}/reviews/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
            body: JSON.stringify({ title, author, rating: parseInt(rating), review_text: review }),
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('Review added successfully!');
            addReviewForm.reset();
            loadReviews();
        } else {
            showMessage(data.error || 'Failed to add review', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server', 'error');
    }
});

// Load all reviews
async function loadReviews() {
    try {
        const response = await fetch(`${API_URL}/reviews/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
        });
        
        const data = await response.json();
        
        if (response.ok) {
            allReviews = data;
            displayReviews(allReviews);
        }
    } catch (error) {
        showMessage('Error loading reviews', 'error');
    }
}

// Load user's reviews
async function loadMyReviews() {
    try {
        const response = await fetch(`${API_URL}/reviews/user/${currentUser.id}/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayReviews(data);
        }
    } catch (error) {
        showMessage('Error loading your reviews', 'error');
    }
}

// Display reviews
function displayReviews(reviews) {
    reviewsList.innerHTML = '';
    
    if (reviews.length === 0) {
        reviewsList.innerHTML = '<p style="text-align: center; color: #888;">No reviews found.</p>';
        return;
    }
    
    reviews.forEach(review => {
        const card = document.createElement('div');
        card.className = 'review-card';
        
        const stars = '⭐'.repeat(review.rating);
        const isOwner = currentUser && review.user_id === currentUser.id;
        
        card.innerHTML = `
            <div class="review-header">
                <div>
                    <div class="review-title">${review.title}</div>
                    <div class="review-author">by ${review.author}</div>
                </div>
                <div class="review-rating">${stars}</div>
            </div>
            <div class="review-meta">
                <span>Reviewed by: ${review.username}</span>
                <span>${new Date(review.created_at).toLocaleDateString()}</span>
            </div>
            <div class="review-text">${review.review_text}</div>
            ${isOwner ? `
                <div class="review-actions">
                    <button class="edit-btn" onclick="editReview(${review.id})">Edit</button>
                    <button class="delete-btn" onclick="deleteReview(${review.id})">Delete</button>
                </div>
            ` : ''}
        `;
        
        reviewsList.appendChild(card);
    });
}

// Delete review
async function deleteReview(id) {
    if (!confirm('Are you sure you want to delete this review?')) return;
    
    try {
        const response = await fetch(`${API_URL}/reviews/${id}/`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
        });
        
        if (response.ok) {
            showMessage('Review deleted successfully!');
            loadReviews();
        } else {
            showMessage('Failed to delete review', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server', 'error');
    }
}

// Edit review (simplified - shows prompt)
async function editReview(id) {
    const review = allReviews.find(r => r.id === id);
    if (!review) return;
    
    const newReviewText = prompt('Edit your review:', review.review_text);
    if (!newReviewText) return;
    
    try {
        const response = await fetch(`${API_URL}/reviews/${id}/`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
            body: JSON.stringify({ review_text: newReviewText }),
        });
        
        if (response.ok) {
            showMessage('Review updated successfully!');
            loadReviews();
        } else {
            showMessage('Failed to update review', 'error');
        }
    } catch (error) {
        showMessage('Error connecting to server', 'error');
    }
}

// Search functionality
searchInput.addEventListener('input', filterReviews);
filterRating.addEventListener('change', filterReviews);

function filterReviews() {
    const searchTerm = searchInput.value.toLowerCase();
    const ratingFilter = filterRating.value;
    
    let filtered = allReviews.filter(review => {
        const matchesSearch = review.title.toLowerCase().includes(searchTerm) || 
                            review.author.toLowerCase().includes(searchTerm);
        const matchesRating = !ratingFilter || review.rating === parseInt(ratingFilter);
        
        return matchesSearch && matchesRating;
    });
    
    displayReviews(filtered);
}

// UI Helper functions
function showAuthSection() {
    authSection.style.display = 'flex';
    mainSection.style.display = 'none';
    loginLink.style.display = 'inline';
    registerLink.style.display = 'inline';
    logoutLink.style.display = 'none';
    homeLink.style.display = 'none';
    myReviewsLink.style.display = 'none';
}

function showMainSection() {
    authSection.style.display = 'none';
    mainSection.style.display = 'block';
    loginLink.style.display = 'none';
    registerLink.style.display = 'none';
    logoutLink.style.display = 'inline';
    homeLink.style.display = 'inline';
    myReviewsLink.style.display = 'inline';
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    currentUser = null;
    allReviews = [];
    showAuthSection();
    showMessage('Logged out successfully!');
}

function showMessage(message, type = 'success') {
    messageToast.textContent = message;
    messageToast.className = `message-toast show ${type}`;
    
    setTimeout(() => {
        messageToast.className = 'message-toast';
    }, 3000);
}