import requests
from math import radians, sin, cos, sqrt, asin

def geocode_address(address, city, state, zip_code):
    """Convert address to coordinates using Nominatim (OpenStreetMap) API"""
    try:
        full_address = f"{address}, {city}, {state} {zip_code}, USA"
        params = {
            'q': full_address,
            'format': 'json',
            'limit': 1
        }
        headers = {
            'User-Agent': 'RentalApp/1.0'  # Required by Nominatim ToS
        }
        response = requests.get('https://nominatim.openstreetmap.org/search', 
                              params=params, headers=headers)
        data = response.json()
        
        if data:
            return {
                'latitude': float(data[0]['lat']),
                'longitude': float(data[0]['lon'])
            }
    except Exception as e:
        print(f"Geocoding error: {e}")
    return None

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula"""
    R = 3959.87433  # Earth's radius in miles

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    
    return R * c

def get_properties_within_radius(latitude, longitude, radius_miles, query):
    """Filter properties within a given radius"""
    # First, get a rough square boundary to reduce the number of distance calculations
    lat_range = radius_miles / 69  # approximately 69 miles per degree of latitude
    lon_range = radius_miles / (cos(radians(latitude)) * 69)
    
    properties = query.filter(
        Property.latitude.between(latitude - lat_range, latitude + lat_range),
        Property.longitude.between(longitude - lon_range, longitude + lon_range)
    ).all()
    
    # Then filter more precisely using actual distance calculation
    return [p for p in properties if calculate_distance(
        latitude, longitude, p.latitude, p.longitude) <= radius_miles]
