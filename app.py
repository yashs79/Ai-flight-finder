import google.generativeai as genai
from dotenv import load_dotenv
import os
from flight_data_service import FlightDataService
import pandas as pd
import chainlit as cl
import asyncio
import logging
from datetime import datetime, timedelta
logging.basicConfig(level=logging.DEBUG)

load_dotenv()

# Configure Gemini
genai.configure(api_key="AIzaSyDM_a8Cp6_m9MFk_8H0e8xaBMbHbMK4tgs")

# Initialize the flight data service
flight_service = FlightDataService()
system_message="""
            You are a helpful technical flight support assistant. Your role is to assist users in finding flight details in a clear and easy-to-read format. When flight details are found, format the information in a readable table with the following columns:
            - FlightNumber
            - Origin
            - Destination
            - DepartureDate
            - DepartureTime
            - ArrivalDate
            - ArrivalTime
            - Price
            - Airline
            - Duration
            - Duration_min (in minutes)
            You should ensure that all the details are displayed properly, including correct formatting for time, dates, prices, and flight durations.
            Additionally, offer concise and helpful explanations or answers to any flight-related queries.
            Remember these are available flights:  ["Air India", "SpiceJet", "IndiGo", "Vistara", "GoAir", "AirAsia"]. Follow the flight names stricly. Do not make them uppercase or lowercase randomly.
            Remember these are available airports:  ["Bangalore", "Delhi", "Mumbai", "Chennai", "Kolkata", "Hyderabad", "Pune", "Jaipur"]. Follow the flight names stricly. Do not make them uppercase or lowercase randomly.
        """
from typing import List

async def GetFlightDetails(*, 
                     origin: List[str] = [], 
                     destination: List[str] = [], 
                     departure_date: List[str] = [], 
                     arrival_date: List[str] = [], 
                     price: List[float] = [], 
                     airline: List[str] = [], 
                     duration: List[int] = []) -> dict:
    """
    Get the details of a flight and show them in the form of table. This function processes user queries to extract flight details.

    Args:
        origin: A list of origin city/cities for the flight. For example: ['Kolkata']. If the user mentions additional origins, append them to the list (e.g., ['Kolkata', 'Delhi']). If the user has no preference, send an empty list ([]). Available airports are: ["Bangalore", "Delhi", "Mumbai", "Chennai", "Kolkata", "Hyderabad", "Pune", "Jaipur"]

        destination: A list of destination city/cities for the flight. For example: ['Chennai']. If the user mentions additional destinations, append them to the list (e.g., ['Chennai', 'Delhi']). If the user has no preference, send an empty list ([]). Available airports are: ["Bangalore", "Delhi", "Mumbai", "Chennai", "Kolkata", "Hyderabad", "Pune", "Jaipur"]

        departure_date: A list of departure dates in the format 'YYYY-MM-DD'. For example: ['2025-01-02']. If the user mentions additional dates, append them to the list (e.g., ['2025-01-02', '2025-03-21']). If the user has no preference, today's date will be used.

        arrival_date: A list of arrival dates in the format 'YYYY-MM-DD'. Not used in real-time search as we focus on departure dates.

        price: A list specifying price ranges for flights. Not used in real-time search as prices are dynamic.
            
        airline: A list of preferred airlines. For example: ['IndiGo']. If the user mentions additional airlines, append them to the list (e.g., ['Indigo', 'Air India']). If the user has no preference, send an empty list ([]). Available flights are: ["Air India", "SpiceJet", "IndiGo", "Vistara", "GoAir", "AirAsia"]

        duration: A list specifying flight durations in minutes. Not used in real-time search as durations are dynamic.
            
    Returns:
        dict: A dictionary containing all the flight details."""
    
    print(origin, destination, departure_date, arrival_date, price, airline, duration)
    
    # Use first origin and destination if provided, otherwise return empty
    origin_city = origin[0] if origin else None
    dest_city = destination[0] if destination else None
    
    # Use provided departure date or today's date
    search_date = departure_date[0] if departure_date else datetime.now().strftime('%Y-%m-%d')
    
    # Get real-time flight data
    flights = await flight_service.get_flights(
        origin=origin_city,
        destination=dest_city,
        departure_date=search_date
    )
    
    # Filter by airline if specified
    if airline:
        flights = [f for f in flights if f['Airline'] in airline]
    
    if not flights:
        return "No flight details found"
    
    data = pd.DataFrame(flights)
    print(data)
    
    return flights

