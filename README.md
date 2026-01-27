# 🌤️ Weather Prediction Web Application

A production-ready, full-stack weather prediction application powered by Machine Learning. Built with Flask, scikit-learn, and modern web technologies.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🎯 Core Features
- **Real-time Weather Data** - Live weather updates from OpenWeatherMap API
- **ML-Based Predictions** - 7-day forecasts using Linear Regression and Random Forest models
- **Air Quality Index** - Monitor AQI and pollutant levels
- **Weather Alerts** - Intelligent alerts for extreme weather conditions
- **Interactive Charts** - Beautiful visualizations with Chart.js
- **Map Integration** - Location-based weather display with Leaflet.js

### 👤 User Features
- **User Authentication** - Secure signup/login system
- **Favorite Cities** - Save and manage favorite locations
- **Personalized Dashboard** - Quick access to saved cities
- **Dark/Light Mode** - Theme toggle with localStorage persistence

### 🤖 Machine Learning
- **Multiple Models** - Linear Regression and Random Forest
- **Model Comparison** - Compare predictions from different models
- **Accuracy Metrics** - View model performance (MAE, RMSE, R²)
- **Retraining Capability** - Update models with new data

## 🏗️ Project Structure

```
Weather Prediction/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── models/                  # Database models
│   │   ├── user.py
│   │   ├── favorite_city.py
│   │   └── weather_data.py
│   ├── routes/                  # API endpoints
│   │   ├── auth.py              # Authentication
│   │   ├── weather.py           # Weather data
│   │   ├── prediction.py        # ML predictions
│   │   ├── favorites.py         # Favorite cities
│   │   └── main.py              # HTML pages
│   ├── services/                # Business logic
│   │   ├── weather_service.py   # OpenWeatherMap integration
│   │   ├── prediction_service.py # ML predictions
│   │   └── notification_service.py # Weather alerts
│   ├── ml/                      # Machine Learning
│   │   ├── data_collector.py    # Historical data collection
│   │   ├── preprocessor.py      # Data preprocessing
│   │   ├── models.py            # ML model definitions
│   │   ├── trainer.py           # Model training pipeline
│   │   └── saved_models/        # Trained models
│   ├── static/                  # Frontend assets
│   │   ├── css/style.css
│   │   └── js/
│   │       ├── main.js
│   │       ├── weather.js
│   │       ├── charts.js
│   │       └── theme.js
│   └── templates/               # HTML templates
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── signup.html
│       └── dashboard.html
├── data/                        # Training data
├── config.py                    # Configuration
├── wsgi.py                      # WSGI entry point (Production)
├── app.py                       # Application entry point (Development)
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
└── README.md                    # This file
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- OpenWeatherMap API key ([Get it here](https://openweathermap.org/api))

### Installation

1. **Clone the repository**
   ```bash
   cd "Weather Prediction"
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   ```bash
   copy .env.example .env
   ```
   
   Edit `.env` and add your OpenWeatherMap API key:
   ```
   OPENWEATHER_API_KEY=your_api_key_here
   SECRET_KEY=your_secret_key_here
   ```

6. **Train ML models** (Optional but recommended)
   ```bash
   python -m app.ml.trainer
   ```
   
   This will:
   - Collect historical weather data
   - Preprocess and engineer features
   - Train Linear Regression and Random Forest models
   - Save trained models to `app/ml/saved_models/`

7. **Run the application**
   ```bash
   python app.py
   ```

8. **Open your browser**
   ```
   http://localhost:5000
   ```

## 📖 Usage

### Search for Weather
1. Enter a city name in the search bar
2. View current weather, 7-day forecast, and AQI
3. Check weather alerts and recommendations

### ML Predictions
1. Search for a city
2. Click on the "ML Prediction" tab
3. Select a model (Random Forest recommended)
4. Click "Load Prediction" to see AI-generated forecasts

### User Account
1. Sign up for an account
2. Login to access the dashboard
3. Add cities to favorites for quick access
4. View all your favorite cities' weather at once

### Dark Mode
- Click the moon/sun icon in the navigation bar
- Theme preference is saved automatically

## 🧠 Machine Learning Models

### Data Collection
The application uses historical weather data to train ML models. For demonstration purposes, synthetic data is generated based on current weather patterns. In production, you can integrate with OpenWeatherMap's Historical Weather API.

### Models Implemented

1. **Linear Regression**
   - Fast, simple baseline model
   - Good for understanding linear relationships
   - Lower accuracy but quick predictions

2. **Random Forest**
   - Ensemble learning method
   - Higher accuracy than Linear Regression
   - Handles non-linear patterns well
   - **Recommended for production use**

### Features Used
- Temperature (current and lag features)
- Humidity (current and lag features)
- Pressure
- Wind speed
- Time-based features (day of year, month, cyclical encoding)
- Rolling averages (3-day, 7-day)

