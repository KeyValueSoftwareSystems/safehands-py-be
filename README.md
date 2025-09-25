# SafeHands Senior AI Assistant Backend

A production-ready Python backend for the SafeHands Senior AI Assistant, providing real-time WebSocket communication, intelligent AI orchestration, and comprehensive assistance for seniors.

## 🚀 Features

- **Real-time WebSocket Communication**: Always-on connection for instant assistance
- **Intelligent AI Workflow**: LangGraph-based orchestration with conditional branching
- **Multi-modal Processing**: Voice, screen, and command message handling
- **Session Management**: Redis-based session tracking and management
- **Error Recovery**: Smart error detection and recovery strategies
- **Learning System**: Continuous learning from user interactions
- **Performance Optimization**: Caching, monitoring, and analytics

## 🛠 Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **WebSockets**: Real-time bidirectional communication
- **LangGraph**: Intelligent AI agent orchestration
- **OpenAI**: LLM integration (GPT-3.5-turbo, GPT-4-Vision, Whisper, TTS)
- **Redis**: Session management and caching
- **PostgreSQL**: Persistent data storage

## 📋 Prerequisites

- Python 3.11+
- Redis server
- PostgreSQL database
- OpenAI API key

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd safehands-py-be

# Run the development setup script
python setup_dev.py

# Or manually set your API key
export OPENAI_API_KEY="sk-your-openai-api-key-here"
cp env.example .env
```

### 2. Start with Docker (Recommended)

```bash
# Start all services
docker-compose up -d

# Check if services are running
curl http://localhost:8000/health
```

### 3. Manual Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start Redis and PostgreSQL
# (Install and start these services on your system)

# Start the backend
./start.sh
```

## 🧪 Testing

### Web-Based Test Interface

```bash
# Start the backend
./start.sh

# Start the test interface (in another terminal)
./start_test_interface.sh

# Open your browser to: http://localhost:3000
```

**Test Interface Features:**
- 🤖 Real-time chat with AI assistant
- 📱 Screen upload and analysis
- 🎯 Quick test scenarios (food ordering, messaging, payments)
- 📊 Performance monitoring

## 🏗 Architecture

### Core Components

- **`app/main.py`**: FastAPI application with WebSocket endpoints
- **`app/agents/`**: AI agents for intent recognition, guidance generation, etc.
- **`app/services/`**: Core services (AI, voice, screen analysis, RAG)
- **`app/websocket/`**: WebSocket connection and message management
- **`app/models/`**: Data models and schemas

### Intelligent Workflow

The system uses LangGraph for intelligent AI orchestration:

```
Intent Recognition → Context Analysis → RAG Enhancement → 
Guidance Generation → Step Verification → Error Detection → 
Learning → Response Generation
```

With conditional branching based on:
- Intent complexity (simple vs complex)
- User skill level (beginner/intermediate/advanced)
- Error types and recovery strategies

## 📡 API Endpoints

### REST API
- `GET /health` - Health check
- `GET /stats` - System statistics
- `POST /sessions` - Create session
- `GET /sessions/{session_id}` - Get session info

### WebSocket API
- `ws://localhost:8000/ws/{session_id}` - Real-time communication

**Message Types:**
- `voice` - Voice input processing
- `screen` - Screen analysis
- `command` - Text commands
- `heartbeat` - Connection health

## 🔧 Configuration

Key environment variables in `.env`:

```bash
# AI Services
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
VISION_MODEL=gpt-4-vision-preview

# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/safehands
REDIS_URL=redis://localhost:6379

# Server
HOST=0.0.0.0
PORT=8000
```

## 🚀 Production Deployment

### Docker Compose
```bash
# Production deployment
docker-compose -f docker-compose.yml up -d

# Check logs
docker-compose logs -f backend
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set production environment variables
export ENVIRONMENT=production
export DEBUG=false

# Start with production settings
./start.sh
```

## 📊 Monitoring

The system includes comprehensive monitoring:

- **Real-time Metrics**: Request counts, response times, error rates
- **Session Analytics**: User interactions, success rates, learning patterns
- **Performance Monitoring**: System health, resource usage
- **Error Tracking**: Detailed error logging and recovery

Access monitoring at:
- `GET /monitoring/dashboard` - Real-time dashboard
- `GET /monitoring/analytics` - Analytics reports
- `GET /monitoring/performance` - Performance metrics

## 🤝 Development

### Project Structure
```
safehands-py-be/
├── app/                    # Main application code
│   ├── agents/            # AI agents and workflows
│   ├── services/          # Core services
│   ├── websocket/         # WebSocket handling
│   ├── models/            # Data models
│   └── main.py           # FastAPI application
├── web_interface/         # Test interface
├── requirements.txt       # Dependencies
├── docker-compose.yml     # Container orchestration
└── README.md             # This file
```

### Key Features for Development

1. **Intelligent Routing**: Conditional workflow based on user context
2. **Error Recovery**: Multiple strategies for handling user errors
3. **Learning System**: Continuous improvement from interactions
4. **Performance Optimization**: Caching and monitoring
5. **Real-time Communication**: WebSocket-based instant responses

## 📝 License

This project is part of the SafeHands Senior AI Assistant system.

## 🆘 Support

For development support and questions, please refer to the API documentation in `API.md`.