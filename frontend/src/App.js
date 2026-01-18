import React, { useState } from 'react';
import './App.css';
import axios from 'axios';

function App() {
  const [meetingText, setMeetingText] = useState('');
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await axios.post(`${process.env.REACT_APP_API_URL}/schedule-meeting`, {
        text: meetingText
      });

      setResponse(result.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to schedule meeting');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <div className="container">
        <h1>🤖 AI Meeting Scheduler</h1>
        <p className="subtitle">Schedule meetings with natural language</p>

        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label>Enter meeting details:</label>
            <input
              type="text"
              value={meetingText}
              onChange={(e) => setMeetingText(e.target.value)}
              placeholder="Schedule meeting with John tomorrow at 3pm for 1 hour"
              className="meeting-input"
              disabled={loading}
            />
            <p className="hint">Try: "Meet Sarah tomorrow at 2pm" or "Call with john@email.com Friday afternoon"</p>
          </div>

          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Scheduling...' : 'Schedule Meeting'}
          </button>
        </form>

        {/* Success Response */}
        {response && response.success && (
          <div className="success-box">
            <h2>✅ Meeting Scheduled!</h2>
            <div className="details">
              <p><strong>Attendee:</strong> {response.details.attendee}</p>
              <p><strong>Date:</strong> {response.details.date}</p>
              <p><strong>Time:</strong> {new Date('2000-01-01 ' + response.details.time).toLocaleTimeString('en-US', {hour: 'numeric', minute: '2-digit', hour12: true})}</p>
              <p><strong>Duration:</strong> {response.details.duration} minutes</p>
            </div>
            <div className="button-group">
              <a href={response.calendar_link?.event_link} target="_blank" rel="noopener noreferrer" className="calendar-link">
                View in Google Calendar →
              </a>
              <button onClick={() => { setMeetingText(''); setResponse(null); }} className="reset-btn">
                Schedule Another Meeting
              </button>
            </div>
          </div>
        )}

        {/* Conflict Response */}
        {response && !response.success && response.suggestions && (
          <div className="conflict-box">
            <h2>⚠️ Time Slot Not Available</h2>
            <p className="conflict-message">{response.message}</p>

            {response.suggestions.length > 0 && (
              <div className="suggestions">
                <h3>Suggested Alternative Times:</h3>
                <ul>
                  {response.suggestions.map((suggestion, index) => (
                    <li key={index}>{suggestion}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="error-box">
            <h2>❌ Error</h2>
            <p>{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;