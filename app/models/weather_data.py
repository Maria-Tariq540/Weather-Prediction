"""
Weather Data Model
Caches weather data to reduce API calls and improve performance.
"""
from app import db
from datetime import datetime
import json


class WeatherData(db.Model):
    """Model for caching weather data."""
    
    __tablename__ = 'weather_data'
    
    id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(100), nullable=False, index=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    data_type = db.Column(db.String(20), nullable=False)  # 'current', 'forecast', 'aqi'
    data = db.Column(db.Text, nullable=False)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # Composite index for faster queries
    __table_args__ = (
        db.Index('idx_city_type', 'city_name', 'data_type'),
    )
    
    def __repr__(self):
        return f'<WeatherData {self.city_name} ({self.data_type})>'
    
    def set_data(self, data_dict):
        """Store data as JSON string."""
        self.data = json.dumps(data_dict)
    
    def get_data(self):
        """Retrieve data as dictionary."""
        return json.loads(self.data)
    
    def is_expired(self):
        """Check if cached data has expired."""
        return datetime.utcnow() > self.expires_at
