import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from fpdf import FPDF
from tours_dataset import expert_tours
import requests

# --------------------------
# Configure API key
# --------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")


# --------------------------
# Function to generate itinerary (AI)
# --------------------------
def generate_itinerary(city, days, budget, interests, travel_type, currency, month=None):
    month_info = f" for the month of {month}" if month else ""
    prompt = f"""
    You are a professional travel planner.
    Create a {days}-day travel itinerary for a tourist visiting {city}{month_info}.

    Traveler details:
    - Budget: {budget}
    - Travel style: {travel_type}
    - Interests: {interests}
    - Currency: {currency}

    Requirements:
    - Recommended attractions, activities, restaurants, and local transport
    - Approximate daily and total cost in {currency}
    - Essential items to pack
    - Weather conditions and seasonal tips
    - Money-saving tips and avoid tourist traps
    - Day-by-day structured plan
    """
    response = model.generate_content(prompt)
    return response.text


# --------------------------
# Function to create PDF
# --------------------------
def create_itinerary_pdf(title, itinerary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.multi_cell(0, 10, f"{title}\n\n{itinerary}")
    output_path = f"{title.replace(' ', '_')}.pdf"
    pdf.output(output_path, "F")
    return output_path

# ---------------------------
# Streamlit App Layout
# ---------------------------
# --------------------------
# Streamlit UI
# --------------------------
st.set_page_config(page_title="🌍 THE VOYAGERS", layout="wide")
st.title("🌍 THE VOYAGERS")
st.markdown("Create **personalized travel itineraries** or explore **expert-curated tours** ✨")

# --- Custom AI Itinerary Generator ---
st.header("✈️ AI Itinerary Generator")

cities_input = st.text_input("Enter cities you want to visit (comma separated)")
cities = [city.strip() for city in cities_input.split(",") if city.strip()]

city_days = {}
for city in cities:
    days = st.number_input(f"How many days do you plan to spend in {city}?", min_value=1, key=city)
    city_days[city] = days

budget = st.selectbox("Budget", ["low", "medium", "high"])
interests = st.text_input("Main interests (food, history, art, adventure, shopping, etc.)")
travel_type = st.selectbox("Travel type", ["solo", "couple", "family", "group"])
currency = st.text_input("Preferred currency (e.g., USD, AUD, EUR)")
travel_month = st.text_input("Travel month (optional)")


if st.button("✨ Generate Itinerary"):
    st.subheader("📌 Your Personalized Itinerary")

    for city, days in city_days.items():
        with st.expander(f"📍 {city} ({days} days)", expanded=True):
            with st.spinner(f"Generating itinerary for {city}..."):
                itinerary = generate_itinerary(
                    city, days, budget, interests, travel_type, currency, travel_month or None
                )
                st.markdown(itinerary)

                # PDF download
                pdf_path = create_itinerary_pdf(f"{city} Trip", itinerary)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="📥 Download PDF",
                        data=f,
                        file_name=f"{city}_itinerary.pdf",
                        mime="application/pdf"
                    )

    st.success("✅ Itineraries generated successfully!")

# Section 2: Expert Tours
st.header("🌟 Expert Curated Tours by Continent")

for continent, tours in expert_tours.items():
    st.subheader(continent)
    cols = st.columns(len(tours))  # Display tours side by side

    for idx, tour in enumerate(tours):
        with cols[idx]:
            st.markdown(f"**{tour['title']}**")
            st.write(f"Duration: {tour['duration']}")
            st.write(f"Budget: {tour['budget']}")
            st.write(f"Description: {tour['description']}")

            if st.button(f"View Itinerary - {tour['title']}", key=f"{continent}_{idx}"):
                st.write("### Itinerary")
                for day, plan in enumerate(tour["itinerary"], start=1):
                    st.write(f"Day {day}: {plan}")

                # Generate PDF for this tour
                pdf_path = create_tour_pdf(tour)
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        "📥 Download Tour Itinerary PDF",
                        data=f,
                        file_name=pdf_path,
                        mime="application/pdf",
                        key=f"download_{continent}_{idx}",
                    )
# ---------------------------------------------------
# 🧭 City Tourist Guide (New Feature Integration)
# ---------------------------------------------------
from city_guide import load_all_cities, find_nearest_city

st.header("🧭 City Tourist Guide")

if st.button("Find Nearest Tourist City"):
    with st.spinner("Detecting location and finding the nearest tourist city..."):
        user_lat, user_lon, user_city, user_country = get_location_from_ip()
        st.write(f"📍 Your detected location: **{user_city}, {user_country}**")

        # Load dataset and find nearest city
        all_cities = load_all_cities("knowledge_base")
        nearest_city, distance = find_nearest_city(user_lat, user_lon, all_cities)

        if nearest_city:
            st.success(f"Nearest tourist city: **{nearest_city['city']}**, {nearest_city['country']} ({distance} km away)")

            # Display attractions
            st.subheader("🏰 Attractions")
            for a in nearest_city["attractions"]:
                st.markdown(f"- **{a['name']}**, {a.get('address', 'No address')}")

            # Display restaurants
            st.subheader("🍽️ Restaurants")
            for r in nearest_city["restaurants"]:
                st.markdown(f"- **{r['name']}**, {r.get('address', 'No address')}")

            # Display emergency info
            st.subheader("🚨 Emergency Contacts")
            for e in nearest_city["emergency"]:
                st.markdown(f"- **{e['type']}**: {e['name']} ({e['address']})")

            # Display tips
            st.subheader("💡 Travel Tips")
            for tip in nearest_city["tips"]:
                st.markdown(f"- {tip}")

        else:
            st.error("No nearby city found in database. Try again later.")

