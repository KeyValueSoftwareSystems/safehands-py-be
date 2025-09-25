#!/usr/bin/env python3
"""
SafeHands Backend - Full LLM Agent
"""
import uvicorn
import logging
from app.main import app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Starting SafeHands Backend (Full LLM Agent) on port 8000")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
