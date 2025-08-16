# backend/app/models.py
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class FlightRequest(BaseModel):
    origin: str
    destination: str
    outbound_date: str
    return_date: str
    cabin_class: str = "economy"
    nonstop: bool = False
    search_return: bool = False

class HotelRequest(BaseModel):
    location: str
    check_in_date: str
    check_out_date: str
    stars: Optional[int] = None

class ItineraryRequest(BaseModel):
    destination: str
    duration: int
    interests: List[str]
    budget: str
    travel_style: str
    arrival_time: Optional[str] = None

class EmailRequest(BaseModel):
    email: str
    itinerary: Dict[str, Any]
    personal_message: Optional[str] = None

class FlightSegment(BaseModel):
    airline: str
    flight_number: str
    departure_airport: str
    departure_terminal: Optional[str]
    departure_time: str
    arrival_airport: str
    arrival_terminal: Optional[str]
    arrival_time: str
    duration: int
    aircraft: str
    baggage: str
    cabin_class: str
    amenities: List[str]

class FlightOption(BaseModel):
    total_price: str
    total_duration: int
    stops: int
    segments: List[FlightSegment]
    booking_link: str
    fare_rules: Dict[str, str]

class TimeSlot(BaseModel):
    time: str
    activities: List[str]

class DailyPlan(BaseModel):
    day: int
    date: str
    time_slots: Dict[str, TimeSlot]
    highlights: List[str]
    arrival_info: Optional[str] = None

class GeneratedItinerary(BaseModel):
    summary: str
    daily_plans: List[DailyPlan]
    packing_list: List[str]
    local_tips: List[str]
    destination: str