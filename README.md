# The Voyagers: AI Travel Planner

A Streamlit app that generates personalised travel itineraries with Google Gemini and pairs them with a curated city guide.

## Features

- **AI itinerary generator:** builds a day-by-day plan from city, trip length, budget, interests, travel style, currency and month, using `gemini-1.5-flash`. Itineraries can be exported as PDF.
- **Expert curated tours:** hand-picked tours grouped by continent.
- **City tourist guide:** looks up attractions, restaurants, emergency contacts and travel tips from a JSON knowledge base covering six continents.

## Stack

Python · Streamlit · Google Generative AI (Gemini) · geopy · FPDF

## Run locally

```bash
pip install -r requirements.txt
echo "GOOGLE_API_KEY=your-key" > .env
streamlit run app.py
```

## Structure

```
app.py            Streamlit UI and Gemini itinerary generation
city_guide.py     Knowledge-base loader and city lookup
tours_dataset.py  Curated tours by continent
knowledge_base/   City data per continent (JSON)
```