async def CallGemini(query):
    try:
        import aiohttp
        import json
        from datetime import datetime
        
        # First try to get flight details
        try:
            # Extract date from query or use tomorrow's date
            if "tomorrow" in query.lower():
                date = (datetime.now().date() + timedelta(days=1)).strftime("%Y-%m-%d")
            else:
                date = datetime.now().date().strftime("%Y-%m-%d")
            
            # Extract filters from query
            query_lower = query.lower()
            
            # Extract origin and destination
            origin = "Delhi" if "delhi" in query_lower else None
            destination = "Mumbai" if "mumbai" in query_lower else None
            
            # Extract price filter
            max_price = None
            price_keywords = [
                "under", "less than", "cheaper than", "below", "maximum", "max",
                "not more than", "no more than", "within", "up to"
            ]
            
            for keyword in price_keywords:
                if keyword in query_lower:
                    parts = query_lower.split(keyword)
                    if len(parts) > 1:
                        import re
                        numbers = re.findall(r'\d+(?:,\d+)*', parts[1].replace(',', ''))
                        if numbers:
                            max_price = float(numbers[0])
            
            # Extract time filter
            time_filter = None
            morning_keywords = ["morning", "before noon", "am", "early"]
            afternoon_keywords = ["afternoon", "post noon", "post-noon", "pm", "evening"]
            night_keywords = ["night", "late"]
            
            if any(keyword in query_lower for keyword in morning_keywords):
                time_filter = "morning"
            elif any(keyword in query_lower for keyword in afternoon_keywords):
                time_filter = "afternoon"
            elif any(keyword in query_lower for keyword in night_keywords):
                time_filter = "night"
            
            # Get flight details from Amadeus
            flight_results = await flight_service.get_flights(
                origin=origin,
                destination=destination,
                departure_date=date
            )
            
            # Extract price filter from query
            max_price = None
            query_lower = query.lower()
            price_keywords = [
                "under", "less than", "cheaper than", "below", "maximum", "max",
                "not more than", "no more than", "within", "up to"
            ]
            
            for keyword in price_keywords:
                if keyword in query_lower:
                    # Find the price mentioned after the keyword
                    parts = query_lower.split(keyword)
                    if len(parts) > 1:
                        # Extract numbers from the text after the keyword
                        import re
                        numbers = re.findall(r'\d+(?:,\d+)*', parts[1].replace(',', ''))
                        if numbers:
                            max_price = float(numbers[0])
            
            if flight_results:
                # Apply filters
                filtered_flights = flight_results
                
                # Apply price filter
                if max_price:
                    filtered_flights = [f for f in filtered_flights if f['Price'] <= max_price]
                
                # Apply time filter
                if time_filter:
                    if time_filter == "morning":
                        filtered_flights = [f for f in filtered_flights 
                            if int(f['DepartureTime'].split(':')[0]) < 12]
                    elif time_filter == "afternoon":
                        filtered_flights = [f for f in filtered_flights 
                            if 12 <= int(f['DepartureTime'].split(':')[0]) < 17]
                    elif time_filter == "night":
                        filtered_flights = [f for f in filtered_flights 
                            if int(f['DepartureTime'].split(':')[0]) >= 17]
                
                if not filtered_flights:
                    price_msg = f"under ₹{max_price:,.0f}" if max_price else ""
                    flight_info = f"\nNo flights found {price_msg} for this route and date."
                else:
                    # Sort flights by departure time
                    filtered_flights.sort(key=lambda x: x['DepartureTime'])
                    
                    # Create table header with alignment
                    flight_info = "\n| Airline | Flight | Departure Time | Duration | Price |\n"
                    flight_info += "|:--------|:-------|:--------------|:---------|------:|\n"
                    
                    # Add each flight as a row
                    for flight in filtered_flights:
                        # Format time to be more readable
                        dep_time = f"{flight['DepartureTime'][:5]}"
                        
                        # Format price with thousand separator
                        price = "{:,.0f}".format(flight['Price'])
                        
                        # Build the row
                        flight_info += f"| {flight['Airline']} | {flight['FlightNumber']} | "
                        flight_info += f"{dep_time} | "
                        flight_info += f"{flight['Duration']} | "
                        flight_info += f"₹{price} |\n"
                    
                    # Build filter message
                    filters = []
                    if max_price:
                        filters.append(f"under ₹{max_price:,.0f}")
                    if time_filter:
                        time_desc = {
                            "morning": "before noon",
                            "afternoon": "between 12 PM and 5 PM",
                            "night": "after 5 PM"
                        }[time_filter]
                        filters.append(time_desc)
                    
                    filter_msg = " and ".join(filters)
                    flight_info += f"\nShowing {len(filtered_flights)} flights {filter_msg} (sorted by departure time)"
                
                query = f"Here are the available flights from {origin} to {destination} for {date}:\n{flight_info}\n\nPlease note:\n- All times are in 24-hour format\n- Prices are in Indian Rupees (₹)\n- Duration shows hours and minutes"
            
        except Exception as e:
            logging.error(f"Error getting flight details: {e}")
            query = f"Error getting flight details: {str(e)}. " + query
        
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        
        # Create the prompt with context
        prompt = f"""You are a flight booking assistant. Present the flight information EXACTLY as shown below, preserving all markdown formatting.

Here are the available flights from {origin} to {destination} for {date}:

{flight_info}

Notes:
- All times are in 24-hour format
- Prices are in Indian Rupees (₹)
- Duration shows hours and minutes

Would you like to:
1. Filter by airline
2. Sort by price
3. Sort by departure time
4. Search for different dates

Please let me know how I can help you further."""
        
        if not flight_results:
            prompt = """I apologize, but I couldn't find any flights matching your criteria at the moment. Here are some suggestions:

1. Try different dates: Flight availability can vary by day
2. Check alternative airlines: Different carriers may have other options
3. Visit these resources for more options:
   - Popular flight booking websites (MakeMyTrip, Cleartrip)
   - Airline websites (Air India, IndiGo, SpiceJet)
   - Local travel agencies

Would you like to try searching for a different date or route?"""
        
        data = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 1,
                "topP": 1,
                "maxOutputTokens": 1024,
                "stopSequences": ["tool_code", "tool_code_output"]
            }
        }
        
        params = {
            "key": "AIzaSyDM_a8Cp6_m9MFk_8H0e8xaBMbHbMK4tgs"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, params=params, json=data) as response:
                if response.status == 200:
                    result = await response.json()
                    logging.info(f"API Response: {result}")
                    if 'candidates' in result and result['candidates']:
                        return result['candidates'][0]['content']['parts'][0]['text']
                    else:
                        return "I apologize, but I couldn't find any flight information at the moment."
                else:
                    error_text = await response.text()
                    logging.error(f"API Error: {error_text}")
                    return f"I apologize, but I encountered an error while searching for flights. Please try again later."
                    
    except Exception as e:
        logging.error(f"Error in CallGemini: {str(e)}")
        return f"I apologize, but I encountered an error: {str(e)}"

@cl.on_chat_start
async def StartChat():
    welcome_message = "Hi there! ✈️ Ready to help you find the best flights. How can I assist you today?"
    await cl.Message(content=welcome_message, author="Answer").send()
    
@cl.on_message
async def SendMsg(user_message: cl.Message):
    try:
        # Send a thinking message
        msg = cl.Message(content="Searching for flights...")
        await msg.send()

        # Get the response
        response_text = await CallGemini(user_message.content)
        
        # Send the final response as a new message
        await cl.Message(content=response_text).send()

    except Exception as e:
        logging.error(f"Error in SendMsg: {str(e)}")
        await cl.Message(content=f"I apologize, but I encountered an error: {str(e)}").send()