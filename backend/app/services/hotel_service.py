import os
import requests
import urllib.parse
import logging
from fastapi import HTTPException
from typing import Dict
from app.utils import clean_hotel_data

# Initialize logger
logger = logging.getLogger(__name__)

def search_hotels_service(request):
    try:
        params = {
            "engine": "google_hotels",
            "q": request.location,
            "check_in_date": request.check_in_date,
            "check_out_date": request.check_out_date,
            "currency": "INR",
            "api_key": os.getenv("SERPAPI_API_KEY"),
            "hl": "en"
        }
        
        if request.stars:
            params["stars"] = request.stars

        res = requests.get("https://serpapi.com/search", params=params)
        data = res.json()

        hotels = [clean_hotel_data(h, request.location) for h in data.get("properties", [])]
        return {"hotels": hotels}

    except Exception as e:
        logger.error(f"Hotel search error: {str(e)}")
        raise HTTPException(500, "Hotel search failed")