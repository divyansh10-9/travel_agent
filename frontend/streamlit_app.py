# frontend/streamlit_app.py
import streamlit as st
import requests
import os
import json
from datetime import date, timedelta

# Config
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://127.0.0.1:8000")
MIN_DATE = date.today()

# Session State
if "selected_flight" not in st.session_state:
    st.session_state.selected_flight = {"outbound": None, "return": None}
if "selected_hotel" not in st.session_state:
    st.session_state.selected_hotel = None
if "flights" not in st.session_state:
    st.session_state.flights = {"outbound": [], "return": []}
if "hotels" not in st.session_state:
    st.session_state.hotels = []
if "itinerary" not in st.session_state:
    st.session_state.itinerary = None

# UI Setup
st.set_page_config(page_title="Travel Planner Pro", page_icon="✈️", layout="wide")
st.title("✈️ AI Travel Planner Pro")

# Flight Search Section
st.header("Step 1: Find Flights")
with st.form("flight_form"):
    col1, col2 = st.columns(2)
    with col1:
        origin = st.text_input("From (Airport Code)", value="DEL", max_chars=3).upper()
    with col2:
        destination = st.text_input("To (Airport Code)", value="MAA", max_chars=3).upper()

    col3, col4 = st.columns(2)
    with col3:
        outbound_date = st.date_input("Departure", min_value=MIN_DATE, value=MIN_DATE + timedelta(days=7))
    with col4:
        return_date = st.date_input("Return", min_value=outbound_date + timedelta(days=1), value=outbound_date + timedelta(days=7))

    col5, col6 = st.columns(2)
    with col5:
        cabin_class = st.selectbox("Class", ["economy", "premium", "business", "first"], index=0)
    with col6:
        nonstop = st.checkbox("Direct flights only", False)

    search_return = st.checkbox("Search return flights separately", False)

    if st.form_submit_button("Search Flights", type="primary"):
        payload = {
            "origin": origin,
            "destination": destination,
            "outbound_date": outbound_date.strftime("%Y-%m-%d"),
            "return_date": return_date.strftime("%Y-%m-%d"),
            "cabin_class": cabin_class,
            "nonstop": nonstop,
            "search_return": search_return
        }
        with st.spinner("Finding best flights..."):
            try:
                res = requests.post(f"{FASTAPI_URL}/search_flights", json=payload)
                if res.status_code == 200:
                    st.session_state.flights = res.json()
                    st.success(f"Found {len(st.session_state.flights['outbound'])} outbound options" + 
                              (f" and {len(st.session_state.flights['return'])} return options" if search_return else ""))
                else:
                    st.error(res.json().get("detail", "Flight search failed"))
            except Exception as e:
                st.error(f"Error: {str(e)}")

# Display Outbound Flights
if st.session_state.flights["outbound"]:
    st.subheader("Outbound Flights")
    for i, flight in enumerate(st.session_state.flights["outbound"]):
        with st.expander(
            f"✈️ Flight {i+1} | {flight['total_price']} | "
            f"{flight['total_duration']//60}h {flight['total_duration']%60}m | "
            f"{flight['stops']} stop{'s' if flight['stops'] != 1 else ''}"
        ):
            tab1, tab2 = st.tabs(["Flight Details", "Fare Rules"])
            
            with tab1:
                for seg in flight["segments"]:
                    col7, col8 = st.columns(2)
                    with col7:
                        st.markdown(f"""
                        **{seg['airline']} {seg['flight_number']}**  
                        🛫 **Departure:** {seg['departure_time']}  
                        Terminal: {seg['departure_terminal'] or 'Unknown'}  
                        Airport: {seg['departure_airport']}  
                        """)
                    with col8:
                        st.markdown(f"""
                        **{seg['cabin_class'].title()} Class**  
                        🛬 **Arrival:** {seg['arrival_time']}  
                        Terminal: {seg['arrival_terminal'] or 'Unknown'}  
                        Airport: {seg['arrival_airport']}  
                        """)
                    
                    st.markdown(f"""
                    ✈️ **Aircraft:** {seg['aircraft']}  
                    🛄 **Baggage:** {seg['baggage']}  
                    ⏱️ **Duration:** {seg['duration']} minutes  
                    """)
                    st.divider()
            
            with tab2:
                st.write("📜 **Fare Conditions**")
                for rule, desc in flight["fare_rules"].items():
                    st.write(f"- **{rule.title()}:** {desc}")
                
                st.link_button("Book This Flight", flight["booking_link"])
            
            if st.button(f"Select Outbound Flight {i+1}", key=f"outbound_{i}"):
                st.session_state.selected_flight["outbound"] = flight
                st.success("Outbound flight selected!")

