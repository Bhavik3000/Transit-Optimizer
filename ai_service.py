from dotenv import load_dotenv
import os

load_dotenv()

from google import genai

client = genai.Client(api_key=os.getenv("GEMINIAI_API_KEY"))

class AIService:
    @staticmethod
    def get_commute_advice(transit_data: dict, calendar_data: list, user_question: str, weather_data: str, direction: str) -> str:
        
        context = f"""
        You are the 'Smart Commute Assistant' for a university student in Vancouver. 
        Be concise, helpful, and direct.
        
        BACKGROUND KNOWLEDGE:
        - The student is currently looking for a commute heading towards: {direction}.
        - If heading to 'UBC', they are taking the Westbound 49 bus.
        - If heading to 'Home', they are taking the Eastbound 49 bus away from campus.
        - The travel time is approximately 45 minutes.
        - The current weather outside is: {weather_data}
        
        LIVE CONTEXT:
        Here is the LIVE transit data for their chosen bus stop right now:
        {transit_data}
        
        Here are the user's UPCOMING CALENDAR EVENTS:
        {calendar_data}
        
        The user is asking this question: "{user_question}"
        
        INSTRUCTIONS:
        Based on the live bus data, their travel time, and their upcoming calendar events, 
        answer the user's question. Warn them if a bus delay will make them late. 
        If the weather is cold or raining, mention it and advise them to dress appropriately 
        for the wait at the bus stop.
        
        You are a precise transit assistant. CRITICAL RULE: The baseline travel time between Home and 
        UBC is exactly 30 minutes. Only add extra time if the live transit data shows a delay. 
        You also have access to the user's upcoming schedule: {calendar_data}. 
        If they have an event, calculate exactly what time they need to leave to arrive 
        10 minutes early
        """
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=context
            )
            return response.text
        except Exception as e:
            return f"Brain is currently offline: {str(e)}"