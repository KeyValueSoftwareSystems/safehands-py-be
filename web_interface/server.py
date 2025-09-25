"""
Simple web server to serve the SafeHands test interface
"""
import asyncio
import logging
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="SafeHands Test Interface")

# Get the directory containing this file
current_dir = Path(__file__).parent

# Mount static files
app.mount("/static", StaticFiles(directory=current_dir), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_interface():
    """Serve the main test interface"""
    try:
        index_file = current_dir / "index.html"
        if index_file.exists():
            return FileResponse(index_file)
        else:
            return HTMLResponse("""
            <html>
                <head><title>SafeHands Test Interface</title></head>
                <body>
                    <h1>SafeHands Test Interface</h1>
                    <p>index.html not found. Please ensure the file exists.</p>
                </body>
            </html>
            """)
    except Exception as e:
        logger.error(f"Error serving interface: {e}")
        return HTMLResponse(f"Error: {str(e)}", status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "SafeHands Test Interface"}

@app.get("/info")
async def get_info():
    """Get interface information"""
    return {
        "name": "SafeHands Senior AI Assistant - Test Interface",
        "version": "1.0.0",
        "description": "Web-based test interface for the SafeHands AI Assistant",
        "features": [
            "Real-time WebSocket communication",
            "Voice and text message support",
            "Screen upload and analysis",
            "Step-by-step guidance display",
            "Error detection and recovery",
            "Context-aware assistance"
        ],
        "backend_url": "http://localhost:8000",
        "websocket_url": "ws://localhost:8000/ws"
    }

if __name__ == "__main__":
    print("🚀 Starting SafeHands Test Interface Server...")
    print("📱 Open your browser and go to: http://localhost:8081")
    print("🔗 Make sure the SafeHands backend is running on: http://localhost:8000")
    print("=" * 60)
    
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8081,
        reload=True,
        log_level="info"
    )