# Display Return Flights if searched
if search_return and st.session_state.flights["return"]:
    st.subheader("Return Flights")
    for i, flight in enumerate(st.session_state.flights["return"]):
        with st.expander(
            f"✈️ Flight {i+1} | {flight['total_price']} | "
            f"{flight['total_duration']//60}h {flight['total_duration']%60}m | "
            f"{flight['stops']} stop{'s' if flight['stops'] != 1 else ''}"
        ):
            tab1, tab2 = st.tabs(["Flight Details", "Fare Rules"])
            
            with tab1:
                for seg in flight["segments"]:
                    col7, col8 = st.columns(2)
                    with col7:
                        st.markdown(f"""
                        **{seg['airline']} {seg['flight_number']}**  
                        🛫 **Departure:** {seg['departure_time']}  
                        Terminal: {seg['departure_terminal'] or 'Unknown'}  
                        Airport: {seg['departure_airport']}  
                        """)
                    with col8:
                        st.markdown(f"""
                        **{seg['cabin_class'].title()} Class**  
                        🛬 **Arrival:** {seg['arrival_time']}  
                        Terminal: {seg['arrival_terminal'] or 'Unknown'}  
                        Airport: {seg['arrival_airport']}  
                        """)
                    
                    st.markdown(f"""
                    ✈️ **Aircraft:** {seg['aircraft']}  
                    🛄 **Baggage:** {seg['baggage']}  
                    ⏱️ **Duration:** {seg['duration']} minutes  
                    """)
                    st.divider()
            
            with tab2:
                st.write("📜 **Fare Conditions**")
                for rule, desc in flight["fare_rules"].items():
                    st.write(f"- **{rule.title()}:** {desc}")
                
                st.link_button("Book This Flight", flight["booking_link"])
            
            if st.button(f"Select Return Flight {i+1}", key=f"return_{i}"):
                st.session_state.selected_flight["return"] = flight
                st.success("Return flight selected!")

# Hotel Search Section
if st.session_state.selected_flight["outbound"]:
    st.header("Step 2: Find Hotels")
    with st.form("hotel_form"):
        location = st.text_input("City", value=destination)
        col9, col10 = st.columns(2)
        with col9:
            check_in = st.date_input("Check-in", value=outbound_date)
        with col10:
            check_out = st.date_input("Check-out", value=return_date)
        
        stars = st.slider("Minimum Stars", 1, 5, 3)
        
        if st.form_submit_button("Search Hotels", type="primary"):
            payload = {
                "location": location,
                "check_in_date": check_in.strftime("%Y-%m-%d"),
                "check_out_date": check_out.strftime("%Y-%m-%d"),
                "stars": stars
            }
            with st.spinner("Finding hotels..."):
                try:
                    res = requests.post(f"{FASTAPI_URL}/search_hotels", json=payload)
                    if res.status_code == 200:
                        st.session_state.hotels = res.json().get("hotels", [])
                        st.success(f"Found {len(st.session_state.hotels)} hotels!")
                    else:
                        st.error(res.json().get("detail", "Hotel search failed"))
                except Exception as e:
                    st.error(f"Error: {str(e)}")

