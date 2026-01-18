from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify
from flask_cors import CORS
from services.nlp_service import extract_meeting_details
from services.calendar_service import check_availability, create_meeting
import os


# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Allow frontend to communicate with backend

# Health check endpoint - test if server is running
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Server is running!"}), 200
# Main endpoint - process meeting request
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "app": "AI Meeting Scheduler API",
        "version": "1.0",
        "status": "running",
        "endpoints": {
            "GET /health": "Health check",
            "POST /schedule-meeting": "Schedule a meeting with natural language"
        },
        "developer": "Jeena"
    }), 200
@app.route('/schedule-meeting', methods=['POST'])
def schedule_meeting():
    try:
        # Get text input from user
        data = request.json
        user_text = data.get('text', '')
        
        if not user_text:
            return jsonify({"error": "No text provided"}), 400
        
        # Step 1: Extract meeting details (simple parsing for now)
        meeting_details = extract_meeting_details(user_text)
        
        # Check if extraction had errors
        if meeting_details.get('error'):
            return jsonify({
                "success": False,
                "message": meeting_details.get('message')
            }), 400
        
        # Step 2: Check Google Calendar for conflicts
        availability = check_availability(meeting_details)
        
        # Step 3: If no conflicts, create the meeting
        if availability['available']:
            meeting_link = create_meeting(meeting_details)
            return jsonify({
                "success": True,
                "message": "Meeting scheduled successfully!",
                "details": meeting_details,
                "calendar_link": meeting_link
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Time slot not available",
                "conflicts": availability['conflicts'],
                "suggestions": availability['suggested_times']
            }), 200
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Run the server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

