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
def load_all_cities(base_path="knowledge_base"):
    cities_data = []

    for file in os.listdir(base_path):
        if not file.endswith(".json"):
            continue

        path = os.path.join(base_path, file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                continent_data = json.load(f)
        except Exception as e:
            print(f"❌ Error reading {file}: {e}")
            continue

        # Case 1: JSON is a dictionary
        if isinstance(continent_data, dict):
            for country, cities in continent_data.items():
                if isinstance(cities, dict):
                    for city_name, city_info in cities.items():
                        if not isinstance(city_info, dict):
                            continue
                        cities_data.append({
                            "city": city_name,
                            "country": country,
                            "continent": file.replace(".json", ""),
                            "latitude": city_info.get("latitude"),
                            "longitude": city_info.get("longitude"),
                            "attractions": city_info.get("attractions", []),
                            "restaurants": city_info.get("restaurants", []),
                            "emergency": city_info.get("emergency", []),
                            "tips": city_info.get("tips", [])
                        })

        # Case 2: JSON is a list
        elif isinstance(continent_data, list):
            for city_info in continent_data:
                if not isinstance(city_info, dict):
                    continue
                cities_data.append({
                    "city": city_info.get("city"),
                    "country": city_info.get("country"),
                    "continent": file.replace(".json", ""),
                    "latitude": city_info.get("latitude"),
                    "longitude": city_info.get("longitude"),
                    "attractions": city_info.get("attractions", []),
                    "restaurants": city_info.get("restaurants", []),
                    "emergency": city_info.get("emergency", []),
                    "tips": city_info.get("tips", [])
                })

        else:
            print(f"⚠️ Unexpected data format in {file}: {type(continent_data)}")

    print(f"✅ Loaded {len(cities_data)} cities from {base_path}")
    return cities_data


# ----------------------------
# Find nearest city from user's coordinates
# ----------------------------
def find_nearest_city(lat, lon, cities_data):
    min_distance = float("inf")
    nearest_city = None
    for city in cities_data:
        if city["latitude"] and city["longitude"]:
            distance = haversine(lat, lon, city["latitude"], city["longitude"])
            if distance < min_distance:
                min_distance = distance
                nearest_city = city
    return nearest_city, round(min_distance, 1)
