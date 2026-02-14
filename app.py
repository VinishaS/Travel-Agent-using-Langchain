import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from amadeus import Client, ResponseError
from airport_codes import get_airport_code, AIRPORT_CODES, get_destination_currency, DESTINATION_CURRENCIES
import os
from datetime import datetime, timedelta

load_dotenv()

# Page setup
st.set_page_config(page_title="✈️ Travel Planner", page_icon="✈️", layout="wide", initial_sidebar_state="expanded")

# Custom CSS: polished editorial travel style
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700&family=Instrument+Serif:ital@0;1&display=swap" rel="stylesheet">
<style>
    :root {
        --ink: #1a1a1a;
        --ink-soft: #525252;
        --paper: #f6f4f0;
        --paper-warm: #ebe8e2;
        --accent: #0d9488;
        --accent-hover: #0f766e;
        --accent-glow: rgba(13, 148, 136, 0.2);
        --card: #ffffff;
        --border: #e0ddd6;
        --sidebar-bg: #181615;
        --sidebar-surface: rgba(255,255,255,0.06);
        --sidebar-text: #fafaf9;
        --sidebar-muted: #a8a29e;
    }
    
    /* Smooth base */
    .stApp {
        background: var(--paper);
        font-family: 'DM Sans', sans-serif;
        background-image: 
            radial-gradient(ellipse 120% 80% at 50% -20%, rgba(13, 148, 136, 0.06), transparent),
            linear-gradient(180deg, var(--paper) 0%, var(--paper-warm) 100%);
        min-height: 100vh;
    }
    
    .block-container {
        padding-top: 2rem;
        padding-bottom: 4rem;
        max-width: 720px;
    }
    
    /* Title: stronger presence */
    h1 {
        font-family: 'Instrument Serif', serif !important;
        font-weight: 400 !important;
        color: var(--ink) !important;
        font-size: 3rem !important;
        letter-spacing: -0.04em;
        margin-bottom: 0.35rem !important;
        line-height: 1.15 !important;
    }
    
    .main h1 {
        padding-bottom: 0.6rem;
        border-bottom: 3px solid var(--accent);
        display: inline-block;
        box-shadow: 0 3px 0 0 var(--accent-glow);
    }
    
    .main [data-testid="stCaption"] {
        color: var(--ink-soft) !important;
        font-size: 1rem !important;
        margin-top: 0.6rem !important;
        max-width: 32ch;
    }
    
    /* Sidebar: refined dark panel */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--sidebar-bg) 0%, #1f1c1a 100%);
        box-shadow: 4px 0 32px rgba(0,0,0,0.15);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }
    
    [data-testid="stSidebar"] .stMarkdown { color: var(--sidebar-text) !important; }
    [data-testid="stSidebar"] h2 {
        font-family: 'Instrument Serif', serif !important;
        color: var(--sidebar-text) !important;
        font-weight: 400 !important;
        font-size: 1.5rem !important;
        margin-bottom: 1.25rem !important;
        letter-spacing: -0.02em;
    }
    
    [data-testid="stSidebar"] .section-label {
        font-size: 0.68rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: var(--accent) !important;
        margin-bottom: 0.6rem !important;
        margin-top: 1.25rem !important;
        display: block;
    }
    
    [data-testid="stSidebar"] .section-label:first-of-type { margin-top: 0 !important; }
    
    [data-testid="stSidebar"] label {
        color: var(--sidebar-text) !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stSelectbox > div,
    [data-testid="stSidebar"] .stDateInput > div {
        background: var(--sidebar-surface) !important;
        color: var(--sidebar-text) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 10px !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input:focus,
    [data-testid="stSidebar"] .stSelectbox > div:focus-within,
    [data-testid="stSidebar"] .stDateInput > div:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 2px var(--accent-glow) !important;
    }
    
    [data-testid="stSidebar"] .stTextInput input::placeholder {
        color: var(--sidebar-muted);
    }
    
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] .stCaption {
        color: var(--sidebar-muted) !important;
        font-size: 0.85rem !important;
    }
    
    [data-testid="stSidebar"] button {
        font-weight: 600 !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
    }
    
    [data-testid="stSidebar"] button:first-of-type {
        background: linear-gradient(180deg, var(--accent) 0%, var(--accent-hover) 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(13, 148, 136, 0.4);
    }
    [data-testid="stSidebar"] button:first-of-type:hover {
        box-shadow: 0 6px 20px rgba(13, 148, 136, 0.5);
        transform: translateY(-1px);
    }
    
    [data-testid="stSidebar"] button:last-of-type {
        background: transparent !important;
        color: var(--sidebar-muted) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    [data-testid="stSidebar"] button:last-of-type:hover {
        background: rgba(255,255,255,0.08) !important;
        color: var(--sidebar-text) !important;
        border-color: rgba(255,255,255,0.3) !important;
    }
    
    /* Chat: elevated cards */
    [data-testid="stChatMessage"] {
        background: var(--card) !important;
        border-radius: 14px !important;
        padding: 1.4rem 1.6rem !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.04);
        border: 1px solid var(--border) !important;
        margin-bottom: 1.1rem !important;
        transition: box-shadow 0.2s ease !important;
    }
    
    [data-testid="stChatMessage"]:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04) !important;
    }
    
    [data-testid="stChatMessage"] [data-testid="stMarkdown"] {
        font-size: 1rem !important;
        line-height: 1.7 !important;
        color: var(--ink) !important;
    }
    
    /* Itinerary markdown: headings & lists */
    [data-testid="stChatMessage"] [data-testid="stMarkdown"] h2,
    [data-testid="stChatMessage"] [data-testid="stMarkdown"] h3 {
        font-family: 'Instrument Serif', serif !important;
        color: var(--ink) !important;
        margin-top: 1.25em !important;
        margin-bottom: 0.4em !important;
        font-weight: 400 !important;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdown"] h2 { font-size: 1.35rem !important; }
    [data-testid="stChatMessage"] [data-testid="stMarkdown"] h3 { font-size: 1.15rem !important; }
    [data-testid="stChatMessage"] [data-testid="stMarkdown"] ul,
    [data-testid="stChatMessage"] [data-testid="stMarkdown"] ol {
        padding-left: 1.4em !important;
        margin: 0.5em 0 !important;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdown"] li { margin-bottom: 0.25em !important; }
    [data-testid="stChatMessage"] [data-testid="stMarkdown"] strong { color: var(--ink); font-weight: 600 !important; }
    
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        border-left: 4px solid var(--accent);
    }
    
    [data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
        border-left: 4px solid #64748b;
    }
    
    [data-testid="stChatInput"] {
        background: var(--card) !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06) !important;
        border: 1px solid var(--border) !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08), 0 0 0 2px var(--accent-glow) !important;
    }
    
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.1) !important; margin: 1rem 0 !important; }
    [data-testid="stSidebar"] .stCheckbox label { color: var(--sidebar-text) !important; }
    
    /* Intro box: subtle accent stripe */
    .intro-box {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 1.75rem 2rem;
        margin: 1.25rem 0 1.75rem 0;
        font-size: 1rem;
        line-height: 1.65;
        color: var(--ink-soft);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border-left: 4px solid var(--accent);
    }
    .intro-box strong { color: var(--ink); font-weight: 600 !important; }
    .intro-box ol { margin: 0.6rem 0 0 1.35rem; padding: 0; }
    .intro-box li { margin-bottom: 0.4rem; }
    
    /* Scrollbar */
    .stApp ::-webkit-scrollbar { width: 8px; height: 8px; }
    .stApp ::-webkit-scrollbar-track { background: var(--paper-warm); border-radius: 4px; }
    .stApp ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 4px; }
    .stApp ::-webkit-scrollbar-thumb:hover { background: var(--ink-soft); }
