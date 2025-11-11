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
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css      # Styling and animations
│   └── js/
│       └── chat.js        # Client-side interactivity
├── .gitignore             # Python gitignore
└── replit.md              # Project documentation
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
- **Frontend**: Vanilla JavaScript (ES6+)
- **Styling**: Custom CSS with animations
- **Font**: Google Fonts (Inter)

## API Endpoints
- `GET /` - Serves the main chat interface
- `POST /api/chat` - Handles message sending and AI responses
- `GET /api/messages` - Retrieves conversation history

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
