import streamlit as st
import re
import json
import dateparser
from datetime import datetime, timedelta
from transformers import pipeline
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz

# Initialize NER model
@st.cache_resource
def load_ner_model():
    try:
        return pipeline("ner", model="faraday001/scheduler_bot")
    except Exception as e:
        st.error(f"Error loading the model: {e}")
        return None

ner_model = load_ner_model()

# Initialize geolocator and timezone finder
geolocator = Nominatim(user_agent="meeting_scheduler_bot")
tz_finder = TimezoneFinder()

def get_timezone(country, state, city):
    location = geolocator.geocode(f"{city}, {state}, {country}")
    if location:
        timezone_str = tz_finder.timezone_at(lng=location.longitude, lat=location.latitude)
        return timezone_str if timezone_str else "UTC"
    return "UTC"

def to_datetime(date_str, time_str, timezone_str):
    local_tz = pytz.timezone(timezone_str)
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    return local_tz.localize(dt)

def parse_time(time_str):
    time_str = time_str.lower().replace(" ", "")
    if "pm" in time_str and not time_str.startswith("12"):
        hour = int(time_str.split("pm")[0]) + 12
        return f"{hour:02d}:00"
    elif "am" in time_str:
        hour = int(time_str.split("am")[0])
        if hour == 12:
            hour = 0
        return f"{hour:02d}:00"
    else:
        return f"{int(time_str):02d}:00"

def parse_schedule_request(request):
    participants = []
    requested_date = None
    start_time = None
    end_time = None

    date_pattern = r"(\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:January|February|March|April|May|June|July|August|September|October|November|December))"
    time_pattern = r"(\d{1,2}\s*[apAP][mM])"
    duration_pattern = r"(\d+)\s*hours?|([1-2]?[0-9]:[0-5][0-9])"

    date_match = re.search(date_pattern, request)
    time_matches = re.findall(time_pattern, request)
    duration_match = re.search(duration_pattern, request)

    if date_match:
        requested_date = dateparser.parse(date_match.group(0), settings={'PREFER_DATES_FROM': 'future'}).strftime("%Y-%m-%d")

    if time_matches:
        start_time = parse_time(time_matches[0][0])
        if len(time_matches) > 1:
            end_time = parse_time(time_matches[1][0])

    if not requested_date:
        parsed_datetime = dateparser.parse(request, settings={'PREFER_DATES_FROM': 'future', 'RELATIVE_BASE': datetime.now()})
        if parsed_datetime:
            requested_date = parsed_datetime.strftime("%Y-%m-%d")
            if parsed_datetime.time() != datetime.min.time():
                start_time = parsed_datetime.strftime("%H:%M")

    if 'in' in request.lower() and 'hour' in request.lower():
        hours = int(re.findall(r'\d+', request)[0]) if re.findall(r'\d+', request) else 0
        future_time = datetime.now() + timedelta(hours=hours)
        requested_date = future_time.strftime("%Y-%m-%d")
        start_time = future_time.strftime("%H:%M")

    if 'noon' in request.lower() and not start_time:
        start_time = "12:00"
    elif 'afternoon' in request.lower() and not start_time:
        start_time = "15:00"
    elif 'evening' in request.lower() and not start_time:
        start_time = "18:00"

    if 'next' in request.lower() and any(day in request.lower() for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']):
        day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        today = datetime.today()
        target_day = next(day for day in day_names if day in request.lower())
        target_index = day_names.index(target_day)
        days_ahead = (target_index - today.weekday() + 7) % 7 or 7
        requested_date = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")

    if 'tomorrow' in request.lower() and not requested_date:
        requested_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    elif 'today' in request.lower() and not requested_date:
        requested_date = datetime.now().strftime("%Y-%m-%d")

    if duration_match:
        if duration_match.group(1):
            hours = int(duration_match.group(1))
            if start_time:
                start_dt = datetime.strptime(f"{requested_date} {start_time}", "%Y-%m-%d %H:%M")
                end_time = (start_dt + timedelta(hours=hours)).strftime("%H:%M")
        elif duration_match.group(2):
            end_time = parse_time(duration_match.group(2))

    entities = ner_model(request)
    for ent in entities:
        if ent['entity'] in ['B-PER', 'I-PER']:
            participants.append(ent['word'])

    return participants, requested_date, start_time, end_time

# Streamlit user interface
st.title("Meeting Scheduler Bot")

st.text("Note: There are only 3 candidates' calendars available [Alice, Bob, Jane]. You are \none of them and can schedule a meeting with either of the two or both:")
user_request = st.text_area("Describe your meeting request", height=150)

# Initialize session state for location fields
if 'country' not in st.session_state:
    st.session_state.country = ""
if 'state' not in st.session_state:
    st.session_state.state = ""
if 'city' not in st.session_state:
    st.session_state.city = ""

# Show location input fields only after a request is made
if user_request:
    st.session_state.country = st.text_input("Country", st.session_state.country)
    st.session_state.state = st.text_input("State", st.session_state.state)
    st.session_state.city = st.text_input("City", st.session_state.city)

    if st.button("Schedule Meeting"):
        participants, requested_date, start_time, end_time = parse_schedule_request(user_request)

        if participants and requested_date and start_time and end_time:
            # Only fetch timezone if country, state, and city are provided
            if st.session_state.country and st.session_state.state and st.session_state.city:
                timezone = get_timezone(st.session_state.country, st.session_state.state, st.session_state.city)
                st.write(f"Meeting scheduled with {participants} on {requested_date} from {start_time} to {end_time} in {timezone} timezone.")
            else:
                st.error("Please provide your location (country, state, and city).")
        else:
            st.error("Could not schedule the meeting. Please provide more details.")
