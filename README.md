# Voice Cloning Web Application

A complete voice cloning web application using Resemble AI's Chatterbox technology, focused on rapid deployment and essential functionality.

## Project Overview

This application enables users to:
- Upload audio files for voice training
- Generate text-to-speech with trained voice models
- Manage a library of trained voices
- Access the system through an invite-only authentication system

## Tech Stack

- **Backend**: Python Flask/FastAPI with Resemble AI Chatterbox integration
- **Frontend**: Gradio for rapid UI development
- **Deployment**: Vercel (if compatible) or best alternative
- **Database**: SQLite (with migration path to PostgreSQL)
- **File Storage**: Local initially, cloud storage integration ready

## Project Structure

```
voice-cloning-app/
├── app/                    # Main application directory
│   ├── api/                # API endpoints
│   ├── auth/               # Authentication system
│   ├── models/             # Database models
│   ├── services/           # Business logic and external services
│   ├── static/             # Static assets
│   │   ├── css/            # Stylesheets
│   │   ├── js/             # JavaScript files
│   │   └── uploads/        # User uploaded files
│   ├── templates/          # HTML templates
│   └── utils/              # Utility functions
├── tests/                  # Test suite
├── docs/                   # Documentation
├── .gitignore              # Git ignore file
├── README.md               # Project documentation
└── requirements.txt        # Python dependencies
```

## Priority Features

1. **Voice Upload & Training Pipeline**
   - Audio file upload (min 10 minutes, ideal 30 minutes)
   - Integration with Chatterbox voice training
   - Progress tracking for training jobs

2. **Text-to-Speech Generation**
   - Real-time text input
   - Voice selection from trained models
   - Audio output with download

3. **User Authentication**
   - Invite-only system
   - Admin approval workflow
   - Basic user dashboard

4. **Voice Library Management**
   - List trained voices
   - Voice metadata management
   - Delete/manage voices

5. **Real-time Preview**
   - Quick voice samples during training
   - Live text-to-speech preview

## Development Approach

This project follows a "speed over perfection" philosophy, focusing on delivering a functional MVP quickly while maintaining a scalable architecture.

## Resemble AI Chatterbox Integration

The application integrates with [Resemble AI's Chatterbox](https://github.com/resemble-ai/chatterbox) for zero-shot voice cloning capabilities, supporting:
- Emotion control
- WAV/MP3 file formats
- Webhook architecture for async processing

## Getting Started

Instructions for setting up the development environment and running the application will be provided in subsequent documentation.
