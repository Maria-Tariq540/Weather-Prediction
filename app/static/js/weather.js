/**
 * Weather Display
 * Handles fetching and displaying weather data
 */

// ===================================
// Load Weather Data
// ===================================

async function loadWeatherData(city) {
    currentCity = city;
    showLoading();

    try {
        // Fetch complete weather data
        const response = await fetch(`${API_BASE}/weather/complete/${encodeURIComponent(city)}`);
        const data = await response.json();

        hideLoading();

        if (data.success) {
            displayCurrentWeather(data.current);
            displayForecast(data.forecast);
            displayAQI(data.aqi);
            displayAlerts(data.alerts);
            displayRecommendations(data.recommendations);

            // Show weather section
            const weatherSection = document.getElementById('weather-display');
            if (weatherSection) {
                weatherSection.style.display = 'block';
                weatherSection.scrollIntoView({ behavior: 'smooth' });
            }

            // Initialize charts
            if (data.forecast) {
                initializeCharts(data.forecast.forecast);
            }

            // Initialize map
            initializeMap(data.current.latitude, data.current.longitude, city);
        } else {
            showToast(data.error || 'Failed to load weather data', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('Error loading weather:', error);
        showToast('Failed to load weather data', 'error');
    }
}

// ===================================
// Display Current Weather
// ===================================

function displayCurrentWeather(data) {
    // City name
    const cityEl = document.getElementById('current-city');
    if (cityEl) {
        cityEl.textContent = `${data.city}, ${data.country}`;
    }

    // Weather icon (using Font Awesome as placeholder)
    const iconEl = document.getElementById('weather-icon');
    if (iconEl) {
        iconEl.src = `https://openweathermap.org/img/wn/${data.weather.icon.replace('.svg', '.png')}@4x.png`;
        iconEl.alt = data.weather.description;
    }

    // Temperature
    const tempEl = document.getElementById('current-temp');
    if (tempEl) {
        tempEl.textContent = data.temperature;
    }

    // Description
    const descEl = document.getElementById('weather-desc');
    if (descEl) {
        descEl.textContent = data.weather.description;
    }

    // Feels like
    const feelsLikeEl = document.getElementById('feels-like');
    if (feelsLikeEl) {
        feelsLikeEl.textContent = data.feels_like;
    }

    // Details
    document.getElementById('humidity').textContent = `${data.humidity}%`;
    document.getElementById('wind-speed').textContent = `${data.wind_speed} m/s`;
    document.getElementById('visibility').textContent = `${data.visibility} km`;
    document.getElementById('pressure').textContent = `${data.pressure} hPa`;

    // Update favorite button
    updateFavoriteButton();
}

// ===================================
// Display Forecast
// ===================================

function displayForecast(forecastData) {
    if (!forecastData || !forecastData.forecast) return;

    const grid = document.getElementById('forecast-grid');
    if (!grid) return;

    grid.innerHTML = '';

    forecastData.forecast.forEach(day => {
        const card = document.createElement('div');
        card.className = 'forecast-card';
        card.innerHTML = `
            <div class="forecast-day">${day.day_name}</div>
            <div class="forecast-icon">
                <img src="https://openweathermap.org/img/wn/${day.weather.icon.replace('.svg', '.png')}@2x.png" 
                     alt="${day.weather.description}" 
                     style="width: 60px; height: 60px;">
            </div>
            <div class="forecast-temp">${day.temp_avg}°C</div>
            <div class="forecast-details">
                <div>${day.temp_min}° / ${day.temp_max}°</div>
                <div><i class="fas fa-tint"></i> ${day.humidity}%</div>
                ${day.rainfall > 0 ? `<div><i class="fas fa-cloud-rain"></i> ${day.rainfall}mm</div>` : ''}
            </div>
        `;
        grid.appendChild(card);
    });
}

// ===================================
// Display AQI
// ===================================

function displayAQI(aqiData) {
    if (!aqiData) return;

    const valueEl = document.getElementById('aqi-value');
    const categoryEl = document.getElementById('aqi-category');
    const indicatorEl = document.getElementById('aqi-indicator');

    if (valueEl) valueEl.textContent = aqiData.aqi;
    if (categoryEl) {
        categoryEl.textContent = aqiData.category;
        categoryEl.style.color = aqiData.color;
    }

    // Position indicator (AQI ranges from 1-5)
    if (indicatorEl) {
        const position = ((aqiData.aqi - 1) / 4) * 100;
        indicatorEl.style.left = `${position}%`;
        indicatorEl.style.borderColor = aqiData.color;
    }
}

// ===================================
// Display Alerts
// ===================================

function displayAlerts(alerts) {
    const section = document.getElementById('alerts-section');
    const container = document.getElementById('alerts-container');

    if (!alerts || alerts.length === 0) {
        if (section) section.style.display = 'none';
        return;
    }

    if (section) section.style.display = 'block';
    if (!container) return;

    container.innerHTML = '';

    alerts.forEach(alert => {
        const card = document.createElement('div');
        card.className = `alert-card ${alert.severity}`;
        card.innerHTML = `
            <div style="display: flex; align-items: flex-start; gap: 1rem;">
                <div style="font-size: 1.5rem;">${alert.icon}</div>
                <div style="flex: 1;">
                    <h4 style="margin-bottom: 0.5rem;">${alert.title}</h4>
                    <p style="margin: 0;">${alert.message}</p>
                </div>
            </div>
        `;
        container.appendChild(card);
    });
}

// ===================================
// Display Recommendations
// ===================================

function displayRecommendations(recommendations) {
    if (!recommendations) return;

    const grid = document.getElementById('recommendations-grid');
    if (!grid) return;

    grid.innerHTML = '';

    const categories = [
        { key: 'clothing', icon: 'tshirt', title: 'Clothing' },
        { key: 'activities', icon: 'running', title: 'Activities' },
        { key: 'health', icon: 'heartbeat', title: 'Health' }
    ];

    categories.forEach(cat => {
        if (recommendations[cat.key] && recommendations[cat.key].length > 0) {
            const section = document.createElement('div');
            section.innerHTML = `
                <h4><i class="fas fa-${cat.icon}"></i> ${cat.title}</h4>
                <ul style="list-style: none; padding: 0; margin-top: 0.5rem;">
                    ${recommendations[cat.key].map(rec => `<li style="margin-bottom: 0.5rem;"><i class="fas fa-check" style="color: var(--primary-color); margin-right: 0.5rem;"></i>${rec}</li>`).join('')}
                </ul>
            `;
            grid.appendChild(section);
        }
    });
}

// ===================================
// ML Prediction
// ===================================

async function loadMLPrediction() {
    if (!currentCity) {
        showToast('Please search for a city first', 'info');
        return;
    }

    const modelSelect = document.getElementById('model-select');
    const model = modelSelect ? modelSelect.value : 'random_forest';

    showLoading();

    try {
        const response = await fetch(`${API_BASE}/predict/${encodeURIComponent(currentCity)}?model=${model}&days=7`);
        const data = await response.json();

        hideLoading();

        if (data.success) {
            displayMLForecast(data.forecast);
            loadModelMetrics();
        } else {
            showToast(data.error || 'ML prediction not available', 'error');
        }
    } catch (error) {
        hideLoading();
        console.error('ML prediction failed:', error);
        showToast('ML prediction failed. Models may need to be trained first.', 'error');
    }
}

// Display ML forecast
function displayMLForecast(forecast) {
    const grid = document.getElementById('ml-forecast-grid');
    if (!grid) return;

    grid.innerHTML = '';

    forecast.forEach(day => {
        const card = document.createElement('div');
        card.className = 'forecast-card';
        card.innerHTML = `
            <div class="forecast-day">${day.day_name}</div>
            <div class="forecast-icon">
                <i class="fas fa-brain" style="font-size: 2.5rem; color: var(--primary-color);"></i>
            </div>
            <div class="forecast-temp">${day.temperature}°C</div>
            <div class="forecast-details">
                <div><i class="fas fa-tint"></i> ${day.humidity}%</div>
                ${day.rainfall > 0 ? `<div><i class="fas fa-cloud-rain"></i> ${day.rainfall}mm</div>` : ''}
            </div>
        `;
        grid.appendChild(card);
    });
}

// Load model metrics
async function loadModelMetrics() {
    try {
        const response = await fetch(`${API_BASE}/predict/metrics`);
        const data = await response.json();

        if (data.success) {
            displayModelMetrics(data.metrics);
        }
    } catch (error) {
        console.error('Failed to load metrics:', error);
    }
}

// Display model metrics
function displayModelMetrics(metrics) {
    const container = document.getElementById('model-metrics');
    if (!container) return;

    container.innerHTML = '<h4>Model Accuracy</h4>';

    Object.entries(metrics).forEach(([modelType, modelMetrics]) => {
        const section = document.createElement('div');
        section.style.marginTop = '1rem';
        section.innerHTML = `
            <h5>${modelType.replace('_', ' ').toUpperCase()}</h5>
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-top: 0.5rem;">
                ${Object.entries(modelMetrics).map(([target, values]) => `
                    <div style="padding: 0.75rem; background: var(--bg-tertiary); border-radius: var(--radius-md);">
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">${target.toUpperCase()}</div>
                        <div style="font-size: 0.875rem; color: var(--text-secondary);">
                            R² Score: ${values.r2}<br>
                            Accuracy: ${values.accuracy_percentage}%
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(section);
    });
}

// ===================================
// Favorites
// ===================================

async function updateFavoriteButton() {
    const btn = document.getElementById('add-favorite-btn');
    if (!btn || !currentUser || !currentCity) return;

    try {
        const response = await fetch(`${API_BASE}/favorites`);
        const data = await response.json();

        if (data.success) {
            const isFavorite = data.favorites.some(fav =>
                fav.city_name.toLowerCase() === currentCity.toLowerCase()
            );

            const icon = btn.querySelector('i');
            if (isFavorite) {
                icon.className = 'fas fa-heart';
                btn.title = 'Remove from favorites';
            } else {
                icon.className = 'far fa-heart';
                btn.title = 'Add to favorites';
            }
        }
    } catch (error) {
        console.error('Failed to check favorites:', error);
    }
}

// Toggle favorite
async function toggleFavorite() {
    if (!currentUser) {
        showToast('Please login to add favorites', 'info');
        window.location.href = '/login';
        return;
    }

    if (!currentCity) {
        showToast('Please search for a city first', 'info');
        return;
    }

    const btn = document.getElementById('add-favorite-btn');
    const icon = btn.querySelector('i');
    const isFavorite = icon.className.includes('fas');

    if (isFavorite) {
        // Remove from favorites
        // This would require getting the favorite ID first
        showToast('Remove from dashboard to unfavorite', 'info');
    } else {
        // Add to favorites
        try {
            const response = await fetch(`${API_BASE}/favorites`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ city_name: currentCity })
            });

            const data = await response.json();

            if (data.success) {
                showToast('Added to favorites', 'success');
                icon.className = 'fas fa-heart';
            } else {
                showToast(data.error || 'Failed to add favorite', 'error');
            }
        } catch (error) {
            showToast('Failed to add favorite', 'error');
        }
    }
}

// ===================================
// Map Initialization
// ===================================

let weatherMap = null;

function initializeMap(lat, lon, cityName) {
    const mapContainer = document.getElementById('weather-map');
    if (!mapContainer) return;

    // Remove existing map
    if (weatherMap) {
        weatherMap.remove();
    }

    // Create new map
    weatherMap = L.map('weather-map').setView([lat, lon], 10);

    // Add tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(weatherMap);

    // Add marker
    L.marker([lat, lon]).addTo(weatherMap)
        .bindPopup(`<b>${cityName}</b>`)
        .openPopup();
}

// ===================================
// Event Listeners
// ===================================

document.addEventListener('DOMContentLoaded', () => {
    // ML prediction button
    const mlBtn = document.getElementById('load-ml-btn');
    if (mlBtn) {
        mlBtn.addEventListener('click', loadMLPrediction);
    }

    // Favorite button
    const favBtn = document.getElementById('add-favorite-btn');
    if (favBtn) {
        favBtn.addEventListener('click', toggleFavorite);
    }
});
