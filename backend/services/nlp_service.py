from dotenv import load_dotenv
load_dotenv()

import openai
from datetime import datetime, timedelta
import os
import json

# Set OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

def extract_meeting_details(user_text):
    """
    Uses OpenAI to extract meeting information from natural language
    """
    
    try:
        today = datetime.now()
        today_str = today.strftime('%Y-%m-%d')
        day_of_week = today.strftime('%A')
        
        prompt = f"""You are a meeting scheduler assistant. Extract meeting details from the user's natural language input.

Today's date is {today_str} ({day_of_week}).

User input: "{user_text}"

Extract and return ONLY a JSON object with these fields:
- attendee: email address (MUST include @ symbol. If only name given, create email like name@email.com)
- date: in YYYY-MM-DD format (calculate relative dates like "tomorrow", "Friday", "next Monday")
- time: in HH:MM 24-hour format (convert "3pm" to "15:00", "morning" to "09:00", "afternoon" to "14:00")
- duration: meeting length in minutes (default 30 if not mentioned, "1 hour" = 60)
- title: brief meeting title based on context

Rules:
- "tomorrow" = {(today + timedelta(days=1)).strftime('%Y-%m-%d')}
- "today" = {today_str}
- Day names (Monday, Friday, etc.) = next occurrence of that day
- "morning" = 09:00, "afternoon" = 14:00, "evening" = 17:00
- Always include attendee email with @ symbol

Return ONLY valid JSON, no other text.
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a meeting scheduling assistant. Return only JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        response_text = response.choices[0].message.content.strip()
        
        # Remove markdown if present
        if response_text.startswith("```"):
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
        
        meeting_details = json.loads(response_text.strip())
        
        print(f"OpenAI extracted details: {meeting_details}")
        return meeting_details
        
    except Exception as e:
        print(f"Error in OpenAI extraction: {e}")
        return {
            "error": True,
            "message": f"Could not understand meeting request. Try: 'john@email.com tomorrow at 3pm'"
        }