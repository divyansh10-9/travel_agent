import os
import json
import logging
from groq import Groq
from fastapi import HTTPException
from app.utils import calculate_time_slots

# Initialize logger
logger = logging.getLogger(__name__)

def generate_itinerary_service(request):
    try:
        groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Get available models
        available_models = [model.id for model in groq_client.models.list().data]
        logger.info(f"Available Groq models: {available_models}")
        
        # Calculate time slots based on arrival
        time_slots = calculate_time_slots(request.arrival_time) if request.arrival_time else {
            "morning": "9:00 AM - 12:00 PM",
            "afternoon": "1:00 PM - 5:00 PM",
            "evening": "6:00 PM - 10:00 PM"
        }

        prompt = f"""Create a detailed {request.duration}-day travel itinerary for {request.destination}.
        Travel style: {request.travel_style}
        Budget: {request.budget}
        Interests: {', '.join(request.interests)}
        Flight arrives at: {request.arrival_time or 'morning'}

        For Day 1, use these time slots:
        Morning: {time_slots['morning']} (after arrival activities)
        Afternoon: {time_slots['afternoon']} (main activities)
        Evening: {time_slots['evening']} (dinner/relaxation)

        Return JSON with these exact fields:
        {{
            "summary": "brief overview",
            "daily_plans": [
                {{
                    "day": 1,
                    "date": "Day 1",
                    "time_slots": {{
                        "morning": {{
                            "time": "{time_slots['morning']}",
                            "activities": ["light activity after arrival"]
                        }},
                        "afternoon": {{
                            "time": "{time_slots['afternoon']}",
                            "activities": ["main activity"]
                        }},
                        "evening": {{
                            "time": "{time_slots['evening']}",
                            "activities": ["dinner","relax"]
                        }}
                    }},
                    "highlights": ["key attractions"]
                }}
            ],
            "packing_list": ["essential items"],
            "local_tips": ["useful advice"]
        }}"""
        
        # Try preferred models in order
        preferred_models = [
            "mixtral-8x7b-32768",
            "llama3-70b-8192",
            "llama3-8b-8192",
            "gemma-7b-it"
        ]
        
        last_error = None
        
        for model in preferred_models:
            if model not in available_models:
                continue
                
            try:
                response = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model=model,
                    response_format={"type": "json_object"},
                    temperature=0.7
                )
                
                if response.choices and response.choices[0].message.content:
                    itinerary = json.loads(response.choices[0].message.content)
                    itinerary["destination"] = request.destination
                    return itinerary
                    
            except Exception as e:
                last_error = e
                logger.warning(f"Model {model} failed: {str(e)}")
                continue
        
        raise Exception(f"No working model found. Last error: {str(last_error)}")

    except Exception as e:
        logger.error(f"Itinerary generation error: {str(e)}")
        raise HTTPException(500, f"Itinerary generation failed: {str(e)}")