# Display Hotels
if st.session_state.hotels:
    st.subheader("Available Hotels")
    cols = st.columns(2)
    for i, hotel in enumerate(st.session_state.hotels):
        with cols[i % 2].container(border=True):
            stars = hotel.get('stars', 0)
            st.markdown(f"### 🏨 {hotel['name']} {'⭐' * stars if stars > 0 else ''}")
            
            if hotel.get("photos") and len(hotel["photos"]) > 0:
                st.image(hotel["photos"][0], use_container_width=True)
            else:
                st.image("https://via.placeholder.com/400x300?text=No+Image", 
                        use_container_width=True)
            
            st.markdown(f"**💰 ₹{hotel['price']}/night**")
            
            rating = hotel.get('rating', '')
            if isinstance(rating, str) and rating.replace('.', '').isdigit():
                rating_num = float(rating)
                if 0 <= rating_num <= 5:
                    st.markdown(f"**⭐ Rating:** {rating_num:.1f}/5")
                else:
                    st.markdown("**⭐ Rating:** Not rated")
            elif isinstance(rating, (int, float)) and 0 <= rating <= 5:
                st.markdown(f"**⭐ Rating:** {float(rating):.1f}/5")
            else:
                st.markdown("**⭐ Rating:** Not rated")
            
            st.markdown(f"**📍 {hotel['address'] or 'Address not available'}**")
            
            if hotel.get("amenities"):
                st.write("**🛎️ Amenities:** " + ", ".join(hotel["amenities"][:5]))
            
            col11, col12 = st.columns(2)
            with col11:
                if hotel.get('maps_link'):
                    st.link_button("View on Map", hotel["maps_link"])
            with col12:
                if st.button(f"Select #{i+1}", key=f"hotel_{i}"):
                    st.session_state.selected_hotel = hotel
                    st.success("Hotel selected!")

