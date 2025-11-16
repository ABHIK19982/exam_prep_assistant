# EXAM PREP ASSISTANT
**Description**

This is an exam prep assistant which will assist by answering questions and quizzing Users. 

LLM used - **Gemini-2.5-pro**

This is using Agentic AI which has been implemented using Langchain and LAnggraph

## Overview
A modern, responsive chatbot web application built with Flask and vanilla JavaScript. The interface features a clean design with smooth animations, real-time message handling, and full mobile responsiveness.

## Project Structure
```
.
├── app.py                  # Flask backend application
├── wsgi.py                 # WSGI entry point for Gunicorn
├── gunicorn_config.py      # Gunicorn configuration file
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css      # Styling and animations
│   └── js/
│       └── chat.js        # Client-side interactivity
├── config/
│   └── local.env          # Environment configuration
├── .gitignore             # Python gitignore
└── readme.md              # Project documentation
```

## Features
- ✅ Centered chat window with rounded borders and subtle shadow
- ✅ User messages aligned right with gradient blue bubbles
- ✅ AI messages aligned left with neutral gray bubbles
- ✅ Modern Inter font for clean typography
- ✅ Smooth fade-in/slide-up animations for new messages
- ✅ Automatic scrolling to newest message
- ✅ Responsive design for desktop and mobile
- ✅ Fixed input bar at bottom on mobile devices
- ✅ Send button with hover and active states
- ✅ Enter key to send messages

## Technology Stack
- **Backend**: Flask 3.1.2
- **WSGI Server**: Gunicorn 21.2.0
- **Frontend**: Vanilla JavaScript (ES6+)
- **Styling**: Custom CSS with animations
- **Font**: Google Fonts (Inter)

## API Endpoints
- `GET /` - Serves the main chat interface
- `POST /api/chat` - Handles message sending and AI responses
- `GET /api/messages` - Retrieves conversation history

## Deployment with Gunicorn

This application is configured to run with Gunicorn as a WSGI server for production deployments.

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running the Application

#### Development Mode (Flask built-in server)
```bash
python app.py
```

#### Production Mode (Gunicorn)

**Basic usage:**
```bash
gunicorn wsgi:application
```

**With configuration file:**
```bash
gunicorn -c gunicorn_config.py wsgi:application
```

**Custom bind address and port:**
```bash
gunicorn --bind 0.0.0.0:8000 wsgi:application
```

**With environment variables:**
```bash
PORT=8000 LOG_LEVEL=info gunicorn -c gunicorn_config.py wsgi:application
```

### Gunicorn Configuration

The `gunicorn_config.py` file contains production-ready settings:
- **Workers**: Automatically configured based on CPU count (2 × CPUs + 1)
- **Bind**: Uses `PORT` environment variable or defaults to port 8000
- **Logging**: Logs to stdout/stderr for containerized deployments
- **Worker restart**: Restarts workers after 1000 requests to prevent memory leaks
- **Timeouts**: 120 seconds for worker timeout, 30 seconds for graceful shutdown

### Environment Variables

- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level - debug, info, warning, error, critical (default: info)
- `AI_DEBUG`: Set to 'Y' to enable AI debug mode
- `OUTPUT_LOG_LOC`: Directory for output logs

### Production Recommendations

1. **Use a reverse proxy** (nginx, Apache) in front of Gunicorn
2. **Enable SSL/TLS** by configuring certificates in `gunicorn_config.py`
3. **Set up logging** to files or a logging service in production
4. **Use process managers** like systemd or supervisord for automatic restarts
5. **Monitor worker health** and adjust worker count based on traffic

## Recent Changes
- 2025-11-11: Initial project setup with Flask backend
- 2025-11-11: Created responsive chat UI with animations
- 2025-11-11: Implemented message handling and auto-scroll functionality

## User Preferences
None documented yet.

## Next Steps
- Integrate with actual AI backend (OpenAI, Anthropic, etc.)
- Add session-based conversation history persistence
- Implement typing indicators
- Add message timestamps
- Support rich media messages (images, code blocks, links)
