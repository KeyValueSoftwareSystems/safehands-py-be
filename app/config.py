"""
Configuration management for SafeHands Senior AI Assistant Backend
"""
from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "SafeHands Senior AI Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"  # development, staging, production
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    
    # Database
    database_url: str = "postgresql+asyncpg://user:password@localhost/safehands"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    redis_db: int = 0
    redis_password: Optional[str] = None
    
    # AI Services (OpenAI Only)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    vision_model: str = "gpt-4-vision-preview"
    tts_model: str = "tts-1"
    whisper_model: str = "whisper-1"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    cors_origins: List[str] = ["*"]
    
    # WebSocket
    websocket_heartbeat_interval: int = 30  # seconds
    websocket_timeout: int = 300  # seconds
    websocket_max_connections: int = 1000
    
    # Session Management
    session_timeout: int = 3600  # 1 hour in seconds
    max_concurrent_sessions: int = 1000
    session_cleanup_interval: int = 300  # 5 minutes
    
    # File Storage
    upload_dir: str = "uploads"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    max_audio_size: int = 25 * 1024 * 1024  # 25MB
    max_image_size: int = 20 * 1024 * 1024  # 20MB
    
    # AI Processing
    ai_timeout: int = 30  # seconds
    max_retries: int = 3
    retry_delay: int = 1  # seconds
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    # Rate Limiting
    rate_limit_requests: int = 100  # per minute
    rate_limit_window: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