# AI Itinerary Generation
if st.session_state.selected_flight["outbound"] and st.session_state.selected_hotel:
    st.header("🌟 AI-Powered Itinerary Generator")
    
    with st.expander("➕ Customize Your Itinerary", expanded=True):
        with st.form("preferences_form"):
            st.subheader("Tell us about your travel preferences")
            
            duration = (return_date - outbound_date).days
            arrival_time = st.session_state.selected_flight["outbound"]["segments"][-1]["arrival_time"]
            
            st.write(f"✈️ Your flight arrives at: {arrival_time}")
            
            interests = st.multiselect(
                "What are you interested in?",
                ["Sightseeing", "Food & Dining", "Adventure", "Shopping", 
                 "Culture & History", "Nature", "Relaxation", "Nightlife"],
                default=["Sightseeing", "Food & Dining"]
            )
            
            budget = st.selectbox(
                "Budget Level",
                ["Budget", "Mid-range", "Luxury"],
                index=1
            )
            
            travel_style = st.selectbox(
                "Travel Style",
                ["Fast-paced", "Balanced", "Relaxed"],
                index=1
            )
            
            if st.form_submit_button("Generate Smart Itinerary", type="primary"):
                payload = {
                    "destination": destination,
                    "duration": duration,
                    "interests": interests,
                    "budget": budget,
                    "travel_style": travel_style,
                    "arrival_time": arrival_time
                }
                
                with st.spinner("🧠 Creating your personalized itinerary..."):
                    try:
                        res = requests.post(f"{FASTAPI_URL}/generate_itinerary", json=payload)
                        if res.status_code == 200:
                            st.session_state.itinerary = res.json()
                            st.success("Itinerary generated!")
                        else:
                            st.error(res.json().get("detail", "Itinerary generation failed"))
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Display AI-generated itinerary
    if st.session_state.itinerary:
        itinerary = st.session_state.itinerary
        
        st.subheader("✈️ Your AI-Crafted Travel Plan")
        st.write(itinerary.get("summary", ""))
        
        # Flight and Hotel Cards
        with st.expander("🔍 Your Selections", expanded=False):
            col13, col14 = st.columns(2)
            with col13:
                st.subheader("Outbound Flight")
                flight = st.session_state.selected_flight["outbound"]
                st.write(f"**{flight['segments'][0]['departure_airport']} → {flight['segments'][-1]['arrival_airport']}**")
                st.write(f"**Departure:** {outbound_date.strftime('%a, %b %d')} at {flight['segments'][0]['departure_time']}")
                st.write(f"**Arrival:** {flight['segments'][-1]['arrival_time']}")
                st.write(f"**Price:** {flight['total_price']}")
                st.link_button("Manage Booking", flight["booking_link"])
            
            if st.session_state.selected_flight["return"]:
                with col14:
                    st.subheader("Return Flight")
                    return_flight = st.session_state.selected_flight["return"]
                    st.write(f"**{return_flight['segments'][0]['departure_airport']} → {return_flight['segments'][-1]['arrival_airport']}**")
                    st.write(f"**Departure:** {return_date.strftime('%a, %b %d')} at {return_flight['segments'][0]['departure_time']}")
                    st.write(f"**Arrival:** {return_flight['segments'][-1]['arrival_time']}")
                    st.write(f"**Price:** {return_flight['total_price']}")
                    st.link_button("Manage Booking", return_flight["booking_link"])
            else:
                with col14:
                    st.subheader("Hotel Details")
                    hotel = st.session_state.selected_hotel
                    st.write(f"**{hotel['name']}** ({'⭐' * hotel.get('stars', 0)})")
                    st.write(f"**Check-in:** {hotel['check_in']}")
                    st.write(f"**Check-out:** {hotel['check_out']}")
                    st.write(f"**Price:** ₹{hotel['price']}/night")
                    if hotel.get('maps_link'):
                        st.link_button("View Hotel", hotel["maps_link"])
        
        # Daily Plans
        st.subheader("📅 Daily Schedule")
        for day in itinerary.get("daily_plans", []):
            with st.expander(f"Day {day['day']}: {day.get('date', '')}", expanded=True):
                # Show flight arrival on Day 1
                if day['day'] == 1:
                    arrival = st.session_state.selected_flight["outbound"]["segments"][-1]
                    st.write(f"✈️ **Flight Arrival:** {arrival['arrival_time']} at {arrival['arrival_airport']}")
                
                # Show time slots
                for slot_name, slot in day.get("time_slots", {}).items():
                    with st.container(border=True):
                        st.subheader(f"{slot_name.title()} ({slot['time']})")
                        for activity in slot.get("activities", []):
                            st.write(f"⏰ {activity}")
                
                # Show highlights
                if day.get("highlights"):
                    st.write("🌟 **Top Highlights**")
                    for highlight in day["highlights"]:
                        st.write(f"- {highlight}")
        
        # Additional Information
        with st.expander("🧳 Packing List", expanded=False):
            for item in itinerary.get("packing_list", []):
                st.write(f"✅ {item}")
        
        with st.expander("💡 Local Tips", expanded=False):
            for tip in itinerary.get("local_tips", []):
                st.write(f"💡 {tip}")
        
        # Download Button
        itinerary_json = json.dumps(st.session_state.itinerary, indent=2)
        st.download_button(
            label="📥 Download Itinerary",
            data=itinerary_json,
            file_name=f"{destination}_itinerary.json",
            mime="application/json"
        )
        
        # Email Itinerary Section
        with st.expander("📧 Email This Itinerary", expanded=False):
            with st.form("email_form"):
                email = st.text_input("Enter your email address")
                customize = st.checkbox("Add personal message", False)
                message = ""
                
                if customize:
                    message = st.text_area("Personal message", "Looking forward to my trip!")
                
                if st.form_submit_button("Send Itinerary by Email", type="primary"):
                    if not email:
                        st.error("Please enter an email address")
                    else:
                        # Prepare itinerary with arrival info for Day 1
                        itinerary_data = st.session_state.itinerary.copy()
                        if itinerary_data.get("daily_plans"):
                            arrival_flight = st.session_state.selected_flight["outbound"]["segments"][-1]
                            itinerary_data["daily_plans"][0]["arrival_info"] = (
                                f"Flight arrives at {arrival_flight['arrival_time']} "
                                f"at {arrival_flight['arrival_airport']}"
                            )
                        
                        payload = {
                            "email": email,
                            "itinerary": itinerary_data,
                            "personal_message": message
                        }
                        
                        with st.spinner("Sending email..."):
                            try:
                                res = requests.post(f"{FASTAPI_URL}/send_itinerary_email", json=payload)
                                if res.status_code == 200:
                                    st.success("✉️ Itinerary sent successfully! Check your inbox.")
                                else:
                                    st.error(f"Failed to send email: {res.json().get('detail', 'Unknown error')}")
                            except Exception as e:
                                st.error(f"Error: {str(e)}")