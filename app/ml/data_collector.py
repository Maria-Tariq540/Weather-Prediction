"""
Data Collector
Collects historical weather data for ML model training.
"""
import requests
import pandas as pd
from datetime import datetime, timedelta
import os
import time


class DataCollector:
    """Collects historical weather data from OpenWeatherMap API."""
    
    def __init__(self, api_key):
        """
        Initialize data collector.
        
        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key
        self.base_url = 'https://api.openweathermap.org/data/2.5'
    
    def collect_historical_data(self, city_name, days=30):
        """
        Collect historical weather data for a city.
        Note: Free tier doesn't have historical data API, so we'll use forecast
        and current data to build a dataset. In production, use Historical Weather API.
        
        Args:
            city_name: Name of the city
            days: Number of days of data to collect
        
        Returns:
            DataFrame with historical weather data
        """
        print(f"Collecting weather data for {city_name}...")
        
        # For demonstration, we'll create synthetic historical data
        # In production, use the Historical Weather API (paid tier)
        data = self._generate_synthetic_data(city_name, days)
        
        return data
    
    def _generate_synthetic_data(self, city_name, days):
        """
        Generate synthetic historical data for demonstration.
        In production, replace this with actual API calls to Historical Weather API.
        
        Args:
            city_name: Name of the city
            days: Number of days
        
        Returns:
            DataFrame with synthetic weather data
        """
        import numpy as np
        
        # Get current weather to base synthetic data on
        url = f'{self.base_url}/weather'
        params = {'q': city_name, 'appid': self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            current = response.json()
            
            base_temp = current['main']['temp'] - 273.15  # Convert to Celsius
            base_humidity = current['main']['humidity']
            base_pressure = current['main']['pressure']
            
        except Exception as e:
            print(f"Error fetching current weather: {e}")
            # Use default values
            base_temp = 20
            base_humidity = 60
            base_pressure = 1013
        
        # Generate synthetic data
        dates = []
        temperatures = []
        humidity = []
        pressure = []
        wind_speed = []
        rainfall = []
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days-i)
            dates.append(date)
            
            # Add seasonal variation and random noise
            day_of_year = date.timetuple().tm_yday
            seasonal_factor = np.sin(2 * np.pi * day_of_year / 365)
            
            temp = base_temp + seasonal_factor * 10 + np.random.normal(0, 3)
            hum = base_humidity + np.random.normal(0, 10)
            pres = base_pressure + np.random.normal(0, 5)
            wind = abs(np.random.normal(5, 2))
            rain = max(0, np.random.exponential(2) if np.random.random() < 0.3 else 0)
            
            temperatures.append(round(temp, 2))
            humidity.append(max(0, min(100, round(hum, 2))))
            pressure.append(round(pres, 2))
            wind_speed.append(round(wind, 2))
            rainfall.append(round(rain, 2))
        
        df = pd.DataFrame({
            'date': dates,
            'temperature': temperatures,
            'humidity': humidity,
            'pressure': pressure,
            'wind_speed': wind_speed,
            'rainfall': rainfall,
            'day_of_year': [d.timetuple().tm_yday for d in dates],
            'month': [d.month for d in dates],
            'day': [d.day for d in dates]
        })
        
        return df
    
    def save_data(self, df, city_name, output_dir='data'):
        """
        Save collected data to CSV file.
        
        Args:
            df: DataFrame with weather data
            city_name: Name of the city
            output_dir: Output directory
        
        Returns:
            Path to saved file
        """
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"{city_name.lower().replace(' ', '_')}_weather_data.csv"
        filepath = os.path.join(output_dir, filename)
        
        df.to_csv(filepath, index=False)
        print(f"Data saved to {filepath}")
        
        return filepath
    
    def collect_and_save(self, cities, days=30, output_dir='data'):
        """
        Collect and save data for multiple cities.
        
        Args:
            cities: List of city names
            days: Number of days of data
            output_dir: Output directory
        
        Returns:
            Dictionary mapping city names to file paths
        """
        results = {}
        
        for city in cities:
            try:
                df = self.collect_historical_data(city, days)
                filepath = self.save_data(df, city, output_dir)
                results[city] = filepath
                
                # Rate limiting
                time.sleep(1)
                
            except Exception as e:
                print(f"Error collecting data for {city}: {e}")
                results[city] = None
        
        return results


# Example usage
if __name__ == '__main__':
    import sys
    
    # Get API key from environment or command line
    api_key = os.getenv('OPENWEATHER_API_KEY')
    
    if not api_key:
        print("Error: OPENWEATHER_API_KEY not set")
        sys.exit(1)
    
    # Collect data for sample cities
    collector = DataCollector(api_key)
    cities = ['London', 'New York', 'Tokyo', 'Paris', 'Mumbai']
    
    print("Collecting weather data for training...")
    results = collector.collect_and_save(cities, days=90)
    
    print("\nData collection complete!")
    for city, filepath in results.items():
        if filepath:
            print(f"✓ {city}: {filepath}")
        else:
            print(f"✗ {city}: Failed")
