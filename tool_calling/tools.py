import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_weather(city):
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    city_info = requests.get(url)
    city_info = city_info.json()
    
    lat, lon = city_info[0]['lat'], city_info[0]['lon']

    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&units=metric&lon={lon}&appid={api_key}"
    response = requests.get(url)
    response = response.json()
    return response['main']['temp']