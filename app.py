"""A small weather lookup served behind the Terraform-managed reverse proxy."""
import json
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from flask import Flask, render_template_string, request

app = Flask(__name__)

WEATHER_CODES = {
    0: 'Clear sky', 1: 'Mostly clear', 2: 'Partly cloudy', 3: 'Overcast',
    45: 'Fog', 48: 'Freezing fog', 51: 'Light drizzle', 53: 'Drizzle',
    55: 'Heavy drizzle', 56: 'Freezing drizzle', 57: 'Freezing drizzle',
    61: 'Light rain', 63: 'Rain', 65: 'Heavy rain', 66: 'Freezing rain',
    67: 'Freezing rain', 71: 'Light snow', 73: 'Snow', 75: 'Heavy snow',
    77: 'Snow grains', 80: 'Light showers', 81: 'Showers', 82: 'Heavy showers',
    85: 'Snow showers', 86: 'Heavy snow showers', 95: 'Thunderstorm',
    96: 'Thunderstorm with hail', 99: 'Thunderstorm with hail',
}

PAGE = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Weather Lookup</title>
  <style>
    :root { font-family: system-ui, -apple-system, sans-serif; color: #142c3d; background: #eef5f5; }
    * { box-sizing: border-box; }
    body { margin: 0; min-height: 100vh; background: linear-gradient(145deg, #e6f3f1, #f6f8fa 60%, #e9f2f8); }
    main { max-width: 680px; margin: 0 auto; padding: 72px 24px 48px; }
    .eyebrow { color: #126a69; text-transform: uppercase; letter-spacing: .12em; font-size: .75rem; font-weight: 700; }
    h1 { font-size: clamp(2.4rem, 7vw, 3.7rem); letter-spacing: -.05em; line-height: 1.05; margin: 16px 0; }
    .intro { color: #506977; line-height: 1.6; margin-bottom: 30px; }
    .panel { background: white; border: 1px solid #dce8e9; border-radius: 20px; padding: 28px; box-shadow: 0 14px 40px #183d4b0d; }
    label { display: block; font-weight: 650; font-size: .9rem; margin-bottom: 9px; }
    form { display: flex; gap: 10px; }
    input { min-width: 0; flex: 1; border: 1px solid #b9cbce; border-radius: 10px; padding: 13px 14px; font: inherit; }
    button { border: 0; background: #126a69; color: white; border-radius: 10px; padding: 13px 20px; font: inherit; font-weight: 700; cursor: pointer; }
    button:hover { background: #0b5453; }
    input:focus-visible, button:focus-visible { outline: 3px solid #78beba; outline-offset: 2px; }
    .hint, footer { color: #627985; font-size: .85rem; line-height: 1.5; }
    .error { color: #8c362c; background: #fff3f0; border-radius: 10px; padding: 14px; margin: 22px 0 0; }
    .result { margin-top: 28px; border-top: 1px solid #e4eeee; padding-top: 24px; }
    h2 { margin: 0 0 4px; font-size: 1.25rem; }
    .condition { color: #506977; margin: 0; }
    .temperature { font-size: 3.5rem; letter-spacing: -.06em; font-weight: 700; margin: 12px 0; }
    .details { display: flex; gap: 32px; color: #506977; font-size: .95rem; flex-wrap: wrap; }
    .details strong { color: #142c3d; }
    footer { margin-top: 24px; }
    a { color: #126a69; }
    @media (max-width: 450px) { main { padding-top: 45px; } form { flex-direction: column; } }
  </style>
</head>
<body><main>
  <span class="eyebrow">Current conditions</span>
  <h1>Weather, wherever<br>you are.</h1>
  <p class="intro">Search for a city to see its current weather, humidity, and wind.</p>
  <section class="panel" aria-label="Weather lookup">
    <label for="city">City or location</label>
    <form action="/" method="get">
      <input id="city" name="city" type="search" maxlength="100" placeholder="e.g. Boston, United States" value="{{ city }}" required>
      <button type="submit">Check weather</button>
    </form>
    <p class="hint">Use a city and region or country to narrow your search.</p>
    {% if error %}<p class="error" role="alert">{{ error }}</p>{% endif %}
    {% if weather %}
    <div class="result" aria-live="polite">
      <h2>{{ weather.location }}</h2>
      <p class="condition">{{ weather.condition }}</p>
      <p class="temperature">{{ weather.temperature }}{{ weather.temperature_unit }}</p>
      <div class="details"><span>Humidity <strong>{{ weather.humidity }}%</strong></span><span>Wind <strong>{{ weather.wind }} {{ weather.wind_unit }}</strong></span></div>
    </div>
    {% endif %}
  </section>
  <footer>Weather data from <a href="https://open-meteo.com/">Open-Meteo</a>. Current conditions are based on weather models.</footer>
</main></body></html>'''


def fetch_json(base_url, params):
    with urlopen(f'{base_url}?{urlencode(params)}', timeout=6) as response:
        return json.load(response)


def lookup_weather(city):
    locations = fetch_json('https://geocoding-api.open-meteo.com/v1/search', {
        'name': city, 'count': 1, 'language': 'en', 'format': 'json',
    }).get('results', [])
    if not locations:
        return None
    location = locations[0]
    forecast = fetch_json('https://api.open-meteo.com/v1/forecast', {
        'latitude': location['latitude'], 'longitude': location['longitude'],
        'current': 'temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m',
        'temperature_unit': 'fahrenheit', 'wind_speed_unit': 'mph',
    })
    current = forecast['current']
    units = forecast['current_units']
    location_parts = [location.get('name'), location.get('admin1'), location.get('country')]
    return {
        'location': ', '.join(part for part in location_parts if part),
        'temperature': current['temperature_2m'], 'temperature_unit': units['temperature_2m'],
        'humidity': current['relative_humidity_2m'], 'wind': current['wind_speed_10m'],
        'wind_unit': units['wind_speed_10m'],
        'condition': WEATHER_CODES.get(current['weather_code'], 'Weather conditions unavailable'),
    }


@app.get('/')
def home():
    city = request.args.get('city', '').strip()
    weather = None
    error = None
    if 'city' in request.args:
        if not city or len(city) > 100:
            error = 'Enter a city using 1 to 100 characters.'
        else:
            try:
                weather = lookup_weather(city)
                if weather is None:
                    error = 'No locations found. Try another city or include a country.'
            except (URLError, TimeoutError, OSError, ValueError, KeyError, TypeError, IndexError):
                error = 'Weather service is unavailable. Please try again shortly.'
    return render_template_string(PAGE, city=city, weather=weather, error=error)


@app.get('/health')
def health():
    return {'status': 'healthy'}
