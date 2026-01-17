# 🤖 AI Meeting Scheduler

An intelligent meeting scheduling application that uses natural language processing to automatically schedule meetings in Google Calendar.

![AI Meeting Scheduler](https://img.shields.io/badge/AI-Powered-blue) ![Python](https://img.shields.io/badge/Python-3.8+-green) ![React](https://img.shields.io/badge/React-18.0-blue) ![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-orange)

## 🌟 Features

- **Natural Language Processing**: Type in plain English like "Schedule meeting with John tomorrow at 3pm"
- **Smart Date/Time Parsing**: Understands "tomorrow", "Friday", "next Monday", "afternoon", etc.
- **Automatic Email Generation**: Converts names to emails (e.g., "John" → "john@email.com")
- **Google Calendar Integration**: Real-time conflict detection and meeting creation
- **Conflict Resolution**: Suggests alternative time slots when conflicts are detected
- **Beautiful UI**: Modern, responsive design with real-time feedback

## 🚀 Demo

**Input Examples:**
```
"Schedule meeting with sarah@email.com tomorrow at 2pm"
"Meet with John Friday afternoon for 1 hour"
"Quick call with Mike next Monday at 10am"
```

**The AI extracts:**
- Attendee email
- Date (with relative date understanding)
- Time (converts 12/24 hour formats)
- Duration (defaults to 30 minutes)

## 🛠️ Tech Stack

### Backend
- **Python 3.13.5** - Core language
- **Flask 3.0.0** - Web framework
- **OpenAI API (GPT-4o-mini)** - Natural language processing
- **Google Calendar API** - Calendar integration
- **OAuth 2.0** - Secure authentication

### Frontend
- **React 18** - UI framework
- **Axios** - HTTP client
- **CSS3** - Styling with gradients and animations

### APIs & Services
- **OpenAI API** - NLP for meeting extraction
- **Google Calendar API** - Meeting storage and conflict detection
- **Google OAuth 2.0** - User authentication

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Google Cloud account (for Calendar API)
- OpenAI account (with API access)

## 🔧 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/meeting-scheduler.git
cd meeting-scheduler
```

### 2. Backend Setup
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
# Add your API keys:
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here (optional)
```

### 3. Google Calendar Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Calendar API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `credentials.json` and place in `backend/` folder

### 4. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
```

## 🚀 Running the Application

### Start Backend (Terminal 1)
```bash
cd backend
python app.py
```
Backend runs on `http://localhost:5000`

### Start Frontend (Terminal 2)
```bash
cd frontend
npm start
```
Frontend runs on `http://localhost:3000`

## 📖 Usage

1. Open `http://localhost:3000` in your browser
2. Type your meeting request in natural language
3. Click "Schedule Meeting"
4. First time: Authenticate with Google Calendar
5. Meeting is created automatically!

### Example Inputs
```
✅ "Schedule meeting with john@email.com tomorrow at 3pm"
✅ "Meet with Sarah Friday afternoon for 1 hour"
✅ "Call with Mike next Monday at 10am"
✅ "Quick sync with team today at 2:30pm"
```

## 🏗️ Architecture
```
┌─────────────────┐
│   React Frontend│
│  (Port 3000)    │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   Flask Backend │
│  (Port 5000)    │
└────┬──────┬─────┘
     │      │
     │      └──────► OpenAI API (NLP)
     │
     └─────────────► Google Calendar API
                     (OAuth + Data Storage)
```

## 🔑 Key Components

### Backend (`backend/`)
- **app.py** - Main Flask application
- **nlp_service.py** - OpenAI integration for NLP
- **calendar_service.py** - Google Calendar operations
- **requirements.txt** - Python dependencies

### Frontend (`frontend/src/`)
- **App.js** - Main React component
- **App.css** - Styling

## 🎯 Future Enhancements

- [ ] Email notifications when meetings are created
- [ ] Support for recurring meetings
- [ ] Calendar view showing all scheduled meetings
- [ ] Multiple attendee support
- [ ] Integration with other calendar providers (Outlook, Apple Calendar)
- [ ] Meeting reminders via SMS/Email
- [ ] Time zone support for international meetings


## 🙏 Acknowledgments

- OpenAI for GPT-4o-mini API
- Google for Calendar API
- Flask and React communities

---

**Built with ❤️ using AI and modern web technologies**