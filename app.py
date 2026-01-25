"""
Weather Prediction Web Application
Main entry point for the Flask application.

Author: Senior Full-Stack Developer
Description: Advanced weather prediction system using ML and real-time data
"""
from app import create_app
import os

# Create Flask application
app = create_app()

if __name__ == '__main__':
    # Get port from environment or use default
    port = int(os.getenv('PORT', 5000))
    
    # Run the application
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config['DEBUG']
    )
