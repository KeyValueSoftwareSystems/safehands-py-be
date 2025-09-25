"""
SafeHands Backend - Full LLM Agent
Main FastAPI application with WebSocket support
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import base64
import io
from PIL import Image

from app.config import settings
from app.models.schemas import ConnectionRequest, ConnectionResponse
from app.websocket.connection_manager import connection_manager
from app.agents.simple_swiggy_agent import full_llm_swiggy_agent
from app.services.in_memory_state_manager import in_memory_state_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting SafeHands Backend (Full LLM Agent)...")
    
    # Initialize in-memory state manager
    logger.info("Initialized in-memory state manager")
    
    # Start heartbeat task
    heartbeat_task = asyncio.create_task(connection_manager.start_heartbeat_task())
    logger.info("Started heartbeat task")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    heartbeat_task.cancel()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="SafeHands Backend - Full LLM Agent",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint for V2"""
    return {
        "message": "SafeHands Backend V2 - Full LLM Agent",
        "version": "2.0.0",
        "status": "running",
        "agent": "Full LLM Swiggy Agent"
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    try:
        # Check in-memory state manager
        workflow_sessions = await in_memory_state_manager.get_workflow_sessions()
        connection_count = connection_manager.get_connection_count()
        
        # Check AI service (basic connectivity)
        ai_service_status = "available"
        try:
            # Simple test to ensure AI service is accessible
            from app.services.ai_service import AIService
            ai_service = AIService()
            ai_service_status = "available"
        except Exception as e:
            ai_service_status = f"error: {str(e)[:50]}"
        
        return {
            "status": "healthy",
            "service": "SafeHands Backend",
            "version": "1.0.0",
            "agent": "Full LLM Swiggy Agent",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "in_memory_storage": "active",
                "websocket": "active",
                "ai_service": ai_service_status,
                "workflow_manager": "active"
            },
            "metrics": {
                "active_connections": connection_count,
                "active_workflows": len(workflow_sessions)
            },
            "endpoints": {
                "websocket": f"/ws/{{session_id}}",
                "swiggy_demo": "/api/swiggy-demo",
                "sessions": "/sessions/{session_id}",
                "workflow_state": "/workflow/state/{session_id}"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "SafeHands Backend V2",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/connect", response_model=ConnectionResponse)
async def create_connection(request: ConnectionRequest):
    """Create a new session and return connection info"""
    try:
        import uuid
        session_id = f"v2_{request.user_id}_{uuid.uuid4().hex[:8]}"
        
        return ConnectionResponse(
            session_id=session_id,
            status="success",
            message="Session created successfully"
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time communication"""
    logger.info(f"WebSocket connection attempt for session: {session_id}")
    
    # Connect the WebSocket directly without session validation
    await connection_manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            message_data = await websocket.receive_text()
            
            # Simple WebSocket handler for V2
            await handle_v2_websocket_message(websocket, session_id, message_data)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket V2 disconnected for session: {session_id}")
        connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket V2 error for session {session_id}: {e}")
        connection_manager.disconnect(websocket)


async def handle_v2_websocket_message(websocket: WebSocket, session_id: str, message_data: str):
    """V2 WebSocket message handler with Full LLM Agent"""
    try:
        import json
        # Parse message
        message = json.loads(message_data)
        user_text = message.get('data', {}).get('text', '') or message.get('message', '')
        
        # Skip empty messages or connection messages
        if not user_text or user_text.strip() == '':
            return
            
        logger.info(f"🤖 [V2_WEBSOCKET] Processing: {user_text}")
        
        # Process with Full LLM Agent
        response = await full_llm_swiggy_agent.process_request(session_id, user_text)
        
        # Send response back
        response_data = {
            "message_type": "response",
            "data": {
                "type": response.response_type.value,
                "content": response.content,
                "session_id": session_id
            }
        }
        
        await websocket.send_text(json.dumps(response_data))
        logger.info(f"🤖 [WEBSOCKET] Sent response to {session_id}")
        
    except Exception as e:
        logger.error(f"🤖 [WEBSOCKET] Error: {e}")
        error_response = {
            "message_type": "error",
            "data": {"error_message": str(e)}
        }
        await websocket.send_text(json.dumps(error_response))


@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get session information"""
    # Check if session has any workflow state
    workflow_state = await in_memory_state_manager.load_workflow_state(session_id)
    if not workflow_state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "workflow_state": workflow_state,
        "status": "active"
    }


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    success = await in_memory_state_manager.delete_workflow_state(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        workflow_sessions = await in_memory_state_manager.get_workflow_sessions()
        connection_count = connection_manager.get_connection_count()
        
        return {
            "active_workflows": len(workflow_sessions),
            "active_connections": connection_count,
            "session_ids": list(workflow_sessions),
            "version": "1.0.0",
            "agent": "Full LLM Swiggy Agent"
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


# ==================== WORKFLOW STATE MANAGEMENT ENDPOINTS ====================

@app.get("/workflow/state/{session_id}")
async def get_workflow_state(session_id: str):
    """Get current workflow state for a session"""
    try:
        workflow_state = await in_memory_state_manager.load_workflow_state(session_id)
        if not workflow_state:
            return {"status": "no_workflow", "message": "No active workflow found"}
        
        return {
            "status": "success",
            "workflow_state": {
                "workflow_type": workflow_state.get("workflow_type"),
                "workflow_status": workflow_state.get("workflow_status"),
                "current_step_index": workflow_state.get("current_step_index"),
                "total_steps": len(workflow_state.get("workflow_steps", [])),
                "current_step": workflow_state.get("current_step"),
                "waiting_for_verification": workflow_state.get("waiting_for_verification"),
                "workflow_steps": workflow_state.get("workflow_steps", [])
            }
        }
    except Exception as e:
        logger.error(f"Error getting workflow state: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/workflow/interruption/{session_id}")
async def get_interruption(session_id: str):
    """Get interruption data for frontend escalation"""
    try:
        interruption = await in_memory_state_manager.get_interruption(session_id)
        if not interruption:
            return {"status": "no_interruption", "message": "No interruption found"}
        
        return {
            "status": "success",
            "interruption": interruption
        }
    except Exception as e:
        logger.error(f"Error getting interruption: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/workflow/interruption/{session_id}/escalated")
async def mark_interruption_escalated(session_id: str):
    """Mark interruption as escalated to frontend"""
    try:
        success = await in_memory_state_manager.mark_interruption_escalated(session_id)
        if success:
            return {"status": "success", "message": "Interruption marked as escalated"}
        else:
            return {"status": "error", "message": "No interruption found to escalate"}
    except Exception as e:
        logger.error(f"Error marking interruption as escalated: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/workflow/state/{session_id}")
async def clear_workflow_state(session_id: str):
    """Clear workflow state for a session"""
    try:
        success = await in_memory_state_manager.delete_workflow_state(session_id)
        if success:
            return {"status": "success", "message": "Workflow state cleared"}
        else:
            return {"status": "error", "message": "No workflow state to clear"}
    except Exception as e:
        logger.error(f"Error clearing workflow state: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/workflow/sessions")
async def get_active_workflow_sessions():
    """Get all active workflow sessions"""
    try:
        sessions = await in_memory_state_manager.get_workflow_sessions()
        return {
            "status": "success",
            "active_sessions": sessions,
            "count": len(sessions)
        }
    except Exception as e:
        logger.error(f"Error getting active workflow sessions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== V2 SWIGGY DEMO ENDPOINT ====================

@app.post("/api/swiggy-demo")
async def swiggy_demo_v2(request: Dict[str, Any]):
    """V2 Swiggy ordering demo endpoint with Full LLM Agent"""
    try:
        session_id = request.get("session_id", "demo_session_v2")
        user_input = request.get("message", "")
        
        logger.info(f"🤖 [V2_SWIGGY_DEMO] Processing request: {user_input}")
        
        # Process with Full LLM Agent
        response = await full_llm_swiggy_agent.process_request(session_id, user_input)
        
        return {
            "session_id": response.session_id,
            "response_type": response.response_type.value,
            "content": response.content,
            "ui_element": response.ui_element,
            "next_step": response.next_step,
            "version": "1.0.0",
            "agent": "Full LLM Swiggy Agent"
        }
        
    except Exception as e:
        logger.error(f"Error in V2 Swiggy demo: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==================== IMAGE UPLOAD ENDPOINTS ====================

@app.post("/api/upload-screenshot")
async def upload_screenshot(
    session_id: str = Form(...),
    message: str = Form(""),
    image: UploadFile = File(...)
):
    """Upload screenshot with optional text message for V2"""
    try:
        logger.info(f"📸 [V2_IMAGE_UPLOAD] Processing screenshot upload for session: {session_id}")
        logger.info(f"📸 [V2_IMAGE_UPLOAD] Image filename: {image.filename}")
        logger.info(f"📸 [V2_IMAGE_UPLOAD] Image content type: {image.content_type}")
        logger.info(f"📸 [V2_IMAGE_UPLOAD] Message: {message}")
        
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_data = await image.read()
        logger.info(f"📸 [V2_IMAGE_UPLOAD] Image size: {len(image_data)} bytes")
        
        # Check file size (max 20MB)
        if len(image_data) > 20 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Image file too large. Maximum size is 20MB.")
        
        # Convert to base64 for processing
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Process with Full LLM Agent (with image)
        response = await full_llm_swiggy_agent.process_request_with_image(session_id, message, image_base64)
        
        return {
            "session_id": response.session_id,
            "response_type": response.response_type.value,
            "content": response.content,
            "ui_element": response.ui_element,
            "next_step": response.next_step,
            "version": "1.0.0",
            "agent": "Full LLM Swiggy Agent with Image Analysis",
            "image_processed": True
        }
        
    except Exception as e:
        logger.error(f"Error in V2 screenshot upload: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/analyze-screenshot")
async def analyze_screenshot(
    session_id: str = Form(...),
    image: UploadFile = File(...)
):
    """Analyze screenshot without workflow processing"""
    try:
        logger.info(f"🔍 [IMAGE_ANALYSIS] Processing screenshot analysis for session: {session_id}")
        logger.info(f"🔍 [IMAGE_ANALYSIS] Image filename: {image.filename}")
        
        # Validate image file
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_data = await image.read()
        logger.info(f"🔍 [V2_IMAGE_ANALYSIS] Image size: {len(image_data)} bytes")
        
        # Convert to base64 for processing
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Analyze image with Full LLM Agent
        analysis = await full_llm_swiggy_agent.analyze_screenshot(image_base64)
        
        return {
            "session_id": session_id,
            "analysis": analysis,
            "version": "1.0.0",
            "agent": "Full LLM Swiggy Agent - Image Analysis"
        }
        
    except Exception as e:
        logger.error(f"Error in V2 screenshot analysis: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
