"""
Route calculation service using OpenRouteService API.

The API key is read from the ORS_API_KEY environment variable.
Never hardcode the key in source code.
"""

import os
import requests


ORS_API_KEY = os.environ.get('ORS_API_KEY', '')

ORS_BASE = 'https://api.openrouteservice.org'


class RouteServiceError(Exception):
    """Raised when route calculation fails."""
    pass


def geocode(place_name):
    """
    Convert a place name to (lat, lon) coordinates.
    Uses ORS Pelias geocoder.
    Returns (lat, lon, formatted_label) or raises RouteServiceError.
    """
    if not ORS_API_KEY:
        raise RouteServiceError('ORS_API_KEY is not set. Configure the environment variable.')

    url = f'{ORS_BASE}/geocode/search'
    params = {
        'api_key': ORS_API_KEY,
        'text': place_name,
        'size': 1,
        # Bias to Kenya
        'boundary.country': 'KEN',
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise RouteServiceError(f'Geocoding request failed: {e}')

    features = data.get('features', [])
    if not features:
        raise RouteServiceError(f'Could not find location: "{place_name}"')

    feature = features[0]
    lon, lat = feature['geometry']['coordinates']
    label = feature['properties'].get('label', place_name)
    return lat, lon, label


def get_route_distance(start_place, end_place):
    """
    Calculate driving distance (in km) between two place names.
    Returns dict with: distance_km, duration_hours, start_label, end_label.
    """
    if not ORS_API_KEY:
        raise RouteServiceError('ORS_API_KEY is not set.')

    start_lat, start_lon, start_label = geocode(start_place)
    end_lat, end_lon, end_label = geocode(end_place)

    url = f'{ORS_BASE}/v2/directions/driving-car'
    headers = {
        'Authorization': ORS_API_KEY,
        'Content-Type': 'application/json',
    }
    body = {
        'coordinates': [
            [start_lon, start_lat],
            [end_lon, end_lat],
        ],
        'units': 'km',
    }

    try:
        resp = requests.post(url, json=body, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        raise RouteServiceError(f'Route request failed: {e}')

    try:
        summary = data['routes'][0]['summary']
        distance_km = summary['distance']
        duration_hours = summary['duration'] / 3600.0
    except (KeyError, IndexError) as e:
        raise RouteServiceError(f'Unexpected response format: {e}')

    return {
        'distance_km': round(distance_km, 1),
        'duration_hours': round(duration_hours, 2),
        'start_label': start_label,
        'end_label': end_label,
    }