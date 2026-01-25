/**
 * Main JavaScript
 * Core functionality for the application
 */

// Global state
let currentCity = null;
let currentUser = null;

// API Base URL
const API_BASE = '/api';

// ===================================
// Utility Functions
// ===================================

// Show loading overlay
function showLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.add('active');
    }
}

// Hide loading overlay
function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.classList.remove('active');
    }
}

// Show toast notification
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        </div>
    `;

    container.appendChild(toast);

    // Auto remove after 5 seconds
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// ===================================
// Authentication
// ===================================

// Check authentication status
async function checkAuth() {
    try {
        const response = await fetch(`${API_BASE}/auth/check`);
        const data = await response.json();

        if (data.authenticated) {
            currentUser = data.user;
            updateAuthUI(true);
        } else {
            updateAuthUI(false);
        }

        return data.authenticated;
    } catch (error) {
        console.error('Auth check failed:', error);
        return false;
    }
}

// Update authentication UI
function updateAuthUI(isAuthenticated) {
    const authButtons = document.getElementById('auth-buttons');
    const userMenu = document.getElementById('user-menu');

    if (isAuthenticated) {
        if (authButtons) authButtons.style.display = 'none';
        if (userMenu) userMenu.style.display = 'block';
    } else {
        if (authButtons) authButtons.style.display = 'flex';
        if (userMenu) userMenu.style.display = 'none';
    }
}

// Logout
async function logout() {
    try {
        const response = await fetch(`${API_BASE}/auth/logout`, {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showToast('Logged out successfully', 'success');
            currentUser = null;
            updateAuthUI(false);

            // Redirect to home if on dashboard
            if (window.location.pathname === '/dashboard') {
                window.location.href = '/';
            }
        }
    } catch (error) {
        console.error('Logout failed:', error);
        showToast('Logout failed', 'error');
    }
}

// ===================================
// City Search
// ===================================

let searchTimeout = null;

// Initialize city search
function initCitySearch() {
    const searchInput = document.getElementById('city-search');
    const searchBtn = document.getElementById('search-btn');
    const suggestions = document.getElementById('search-suggestions');

    if (!searchInput) return;

    // Input event for auto-suggest
    searchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();

        clearTimeout(searchTimeout);

        if (query.length < 2) {
            if (suggestions) suggestions.classList.remove('active');
            return;
        }

        searchTimeout = setTimeout(() => {
            searchCities(query);
        }, 300);
    });

    // Search button click
    if (searchBtn) {
        searchBtn.addEventListener('click', () => {
            const query = searchInput.value.trim();
            if (query) {
                loadWeatherData(query);
                if (suggestions) suggestions.classList.remove('active');
            }
        });
    }

    // Enter key
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                loadWeatherData(query);
                if (suggestions) suggestions.classList.remove('active');
            }
        }
    });

    // Click outside to close suggestions
    document.addEventListener('click', (e) => {
        if (suggestions && !searchInput.contains(e.target) && !suggestions.contains(e.target)) {
            suggestions.classList.remove('active');
        }
    });
}

// Search for cities
async function searchCities(query) {
    const suggestions = document.getElementById('search-suggestions');
    if (!suggestions) return;

    try {
        const response = await fetch(`${API_BASE}/weather/search/${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.success && data.data.length > 0) {
            displaySuggestions(data.data);
        } else {
            // Show "no results" message
            suggestions.innerHTML = `
                <div class="suggestion-item" style="text-align: center; color: var(--text-secondary);">
                    <em>No cities found for "${query}"</em>
                </div>
            `;
            suggestions.classList.add('active');
        }
    } catch (error) {
        console.error('City search failed:', error);
        suggestions.classList.remove('active');
    }
}

// Display search suggestions with enhanced formatting
function displaySuggestions(cities) {
    const suggestions = document.getElementById('search-suggestions');
    if (!suggestions) return;

    suggestions.innerHTML = '';

    cities.forEach((city, index) => {
        const item = document.createElement('div');
        item.className = 'suggestion-item';
        item.setAttribute('data-index', index);

        // Format city display with icon and better styling
        const cityName = city.name;
        const location = city.state
            ? `${city.state}, ${city.country}`
            : city.country;

        item.innerHTML = `
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <i class="fas fa-map-marker-alt" style="color: var(--primary-color); font-size: 1.1rem;"></i>
                <div style="flex: 1;">
                    <div style="font-weight: 600; color: var(--text-primary);">${cityName}</div>
                    <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.125rem;">${location}</div>
                </div>
            </div>
        `;

        item.addEventListener('click', () => {
            const searchInput = document.getElementById('city-search');
            if (searchInput) {
                searchInput.value = city.name;
            }
            loadWeatherData(city.name);
            suggestions.classList.remove('active');
        });

        suggestions.appendChild(item);
    });

    suggestions.classList.add('active');
}

// ===================================
// Tab Navigation
// ===================================

function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.dataset.tab;

            // Update buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update content
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });

            const targetContent = document.getElementById(tabName);
            if (targetContent) {
                targetContent.classList.add('active');
            }
        });
    });
}

// ===================================
// User Menu Dropdown
// ===================================

function initUserMenu() {
    const userMenuBtn = document.getElementById('user-menu-btn');
    const userDropdown = document.getElementById('user-dropdown');
    const logoutBtn = document.getElementById('logout-btn');

    if (userMenuBtn && userDropdown) {
        userMenuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            userDropdown.classList.toggle('active');
        });

        document.addEventListener('click', () => {
            userDropdown.classList.remove('active');
        });
    }

    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            logout();
        });
    }
}

// ===================================
// Mobile Menu
// ===================================

function initMobileMenu() {
    const toggle = document.getElementById('mobile-menu-toggle');
    const menu = document.querySelector('.nav-menu');

    if (toggle && menu) {
        toggle.addEventListener('click', () => {
            menu.classList.toggle('active');
        });
    }
}

// ===================================
// URL Parameters
// ===================================

function getUrlParameter(name) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(name);
}

// ===================================
// Initialization
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    // Check authentication
    checkAuth();

    // Initialize components
    initCitySearch();
    initTabs();
    initUserMenu();
    initMobileMenu();

    // Check for city parameter in URL
    const cityParam = getUrlParameter('city');
    if (cityParam) {
        const searchInput = document.getElementById('city-search');
        if (searchInput) {
            searchInput.value = cityParam;
            loadWeatherData(cityParam);
        }
    }

    // Set current date
    const currentDateEl = document.getElementById('current-date');
    if (currentDateEl) {
        currentDateEl.textContent = formatDate(new Date());
    }
});