### Model Performance
Models are evaluated using:
- **MAE** (Mean Absolute Error) - Average prediction error
- **RMSE** (Root Mean Squared Error) - Penalizes larger errors
- **R² Score** - Proportion of variance explained (0-1, higher is better)

View model metrics in the app under "ML Prediction" → "Model Accuracy"

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/check` - Check authentication status

### Weather
- `GET /api/weather/current/<city>` - Get current weather
- `GET /api/weather/forecast/<city>` - Get 5-day forecast
- `GET /api/weather/aqi/<city>` - Get Air Quality Index
- `GET /api/weather/search/<query>` - Search cities (auto-suggest)
- `GET /api/weather/complete/<city>` - Get all weather data

### ML Predictions
- `GET /api/predict/<city>?model=<model_type>&days=<days>` - Get ML predictions
- `GET /api/predict/metrics` - Get model accuracy metrics
- `GET /api/predict/compare/<city>` - Compare models

### Favorites
- `GET /api/favorites` - Get user's favorite cities
- `POST /api/favorites` - Add city to favorites
- `DELETE /api/favorites/<id>` - Remove city from favorites

## 🛠️ Technology Stack

### Backend
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database
- **Flask-Login** - User session management
- **Flask-CORS** - Cross-origin resource sharing
- **Requests** - HTTP library for API calls

### Machine Learning
- **scikit-learn** - ML models and preprocessing
- **pandas** - Data manipulation
- **NumPy** - Numerical computing
- **joblib** - Model serialization

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling (Custom design system)
- **JavaScript** - Interactivity
- **Chart.js** - Data visualization
- **Leaflet.js** - Interactive maps
- **Font Awesome** - Icons

### External APIs
- **OpenWeatherMap API** - Weather data, forecasts, and AQI

## 🎨 Design Features

- **Modern UI** - Clean, professional design
- **Glassmorphism** - Frosted glass effect on cards
- **Gradient Accents** - Vibrant color gradients
- **Smooth Animations** - Micro-interactions and transitions
- **Responsive Design** - Works on all devices
- **Dark Mode** - Eye-friendly theme with localStorage persistence

## 📊 Database Schema

### Users
- id, username, email, password_hash
- created_at, updated_at

### Favorite Cities
- id, user_id, city_name, country
- latitude, longitude, created_at

### Weather Data (Cache)
- id, city_name, latitude, longitude
- data_type, data (JSON), created_at, expires_at

## 🔒 Security Features

- Password hashing with Werkzeug
- Session management with Flask-Login
- CSRF protection
- Secure cookie settings
- Environment variable configuration

## 🚀 Deployment

### Production Checklist

1. **Update configuration**
   - Set `FLASK_ENV=production`
   - Use PostgreSQL instead of SQLite
   - Set strong `SECRET_KEY`
   - Enable HTTPS with `SESSION_COOKIE_SECURE=True`

2. **Database migration**
   - Use Flask-Migrate for database versioning
   - Run migrations before deployment

3. **Web server**
   - Use Gunicorn or uWSGI
   - Set up Nginx as reverse proxy

4. **Environment**
   - Use environment variables for sensitive data
   - Never commit `.env` file

5. **Monitoring**
   - Set up logging
   - Monitor API rate limits
   - Track model performance

### AWS EC2 Deployment (Nginx + Gunicorn)

1. **Connect to EC2 Instance**
2. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install python3-pip python3-venv nginx
   ```
3. **Setup Nginx Configuration**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```
4. **Run Gunicorn in Background**
   ```bash
   gunicorn -w 4 -b 127.0.0.1:5000 wsgi:app --daemon
   ```

### Example Gunicorn Command
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## 🔮 Future Improvements

- [ ] Add more ML models (LSTM for time series)
- [ ] Implement hourly forecasts
- [ ] Add weather radar maps
- [ ] Email notifications for weather alerts
- [ ] Mobile app (React Native)
- [ ] Historical weather data visualization
- [ ] Weather comparison between cities
- [ ] Export weather reports (PDF)
- [ ] Multi-language support
- [ ] Social sharing features

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Senior Full-Stack Python Developer & Data Scientist**

- Built with ❤️ for final-year projects and portfolios
- Demonstrates full-stack development and ML integration
- Production-ready code with best practices

## 🙏 Acknowledgments

- [OpenWeatherMap](https://openweathermap.org/) for weather data API
- [Chart.js](https://www.chartjs.org/) for beautiful charts
- [Leaflet](https://leafletjs.com/) for interactive maps
- [Font Awesome](https://fontawesome.com/) for icons
- [Flask](https://flask.palletsprojects.com/) for the amazing framework

## 📧 Support

For support, email muhmmadalibintariq@gmail.com or open an issue in the repository.

---

**⭐ If you find this project useful, please consider giving it a star!**
