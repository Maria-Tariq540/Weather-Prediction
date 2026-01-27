"""Models package initialization."""
from app.models.user import User
from app.models.favorite_city import FavoriteCity
from app.models.weather_data import WeatherData

__all__ = ['User', 'FavoriteCity', 'WeatherData']