</style>
""", unsafe_allow_html=True)

st.title("Travel Itinerary Planner")

# Initialize Amadeus client
amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET")
)

# Initialize the LLM
llm = ChatOpenAI(model="gpt-4o")

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an expert travel planner. Create a day-by-day itinerary based on the user's preferences.

Include:
- Morning, afternoon, and evening activities
- Restaurant recommendations
- Estimated costs
- Practical tips

When flight and hotel data is provided, reference those specific options and prices.

Also generate a packing checklist based on the destination and activities.

Keep it realistic and well-paced. Don't over-schedule.

When the user asks follow-up questions, modify the existing itinerary accordingly."""),
    
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])

chain = prompt | llm

def search_flights(origin, destination, departure_date):
    """Search for flights using Amadeus API."""
    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=1,
            max=5
        )
        return response.data
    except ResponseError as e:
        return None

def search_hotels(city_code, check_in, check_out):
    """Search for hotels using Amadeus API."""
    try:
        hotels = amadeus.reference_data.locations.hotels.by_city.get(
            cityCode=city_code,
            radius=30,
            radiusUnit="KM"
        )
        
        if hotels.data:
            return hotels.data[:5]
        return None
    except ResponseError as e:
        return None

def format_flight_results(flights, dest_code):
    """Format flight results into readable text with local currency."""
    if not flights:
        return "Could not fetch flight data. Please check airport codes."
    
    # Get destination currency
    local_currency = get_destination_currency(dest_code)
    
    result = "### ✈️ Flight Options Found:\n\n"
    for i, flight in enumerate(flights[:5], 1):
        price = float(flight['price']['total'])
        currency = flight['price']['currency']
        segments = flight['itineraries'][0]['segments']
        
        departure = segments[0]['departure']['at']
        arrival = segments[-1]['arrival']['at']
        stops = len(segments) - 1
        
        # Show price in original currency
        result += f"**Option {i}:** {currency} {price:.2f}"
        
        # Note about local currency
        if currency != local_currency:
            result += f" *(local currency: {local_currency})*"
        
        result += f"\n- Departure: {departure[:16].replace('T', ' ')}\n"
        result += f"- Arrival: {arrival[:16].replace('T', ' ')}\n"
        result += f"- Stops: {stops if stops > 0 else 'Non-stop'}\n\n"
    
    return result

