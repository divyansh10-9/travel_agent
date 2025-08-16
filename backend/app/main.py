# backend/app/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from typing import List, Optional, Dict, Any
import logging
import urllib.parse
from groq import Groq
import json
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, From, To, Subject, HtmlContent

# Import models and services
from app.models import (
    FlightRequest, HotelRequest, ItineraryRequest, EmailRequest,
    FlightSegment, FlightOption, TimeSlot, DailyPlan, GeneratedItinerary
)
from app.utils import format_time, calculate_time_slots, clean_hotel_data
from app.services import (
    flight_service,
    hotel_service,
    itinerary_service,
    email_service
)

# Initialize
load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Load API keys
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")
if not SERPAPI_KEY:
    raise ValueError("Missing SERPAPI_API_KEY")
if not GROQ_KEY:
    raise ValueError("Missing GROQ_API_KEY")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_KEY)

# Endpoints
@app.post("/search_flights", response_model=Dict[str, List[FlightOption]])
def search_flights(request: FlightRequest):
    return flight_service.search_flights_service(request)

@app.post("/search_hotels")
def search_hotels(request: HotelRequest):
    return hotel_service.search_hotels_service(request)

@app.post("/generate_itinerary", response_model=GeneratedItinerary)
def generate_itinerary(request: ItineraryRequest):
    return itinerary_service.generate_itinerary_service(request)

@app.post("/send_itinerary_email")
def send_itinerary_email(request: EmailRequest):
    return email_service.send_itinerary_email_service(request)

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}