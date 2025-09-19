import streamlit as st
from fpdf import FPDF
import os
from tours_dataset import expert_tours

# ---------------------------
# PDF Generator for Expert Tours
# ---------------------------
def create_tour_pdf(tour):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"{tour['title']} - {tour['continent']}", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, f"Duration: {tour['duration']}")
    pdf.multi_cell(0, 10, f"Budget: {tour['budget']}")
    pdf.multi_cell(0, 10, f"Description: {tour['description']}")
    pdf.ln(10)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, "Itinerary:", ln=True)
    pdf.set_font("Arial", size=12)
    for day, plan in enumerate(tour["itinerary"], start=1):
        pdf.multi_cell(0, 10, f"Day {day}: {plan}")

    # Save file
    output_path = f"{tour['title'].replace(' ', '_')}.pdf"
    pdf.output(output_path)
    return output_path


# ---------------------------
# Streamlit App Layout
# ---------------------------
st.title("🌍 The Voyagers AI Travel Planner")

# Section 1: Custom Itinerary Generator
st.header("✈️ Generate Your Own Custom Itinerary")
city = st.text_input("Enter city")
days = st.number_input("Number of days", min_value=1, max_value=30, value=5)

if st.button("Generate Itinerary"):
    st.success(f"Custom Itinerary for {city}")
    itinerary = [f"Day {i+1}: Explore attractions in {city}" for i in range(days)]
    for day in itinerary:
        st.write(day)

    # Create a PDF for this itinerary
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Custom Itinerary for {city}", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    for day in itinerary:
        pdf.multi_cell(0, 10, day)

    custom_pdf = f"Custom_Itinerary_{city}.pdf"
    pdf.output(custom_pdf)

    with open(custom_pdf, "rb") as f:
        st.download_button(
            "📥 Download Custom Itinerary PDF",
            data=f,
            file_name=custom_pdf,
            mime="application/pdf",
        )

st.markdown("---")

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
