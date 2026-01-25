"""
Favorite City Model
Stores user's favorite cities for quick access.
"""
from app import db
from datetime import datetime


class FavoriteCity(db.Model):
    """Model for storing user's favorite cities."""
    
    __tablename__ = 'favorite_cities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    city_name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100))
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Composite index for faster queries
    __table_args__ = (
        db.Index('idx_user_city', 'user_id', 'city_name'),
    )
    
    def __repr__(self):
        return f'<FavoriteCity {self.city_name} for User {self.user_id}>'
    
    def to_dict(self):
        """Convert favorite city object to dictionary."""
        return {
            'id': self.id,
            'city_name': self.city_name,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'created_at': self.created_at.isoformat()
        }
