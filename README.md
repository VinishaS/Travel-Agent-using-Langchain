#  Travel Agent using LangChain

An AI-powered travel planning assistant that creates personalized day-by-day itineraries with real flight prices, hotel recommendations, and packing checklists.

## 🌟 Features

- **AI-Powered Itineraries** — GPT-4o creates detailed day-by-day travel plans based on your preferences
- **Real Flight Data** — Live flight prices and schedules from Amadeus API
- **Hotel Recommendations** — Find real hotels at your destination
- **Smart Packing Lists** — AI generates a custom packing checklist based on your destination and activities
- **Conversational Memory** — Ask follow-up questions like "Add more food spots to Day 2"
- **Multi-Currency Support** — See prices in destination's local currency
- **350+ Airports** — Covers all major international airports worldwide

## 🚀 Live Demo

[**Try the app here**](https://your-username-travel-agent-using-langchain.streamlit.app)

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **AI/LLM:** LangChain + OpenAI GPT-4o
- **Flight & Hotel Data:** Amadeus API
- **Language:** Python 3.9+

## 🏃‍♂️ Run Locally

### Prerequisites

- Python 3.9+
- OpenAI API key
- Amadeus API key (free tier available)

## Run Locally

1. Clone the repo
2. Install dependencies: `pip install -r requirements.txt`
3. Create a `.env` file with your API keys:
```
   OPENAI_API_KEY=your-key
   AMADEUS_API_KEY=your-key
   AMADEUS_API_SECRET=your-secret
```
4. Run: 
   `streamlit run app.py`
   

## Getting API Keys

### OpenAI API Key
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new key

### Amadeus API Key (Free)
1. Go to [developers.amadeus.com](https://developers.amadeus.com)
2. Sign up for a free account
3. Create a new app in your dashboard
4. Copy your API Key and API Secret

**Made with ❤️ by Vinisha**
