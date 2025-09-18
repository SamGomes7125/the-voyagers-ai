# app.py
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from fpdf import FPDF
import requests

# --------------------------
# Configure your API key
# --------------------------
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
# Function to create PDF
# --------------------------
def create_itinerary_pdf(city, itinerary_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt=f"Travel Itinerary for {city}", ln=True, align="C")
    pdf.ln(10)

    # Split into days
    days = itinerary_text.split("Day")
    for i, day_plan in enumerate(days[1:], start=1):
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Day {i}", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 8, day_plan.strip())
        pdf.ln(5)

        # Fetch random attraction image from Unsplash
        query = f"{city} attraction"
        url = f"https://source.unsplash.com/600x400/?{query}"
        img_path = f"day{i}.jpg"

        try:
            img_data = requests.get(url, timeout=10).content
            with open(img_path, "wb") as f:
                f.write(img_data)
            pdf.image(img_path, w=100)
            pdf.ln(10)
        except Exception:
            pdf.cell(0, 10, "Image unavailable", ln=True)

    output_path = f"{city}_itinerary.pdf"
    pdf.output(output_path)
    return output_path

# --------------------------
# Streamlit UI
# --------------------------
st.set_page_config(page_title="🌍 THE VOYAGERS AI Itinerary", layout="wide")

st.title("🌍 THE VOYAGERS AI Itinerary Generator")
st.markdown("Create **personalized travel itineraries** powered by AI ✨")

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

st.divider()

if st.button("✨ Generate Itinerary"):
    st.subheader("📌 Your Personalized Itinerary")

    for city, days in city_days.items():
        with st.expander(f"📍 {city} ({days} days)", expanded=True):
            with st.spinner(f"Generating itinerary for {city}..."):
                itinerary = generate_itinerary(
                    city, days, budget, interests, travel_type, currency, travel_month or None
                )
                st.markdown(itinerary)

                # Create PDF
                pdf_path = create_itinerary_pdf(city, itinerary)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label=f"📥 Download {city} Itinerary as PDF",
                        data=f,
                        file_name=pdf_path,
                        mime="application/pdf"
                    )

    st.success("✅ Itineraries generated successfully!")
