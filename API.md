# SafeHands Senior AI Assistant API Documentation

## Overview

The SafeHands Senior AI Assistant Backend provides a WebSocket-based API for real-time communication with mobile applications. The system is designed to provide step-by-step guidance and assistance to seniors using their mobile devices.

## Base URL

- Development: `http://localhost:8000`
- WebSocket: `ws://localhost:8000/ws/{session_id}`

## Authentication

Currently, the system uses session-based authentication. Each client must create a session before establishing a WebSocket connection.

## REST API Endpoints

### 1. Health Check

**GET** `/health`

Check the health status of the service.

**Response:**
```json
{
  "status": "healthy",
  "active_sessions": 5,
  "active_connections": 3
}
```

### 2. Create Session

**POST** `/connect`

Create a new session for a user.

**Request Body:**
```json
{
  "user_id": "optional_user_id",
  "device_info": {
    "platform": "android",
    "version": "1.0.0"
  }
}
```

**Response:**
```json
{
  "session_id": "uuid-string",
  "status": "success",
  "message": "Session created successfully",
  "server_time": "2024-01-01T00:00:00Z"
}
```

### 3. Get Session Info

**GET** `/sessions/{session_id}`

Get information about a specific session.

**Response:**
```json
{
  "session_id": "uuid-string",
  "user_id": "user_id",
  "created_at": "2024-01-01T00:00:00Z",
  "last_activity": "2024-01-01T00:05:00Z",
  "current_app": "swiggy",
  "current_task": "order_food",
  "is_active": true
}
```

### 4. Delete Session

**DELETE** `/sessions/{session_id}`

Delete a specific session.

**Response:**
```json
{
  "message": "Session deleted successfully"
}
```

### 5. System Statistics

**GET** `/stats`

Get system-wide statistics.

**Response:**
```json
{
  "active_sessions": 10,
  "active_connections": 8,
  "session_ids": ["uuid1", "uuid2", "uuid3"]
}
```

## WebSocket API

### Connection

**WebSocket** `/ws/{session_id}`

Establish a WebSocket connection using a valid session ID.

### Message Format

All WebSocket messages follow this format:

```json
{
  "message_type": "voice|screen|command|heartbeat|error",
  "data": {
    // Message-specific data
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Message Types

#### 1. Voice Message

Send voice input from the user.

```json
{
  "message_type": "voice",
  "data": {
    "session_id": "uuid-string",
    "audio_data": "base64-encoded-audio",
    "timestamp": "2024-01-01T00:00:00Z",
    "language": "en-US"
  }
}
```

#### 2. Screen Message

Send a screenshot of the current screen.

```json
{
  "message_type": "screen",
  "data": {
    "session_id": "uuid-string",
    "screenshot": "base64-encoded-image",
    "timestamp": "2024-01-01T00:00:00Z",
    "screen_size": {
      "width": 1080,
      "height": 1920
    }
  }
}
```

#### 3. Command Message

Send a text command to the assistant.

```json
{
  "message_type": "command",
  "data": {
    "session_id": "uuid-string",
    "command": "help",
    "parameters": {
      "context": "swiggy_app"
    },
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

#### 4. Heartbeat Message

Keep the connection alive.

```json
{
  "message_type": "heartbeat",
  "data": {
    "session_id": "uuid-string",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

#### 5. Error Message

Report an error from the client.

```json
{
  "message_type": "error",
  "data": {
    "session_id": "uuid-string",
    "error_code": "CLIENT_ERROR",
    "error_message": "Failed to capture screen",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

### Response Messages

The server sends responses in this format:

```json
{
  "message_type": "response",
  "data": {
    "type": "instruction|highlight|verification|proactive|error",
    "content": "Response text",
    "audio_response": "base64-encoded-audio",
    "ui_element": {
      "id": "element_id",
      "type": "button",
      "position": {
        "x": 100,
        "y": 200,
        "width": 150,
        "height": 50
      },
      "text": "Order Now",
      "app_context": "swiggy"
    },
    "next_step": "Tap the order button",
    "session_id": "uuid-string"
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Response Types

#### 1. Instruction Response

Provides step-by-step guidance.

```json
{
  "type": "instruction",
  "content": "Step 1: Tap on the Swiggy app icon",
  "next_step": "Look for the orange Swiggy icon on your home screen"
}
```

#### 2. Highlight Response

Highlights a specific UI element.

```json
{
  "type": "highlight",
  "content": "I've highlighted the search button for you",
  "ui_element": {
    "id": "search_button",
    "type": "button",
    "position": {"x": 50, "y": 100, "width": 100, "height": 40},
    "text": "Search",
    "app_context": "swiggy"
  }
}
```

#### 3. Verification Response

Verifies if a step was completed correctly.

```json
{
  "type": "verification",
  "content": "Great! I can see you've opened the Swiggy app. Now let's search for food.",
  "next_step": "Tap on the search bar at the top"
}
```

#### 4. Proactive Response

Engages the user proactively.

```json
{
  "type": "proactive",
  "content": "Would you like me to help you with anything else?",
  "next_step": "Just say what you'd like to do next"
}
```

## Error Handling

### HTTP Errors

- `400 Bad Request`: Invalid request data
- `404 Not Found`: Session or resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### WebSocket Errors

- `4004`: Session not found
- `4000`: Normal closure
- `4001`: Going away
- `4002`: Protocol error
- `4003`: Unsupported data type

## Rate Limiting

- WebSocket connections: 10 per IP address
- API requests: 100 per minute per IP address
- Session creation: 5 per minute per IP address

## Best Practices

1. **Always create a session** before establishing WebSocket connection
2. **Send heartbeat messages** every 30 seconds to keep connection alive
3. **Handle disconnections gracefully** and reconnect when needed
4. **Compress large data** (audio, images) before sending
5. **Use appropriate message types** for different data
6. **Implement proper error handling** for all message types

## Example Client Implementation

```python
import asyncio
import websockets
import json
import requests

async def connect_to_assistant():
    # Create session
    response = requests.post("http://localhost:8000/connect", 
                           json={"user_id": "user123"})
    session_id = response.json()["session_id"]
    
    # Connect to WebSocket
    uri = f"ws://localhost:8000/ws/{session_id}"
    async with websockets.connect(uri) as websocket:
        # Send a command
        message = {
            "message_type": "command",
            "data": {
                "session_id": session_id,
                "command": "help",
                "timestamp": "2024-01-01T00:00:00Z"
            }
        }
        await websocket.send(json.dumps(message))
        
        # Listen for responses
        response = await websocket.recv()
        print(json.loads(response))

# Run the client
asyncio.run(connect_to_assistant())
```
