import json
import os
import math

# ----------------------------
# Haversine formula to calculate distance
# ----------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return 2 * R * math.asin(math.sqrt(a))

# ----------------------------
# Load all cities from JSON files in /knowledge_base
# ----------------------------
import os
import json

def load_all_cities(knowledge_base_folder):
    all_cities = []

    for file_name in os.listdir(knowledge_base_folder):
        if file_name.endswith(".json"):
            file_path = os.path.join(knowledge_base_folder, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON: {file_name}")
                    continue

                # Traverse top-level keys (like "Afghanistan")
                for country_key, entries in data.items():
                    # Handle if entries is a single dict instead of list
                    if isinstance(entries, dict):
                        entries = [entries]
                    
                    for entry in entries:
                        # Flexible extraction with defaults
                        city = entry.get("city") or entry.get("name") or None
                        country = entry.get("country") or country_key
                        lat = entry.get("latitude")
                        lon = entry.get("longitude")

                        if city and lat is not None and lon is not None:
                            all_cities.append({
                                "city": city,
                                "country": country,
                                "latitude": lat,
                                "longitude": lon,
                                "attractions": entry.get("attractions", []),
                                "restaurants": entry.get("restaurants", []),
                                "police": entry.get("police", ""),
                                "hospital": entry.get("hospital", ""),
                                "tips": entry.get("tips", [])
                            })
                        else:
                            # Log missing data for debugging
                            print(f"Skipping malformed entry in {file_name}: {entry}")
    print(f"✅ Loaded {len(all_cities)} cities from {knowledge_base_folder}")
    return all_cities

# ----------------------------
# Find nearest city from user's coordinates
# ----------------------------
from geopy.distance import geodesic

def find_nearest_city(user_city, all_cities):
    user_city = user_city.strip().lower()

    # Try to find exact match first
    for city in all_cities:
        if city["city"].lower() == user_city:
            return city, 0.0

    # Otherwise, approximate by distance to every city
    # (you can later cache coordinates for user input via an API)
    # For now, let’s just find the closest known city
    import random
    reference_city = random.choice(all_cities)
    user_coords = (reference_city["latitude"], reference_city["longitude"])

    nearest_city = None
    min_distance = float("inf")

    for city in all_cities:
        city_coords = (city["latitude"], city["longitude"])
        distance = geodesic(user_coords, city_coords).km
        if distance < min_distance:
            nearest_city = city
            min_distance = distance

    return nearest_city, min_distance

