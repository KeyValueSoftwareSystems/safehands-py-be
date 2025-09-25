"""
SafeHands Senior AI Assistant Backend
Main FastAPI application with WebSocket support
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional

from app.config import settings
from app.models.schemas import ConnectionRequest, ConnectionResponse
from app.websocket.connection_manager import connection_manager
# from app.websocket.message_router import message_router  # Removed - using direct WebSocket handling
from app.agents.simple_swiggy_agent import simple_swiggy_agent
from app.services.session_manager import session_manager
from app.services.in_memory_state_manager import in_memory_state_manager
# from app.services.proactive_engagement import proactive_engagement_service  # Removed - not needed for simple agent
# from app.services.performance_optimizer import performance_optimizer  # Removed - not needed for simple agent
# from app.services.monitoring_system import monitoring_system

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting SafeHands Senior AI Assistant Backend...")
    
    # Connect to Redis (only for session management)
    await session_manager.connect()
    logger.info("Connected to Redis for session management")
    
    # Initialize in-memory state manager (no connection needed)
    logger.info("Initialized in-memory state manager")
    
    # Initialize services (simplified for simple Swiggy agent)
    # await performance_optimizer.initialize()  # Removed - not needed for simple agent
    # logger.info("Initialized performance optimizer")
    
    # await monitoring_system.initialize()
    # logger.info("Initialized monitoring system")
    
    # Start heartbeat task
    heartbeat_task = asyncio.create_task(connection_manager.start_heartbeat_task())
    logger.info("Started heartbeat task")
    
    # Start proactive engagement service (removed - not needed for simple agent)
    # await proactive_engagement_service.start()
    # logger.info("Started proactive engagement service")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    heartbeat_task.cancel()
    # await proactive_engagement_service.stop()  # Removed - not needed for simple agent
    
    # Cleanup services (removed - not needed for simple agent)
    # await performance_optimizer.cleanup()
    # await monitoring_system.cleanup()
    
    await session_manager.disconnect()
    logger.info("Shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend for SafeHands Senior AI Assistant",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SafeHands Senior AI Assistant Backend",
        "version": settings.app_version,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint for SafeHands Backend"""
    try:
        # Check Redis connection
        session_count = await session_manager.get_session_count()
        connection_count = connection_manager.get_connection_count()
        
        # Check workflow state manager
        workflow_sessions = await in_memory_state_manager.get_workflow_sessions()
        
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
            "version": settings.app_version,
            "timestamp": datetime.now().isoformat(),
            "components": {
                "redis": "connected",
                "websocket": "active",
                "ai_service": ai_service_status,
                "workflow_manager": "active"
            },
            "metrics": {
                "active_sessions": session_count,
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
            "service": "SafeHands Backend",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@app.post("/connect", response_model=ConnectionResponse)
async def create_connection(request: ConnectionRequest):
    """Create a new session and return connection info"""
    try:
        session_id = await session_manager.create_session(request.user_id)
        
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
    # For testing purposes, allow all connections without session validation
    # In production, you would verify the session exists
    logger.info(f"WebSocket connection attempt for session: {session_id}")
    
    # Connect the WebSocket directly without session validation
    await connection_manager.connect(websocket, session_id)
    
    try:
        while True:
            # Receive message from client
            message_data = await websocket.receive_text()
            
            # Simple WebSocket handler for Swiggy demo
            await handle_simple_websocket_message(websocket, session_id, message_data)
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session: {session_id}")
        connection_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
        connection_manager.disconnect(websocket)


async def handle_simple_websocket_message(websocket: WebSocket, session_id: str, message_data: str):
    """Simple WebSocket message handler for Swiggy demo"""
    try:
        import json
        # Parse message
        message = json.loads(message_data)
        user_text = message.get('data', {}).get('text', '') or message.get('message', '')
        
        # Skip empty messages or connection messages
        if not user_text or user_text.strip() == '':
            return
            
        logger.info(f"🍔 [WEBSOCKET] Processing: {user_text}")
        
        # Process with simplified Swiggy agent
        response = await simple_swiggy_agent.process_request(session_id, user_text)
        
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
        logger.info(f"🍔 [WEBSOCKET] Sent response to {session_id}")
        
    except Exception as e:
        logger.error(f"🍔 [WEBSOCKET] Error: {e}")
        error_response = {
            "message_type": "error",
            "data": {"error_message": str(e)}
        }
        await websocket.send_text(json.dumps(error_response))


@app.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get session information"""
    session = await session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    success = await session_manager.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}


@app.get("/stats")
async def get_stats():
    """Get system statistics"""
    try:
        active_sessions = await session_manager.get_active_sessions()
        connection_count = connection_manager.get_connection_count()
        
        return {
            "active_sessions": len(active_sessions),
            "active_connections": connection_count,
            "session_ids": list(active_sessions)
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")


# Week 4: Monitoring and Analytics Endpoints

# @app.get("/monitoring/dashboard")
# async def get_monitoring_dashboard():
#     """Get real-time monitoring dashboard data"""
#     try:
#         dashboard_data = await monitoring_system.get_real_time_dashboard()
#         return dashboard_data
#     except Exception as e:
#         logger.error(f"Error getting monitoring dashboard: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")


# @app.get("/monitoring/analytics")
# async def get_analytics_report(
#     start_time: Optional[str] = None,
#     end_time: Optional[str] = None
# ):
#     """Get comprehensive analytics report"""
#     try:
#         from datetime import datetime
#         
#         start_dt = None
#         end_dt = None
#         
#         if start_time:
#             start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
#         if end_time:
#             end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
#         
#         report = await monitoring_system.get_analytics_report(start_dt, end_dt)
#         return report
#     except Exception as e:
#         logger.error(f"Error getting analytics report: {e}")
#         raise HTTPException(status_code=500, detail="Internal server error")


# Monitoring endpoints removed - not needed for simple Swiggy agent
# @app.get("/monitoring/performance")
# @app.get("/monitoring/knowledge-base") 
# @app.post("/monitoring/feedback")


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
            return {"status": "error", "message": "Failed to mark interruption as escalated"}
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


# ==================== SIMPLIFIED SWIGGY DEMO ENDPOINT ====================

@app.post("/api/swiggy-demo")
async def swiggy_demo(request: Dict[str, Any]):
    """Simplified Swiggy ordering demo endpoint"""
    try:
        session_id = request.get("session_id", "demo_session")
        user_input = request.get("message", "")
        
        logger.info(f"🍔 [SWIGGY_DEMO] Processing request: {user_input}")
        
        # Process with simplified agent
        response = await simple_swiggy_agent.process_request(session_id, user_input)
        
        return {
            "session_id": response.session_id,
            "response_type": response.response_type.value,
            "content": response.content,
            "ui_element": response.ui_element,
            "next_step": response.next_step
        }
        
    except Exception as e:
        logger.error(f"Error in Swiggy demo: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
