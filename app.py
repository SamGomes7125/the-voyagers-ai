import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from fpdf import FPDF
from tours_dataset import expert_tours

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

# --------------------------
# Expert Curated Tours
# --------------------------
st.divider()
st.header("🌍 Expert-Curated Tours")

for continent, tours in expert_tours.items():
    st.subheader(f"🌎 {continent}")
    cols = st.columns(len(tours))
    for idx, tour in enumerate(tours):
        with cols[idx]:
            st.image(tour["image"], use_container_width=True)
            st.markdown(f"**{tour['title']}**")
            st.markdown(f"📅 {tour['duration']} | 💰 {tour['budget']} {tour['currency']}")

            if st.button(f"View Itinerary - {tour['title']}", key=f"{continent}_{idx}"):
                st.session_state["selected_tour"] = tour

# Show selected tour
if "selected_tour" in st.session_state:
    tour = st.session_state["selected_tour"]
    st.subheader(f"📌 Itinerary for {tour['title']}")
    st.markdown(tour["itinerary"])

    pdf_path = create_itinerary_pdf(tour["title"], tour["itinerary"])
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📥 Download PDF",
            data=f,
            file_name=f"{tour['title'].replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
