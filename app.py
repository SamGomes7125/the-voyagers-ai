# app.py
import streamlit as st
import google.generativeai as genai
import os
import requests
from dotenv import load_dotenv
from fpdf import FPDF
import tempfile

# --------------------------
# Configure your API key
# --------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# --------------------------
# Utility: Clean text for PDF
# --------------------------
def clean_text(text):
    replacements = {
        "–": "-",
        "—": "-",
        "•": "*",
        "°": " degrees",
        "“": '"',
        "”": '"',
        "’": "'",
        "→": "->",
        "…": "...",
        "🌍": "",
        "✨": "",
        "✅": "",
        "📌": "",
        "📍": "",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode("latin-1", "ignore").decode("latin-1")

# --------------------------
# Utility: Fetch Unsplash Image
# --------------------------
def fetch_unsplash_image(city, day):
    url = f"https://source.unsplash.com/800x600/?{city},landmark"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            img_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
            with open(img_file, "wb") as f:
                f.write(response.content)
            return img_file
    except:
        return None
    return None

# --------------------------
# Function to generate itinerary text
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
def create_pdf(itineraries):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for city, data in itineraries.items():
        text, images = data["text"], data["images"]
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(200, 10, f"{city} Itinerary", ln=True, align="C")

        pdf.set_font("Arial", size=12)
        for line in clean_text(text).split("\n"):
            pdf.multi_cell(0, 10, line)

        # Add images
        for img_path in images:
            try:
                pdf.image(img_path, w=150)
            except:
                continue

    # Save PDF in a temp file
    pdf_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(pdf_file.name)
    return pdf_file.name

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

budget = st.text_input("Budget (low, medium, high)")
interests = st.text_input("Main interests (food, history, art, adventure, shopping, etc.)")
travel_type = st.text_input("Travel type (solo, couple, family, group)")
currency = st.text_input("Preferred currency")
travel_month = st.text_input("Travel month (optional, for weather info)")

# --------------------------
# Generate Itinerary + PDF
# --------------------------
if st.button("✨ Generate Itinerary"):
    st.subheader("📌 Your Personalized Itinerary")
    itineraries = {}

    for city, days in city_days.items():
        with st.expander(f"📍 {city} ({days} days)", expanded=True):
            with st.spinner(f"Generating itinerary for {city}..."):
                itinerary_text = generate_itinerary(
                    city, days, budget, interests, travel_type, currency, travel_month or None
                )
                st.markdown(itinerary_text)

                # Fetch images for each day
                images = []
                for day in range(1, days + 1):
                    img_file = fetch_unsplash_image(city, day)
                    if img_file:
                        images.append(img_file)
                        st.image(img_file, caption=f"{city} - Day {day}")

                itineraries[city] = {"text": itinerary_text, "images": images}

    # Create PDF
    pdf_path = create_pdf(itineraries)
    with open(pdf_path, "rb") as pdf_file:
        st.download_button(
            label="📥 Download Itinerary as PDF",
            data=pdf_file,
            file_name="travel_itinerary.pdf",
            mime="application/pdf"
        )
