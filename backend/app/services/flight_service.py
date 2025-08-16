import os
import requests
from datetime import datetime, date
import logging
from fastapi import HTTPException
from typing import Dict, List
from app.models import FlightRequest, FlightOption, FlightSegment
from app.utils import format_time

# Initialize logger
logger = logging.getLogger(__name__)

def search_flights_service(request: FlightRequest):
    try:
        outbound = datetime.strptime(request.outbound_date, "%Y-%m-%d").date()
        return_date = datetime.strptime(request.return_date, "%Y-%m-%d").date()
        if outbound < date.today():
            raise HTTPException(400, "Departure date must be in future")
        if return_date <= outbound:
            raise HTTPException(400, "Return date must be after departure")

        # Search outbound flights
        outbound_params = {
            "engine": "google_flights",
            "departure_id": request.origin.upper(),
            "arrival_id": request.destination.upper(),
            "outbound_date": request.outbound_date,
            "return_date": request.return_date,
            "currency": "INR",
            "hl": "en",
            "api_key": os.getenv("SERPAPI_API_KEY")
        }
        
        if request.nonstop:
            outbound_params["num"] = 0
        if request.cabin_class != "economy":
            outbound_params["cabin_class"] = request.cabin_class

        outbound_res = requests.get("https://serpapi.com/search", params=outbound_params)
        outbound_data = outbound_res.json()

        flight_options = {"outbound": [], "return": []}

        # Process outbound flights
        for flight in outbound_data.get("best_flights", []):
            segments = []
            for segment in flight.get("flights", []):
                segments.append(FlightSegment(
                    airline=segment.get("airline", "Unknown"),
                    flight_number=segment.get("flight_number", "N/A"),
                    departure_airport=segment.get("departure_airport", {}).get("name", "N/A"),
                    departure_terminal=segment.get("departure_airport", {}).get("terminal"),
                    departure_time=format_time(segment.get("departure_airport", {}).get("time")),
                    arrival_airport=segment.get("arrival_airport", {}).get("name", "N/A"),
                    arrival_terminal=segment.get("arrival_airport", {}).get("terminal"),
                    arrival_time=format_time(segment.get("arrival_airport", {}).get("time")),
                    duration=int(segment.get("duration", 0)),
                    aircraft=segment.get("aircraft", "Unknown"),
                    baggage=segment.get("baggage", "1 x 15kg"),
                    cabin_class=request.cabin_class,
                    amenities=["entertainment"] if request.cabin_class != "economy" else []
                ))

            flight_options["outbound"].append(FlightOption(
                total_price=f"₹{flight.get('price', 'N/A')}",
                total_duration=int(flight.get("total_duration", 0)),
                stops=len(segments) - 1,
                segments=segments,
                booking_link=flight.get("travel_ads", [{}])[0].get("link", "#"),
                fare_rules={
                    "cancellation": "Free within 24h",
                    "baggage": "1 checked + 1 cabin"
                }
            ))

        # Search return flights if requested
        if request.search_return:
            return_params = {
                "engine": "google_flights",
                "departure_id": request.destination.upper(),
                "arrival_id": request.origin.upper(),
                "outbound_date": request.return_date,
                "currency": "INR",
                "hl": "en",
                "api_key": os.getenv("SERPAPI_API_KEY")
            }
            
            if request.nonstop:
                return_params["num"] = 0
            if request.cabin_class != "economy":
                return_params["cabin_class"] = request.cabin_class

            return_res = requests.get("https://serpapi.com/search", params=return_params)
            return_data = return_res.json()

            for flight in return_data.get("best_flights", []):
                segments = []
                for segment in flight.get("flights", []):
                    segments.append(FlightSegment(
                        airline=segment.get("airline", "Unknown"),
                        flight_number=segment.get("flight_number", "N/A"),
                        departure_airport=segment.get("departure_airport", {}).get("name", "N/A"),
                        departure_terminal=segment.get("departure_airport", {}).get("terminal"),
                        departure_time=format_time(segment.get("departure_airport", {}).get("time")),
                        arrival_airport=segment.get("arrival_airport", {}).get("name", "N/A"),
                        arrival_terminal=segment.get("arrival_airport", {}).get("terminal"),
                        arrival_time=format_time(segment.get("arrival_airport", {}).get("time")),
                        duration=int(segment.get("duration", 0)),
                        aircraft=segment.get("aircraft", "Unknown"),
                        baggage=segment.get("baggage", "1 x 15kg"),
                        cabin_class=request.cabin_class,
                        amenities=["entertainment"] if request.cabin_class != "economy" else []
                    ))

                flight_options["return"].append(FlightOption(
                    total_price=f"₹{flight.get('price', 'N/A')}",
                    total_duration=int(flight.get("total_duration", 0)),
                    stops=len(segments) - 1,
                    segments=segments,
                    booking_link=flight.get("travel_ads", [{}])[0].get("link", "#"),
                    fare_rules={
                        "cancellation": "Free within 24h",
                        "baggage": "1 checked + 1 cabin"
                    }
                ))

        return flight_options

    except Exception as e:
        logger.error(f"Flight search error: {str(e)}")
        raise HTTPException(500, "Flight search failed")