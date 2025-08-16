# backend/app/utils.py
from typing import Dict
from datetime import datetime
import urllib.parse
import logging

logger = logging.getLogger(__name__)

def format_time(time_str: str) -> str:
    try:
        return datetime.strptime(time_str, "%H:%M").strftime("%I:%M %p")
    except:
        return time_str or "N/A"

def calculate_time_slots(arrival_time: str) -> Dict[str, str]:
    try:
        arrival = datetime.strptime(arrival_time, "%I:%M %p")
        if arrival.hour < 9:
            return {
                "morning": "9:00 AM - 12:00 PM",
                "afternoon": "1:00 PM - 5:00 PM",
                "evening": "6:00 PM - 10:00 PM"
            }
        elif arrival.hour < 13:
            return {
                "morning": f"{arrival.strftime('%I:%M %p')} - 12:00 PM",
                "afternoon": "1:00 PM - 5:00 PM",
                "evening": "6:00 PM - 10:00 PM"
            }
        elif arrival.hour < 18:
            return {
                "morning": "Already traveling",
                "afternoon": f"{arrival.strftime('%I:%M %p')} - 5:00 PM",
                "evening": "6:00 PM - 10:00 PM"
            }
        else:
            return {
                "morning": "Already traveling",
                "afternoon": "Already traveling",
                "evening": f"{arrival.strftime('%I:%M %p')} - 10:00 PM"
            }
    except:
        return {
            "morning": "9:00 AM - 12:00 PM",
            "afternoon": "1:00 PM - 5:00 PM",
            "evening": "6:00 PM - 10:00 PM"
        }

def clean_hotel_data(hotel: dict, location: str) -> dict:
    raw_rating = (
        hotel.get("rating")
        or hotel.get("review_score")
        or hotel.get("stars")
        or hotel.get("user_rating")
        or None
    )
    
    if raw_rating is not None:
        try:
            rating = float(raw_rating)
            rating = f"{rating:.1f}" if 0 <= rating <= 5 else "Not rated"
        except (ValueError, TypeError):
            rating = "Not rated"
    else:
        rating = "Not rated"
    
    address = (
        hotel.get("address", "").strip()
        or hotel.get("location", "").strip()
        or hotel.get("full_address", "").strip()
        or f"Near {location}"
    )
    
    photos = [
        p for p in hotel.get("photos", [])
        if isinstance(p, str) and p.startswith(('http://', 'https://'))
    ][:3]
    
    price = str(hotel.get("rate_per_night", {}).get("lowest", "N/A"))
    price = price.replace("₹", "").strip()
    
    return {
        "name": hotel.get("name", "Unknown Hotel").strip(),
        "price": price,
        "rating": rating,
        "stars": int(hotel.get("stars", 0)),
        "address": address,
        "photos": photos,
        "amenities": hotel.get("amenities", ["WiFi", "Pool", "AC"])[:5],
        "maps_link": f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(f'{hotel.get("name")} {address}')}",
        "check_in": hotel.get("check_in_date"),
        "check_out": hotel.get("check_out_date")
    }