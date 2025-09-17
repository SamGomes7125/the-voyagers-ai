# app.py
import streamlit as st
import google.generativeai as genai

# --------------------------
# Configure your API key
# --------------------------
import os
from dotenv import load_dotenv
load_dotenv()  

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# --------------------------
# Function to generate itinerary
# --------------------------
def generate_itinerary(city, days, budget, interests, travel_type, currency, month=None):
    month_info = f" for the month of {month}" if month else ""
    prompt = f"""
    You are a professional travel planner.
    Create a {days}-day travel itinerary for a tourist visiting {city}{month_info}.

    Traveler details:
    - Budget: {budget} (low/medium/high)
    - Travel style: {travel_type}
    - Interests: {interests}
    - Currency: {currency}

    Requirements:
    1. Include recommended attractions, activities, restaurants, and local transport.
    2. Provide approximate daily and total cost in {currency}, according to the budget type.
    3. Mention essential items the traveler should pack for the trip.
    4. Provide probable weather conditions, temperature ranges, and seasonal tips.
    5. Tips to save money and avoid tourist traps.
    6. Structured day by day with clear bullet points.
    7. Make it practical and tourist-friendly.
    """
    response = model.generate_content(prompt)
    return response.text

# --------------------------
# Streamlit UI
# --------------------------
st.set_page_config(page_title="🌍 THE VOYAGERS AI Itinerary", layout="wide")

st.title("🌍 THE VOYAGERS AI Itinerary Generator")
st.markdown("Create **personalized travel itineraries** powered by AI ✨")

# Sidebar for Inputs
st.sidebar.header("✈️ Travel Preferences")
# --- User Inputs ---
cities_input = st.text_input("Enter cities you want to visit (comma separated)")
cities = [city.strip() for city in cities_input.split(",") if city.strip()]

city_days = {}
for city in cities:
    days = st.number_input(f"How many days do you plan to spend in {city}?", min_value=1)
    city_days[city] = days

budget = st.selectbox("Budget", ["low", "medium", "high"])
interests = st.text_input("Main interests (food, history, art, adventure, shopping, etc.)")
travel_type = st.selectbox("Travel type", ["solo", "couple", "family", "group"])
currency = st.text_input("Preferred currency (e.g., USD, AUD, EUR)")
travel_month = st.text_input("Travel month (optional, for weather info)")


# Main area
st.divider()

if st.button("✨ Generate Itinerary"):
    st.subheader("📌 Your Personalized Itinerary")

    for city, days in city_days.items():
        with st.expander(f"📍 {city} ({days} days)", expanded=True):
            with st.spinner(f"Generating itinerary for {city}..."):
                itinerary = generate_itinerary(
                    city, days, budget, interests, travel_type, currency, travel_month or None
                )
                # Better formatting
                st.markdown(itinerary)

    st.success("✅ Itineraries generated successfully!")