def format_hotel_results(hotels):
    """Format hotel results into readable text."""
    if not hotels:
        return "Could not fetch hotel data."
    
    result = "### 🏨 Hotel Options:\n\n"
    for i, hotel in enumerate(hotels[:5], 1):
        name = hotel.get('name', 'Unknown Hotel')
        result += f"**{i}. {name}**\n"
    
    return result

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "trip_planned" not in st.session_state:
    st.session_state.trip_planned = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "flight_data" not in st.session_state:
    st.session_state.flight_data = ""

if "hotel_data" not in st.session_state:
    st.session_state.hotel_data = ""

# Sidebar for trip details
with st.sidebar:
    st.header("Trip details")
    
    st.markdown('<span class="section-label">Route</span>', unsafe_allow_html=True)
    origin = st.text_input("Flying from", placeholder="e.g., New York")
    destination = st.text_input("Destination", placeholder="e.g., Tokyo")
    
    if origin:
        origin_code = get_airport_code(origin)
        st.caption(f"Airport: {origin_code}" if origin_code else "Airport not found")
    if destination:
        dest_code = get_airport_code(destination)
        st.caption(f"Airport: {dest_code}" if dest_code else "Airport not found")
    
    st.markdown('<span class="section-label">Dates</span>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        departure_date = st.date_input("Departure", min_value=datetime.now().date())
    with col2:
        return_date = st.date_input("Return", min_value=datetime.now().date() + timedelta(days=1))
    
    days = (return_date - departure_date).days
    st.caption(f"Duration: **{days} days**")
    
    st.markdown('<span class="section-label">Preferences</span>', unsafe_allow_html=True)
    budget = st.selectbox("Budget", ["budget", "moderate", "luxury"])
    interests = st.text_input("Interests", placeholder="e.g., food, history, nature")
    
    st.markdown('<span class="section-label">Search options</span>', unsafe_allow_html=True)
    search_flights_option = st.checkbox("Search real flights", value=True)
    search_hotels_option = st.checkbox("Search real hotels", value=True)
    
    st.markdown('<span class="section-label">Actions</span>', unsafe_allow_html=True)
    if st.button("Plan my trip", use_container_width=True):
        if origin and destination:
            st.session_state.trip_planned = True
            st.session_state.chat_history = []
            st.session_state.messages = []
            st.session_state.flight_data = ""
            st.session_state.hotel_data = ""
            
            # Get airport codes
            origin_code = get_airport_code(origin)
            dest_code = get_airport_code(destination)
            
            # Search for flights
            if search_flights_option and origin_code and dest_code:
                with st.spinner("Searching flights..."):
                    flights = search_flights(
                        origin_code, 
                        dest_code, 
                        departure_date.strftime("%Y-%m-%d")
                    )
                    st.session_state.flight_data = format_flight_results(flights, dest_code)
            elif search_flights_option:
                st.session_state.flight_data = f"⚠️ Airport codes not found for {origin} or {destination}."
            
            # Search for hotels
            if search_hotels_option and dest_code:
                with st.spinner("Searching hotels..."):
                    hotels = search_hotels(
                        dest_code,
                        departure_date.strftime("%Y-%m-%d"),
                        return_date.strftime("%Y-%m-%d")
                    )
                    st.session_state.hotel_data = format_hotel_results(hotels)
            
            # Create the initial message
            first_message = f"""Plan a trip for me:
- From: {origin}
- Destination: {destination}
- Dates: {departure_date} to {return_date} ({days} days)
- Budget: {budget}
- Interests: {interests}

{st.session_state.flight_data}

{st.session_state.hotel_data}

Please also include a packing checklist for this trip."""
            
            st.session_state.messages.append({"role": "user", "content": first_message})
        else:
            st.warning("Please fill in origin, and destination!")
    
    st.divider()
    if st.button("Start over", use_container_width=True):
        st.session_state.trip_planned = False
        st.session_state.chat_history = []
        st.session_state.messages = []
        st.rerun()

# Clear intro: show "How it works" when no messages yet
if not st.session_state.messages:
    st.markdown("""
    <div class="intro-box">
        <strong>How it works</strong>
        <ol>
            <li>Fill in <strong>route</strong>, <strong>dates</strong>, and <strong>interests</strong> in the sidebar.</li>
            <li>Click <strong>Plan my trip</strong> — we search real flights and hotels, then AI builds your itinerary.</li>
            <li>Use the chat below to refine (e.g. &ldquo;Add more food spots&rdquo; or &ldquo;What should I pack?&rdquo;).</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Generate response for new trip
if st.session_state.trip_planned and len(st.session_state.messages) == 1:
    with st.chat_message("assistant"):
        with st.spinner("✨ Planning your perfect trip..."):
            response = chain.invoke({
                "chat_history": st.session_state.chat_history,
                "input": st.session_state.messages[0]["content"]
            })
            st.markdown(response.content)
            
            # Save to history
            st.session_state.messages.append({"role": "assistant", "content": response.content})
            st.session_state.chat_history.append(HumanMessage(content=st.session_state.messages[0]["content"]))
            st.session_state.chat_history.append(AIMessage(content=response.content))

# Chat input for follow-ups
if st.session_state.trip_planned and len(st.session_state.messages) > 1:
    if user_input := st.chat_input("Ask a follow-up (e.g., 'Add more food spots' or 'What should I pack for rain?')"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chain.invoke({
                    "chat_history": st.session_state.chat_history,
                    "input": user_input
                })
                st.markdown(response.content)
                
                # Save to history
                st.session_state.messages.append({"role": "assistant", "content": response.content})
                st.session_state.chat_history.append(HumanMessage(content=user_input))
                st.session_state.chat_history.append(AIMessage(content=response.content))