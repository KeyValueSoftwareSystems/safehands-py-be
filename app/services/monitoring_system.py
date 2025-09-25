"""
Comprehensive monitoring and analytics system
"""
import asyncio
import json
import time
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import redis.asyncio as redis
from app.config import settings


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

logger = logging.getLogger(__name__)


class EventType(Enum):
    """Types of events to monitor"""
    USER_SESSION_START = "user_session_start"
    USER_SESSION_END = "user_session_end"
    VOICE_MESSAGE = "voice_message"
    SCREEN_SHARE = "screen_share"
    COMMAND_MESSAGE = "command_message"
    AI_RESPONSE = "ai_response"
    ERROR_OCCURRED = "error_occurred"
    STEP_COMPLETED = "step_completed"
    STEP_FAILED = "step_failed"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    PERFORMANCE_METRIC = "performance_metric"
    USER_FEEDBACK = "user_feedback"


@dataclass
class MonitoringEvent:
    """Monitoring event data structure"""
    event_id: str
    event_type: EventType
    timestamp: datetime
    session_id: str
    user_id: Optional[str]
    data: Dict[str, Any]
    metadata: Dict[str, Any]


@dataclass
class UserSession:
    """User session tracking"""
    session_id: str
    user_id: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    total_messages: int
    successful_steps: int
    failed_steps: int
    apps_used: List[str]
    tasks_completed: List[str]
    average_response_time: float
    user_satisfaction: Optional[float]


@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: datetime
    active_sessions: int
    total_requests: int
    average_response_time: float
    error_rate: float
    cache_hit_rate: float
    memory_usage: float
    cpu_usage: float


class MonitoringSystem:
    """Comprehensive monitoring and analytics system"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.events_buffer: List[MonitoringEvent] = []
        self.user_sessions: Dict[str, UserSession] = {}
        self.system_metrics: List[SystemMetrics] = []
        self.alert_rules: List[Dict[str, Any]] = []
        self.is_initialized = False
        self.buffer_size = 1000
        self.flush_interval = 30  # seconds
        
        # Setup alert rules
        self._setup_alert_rules()
    
    async def initialize(self):
        """Initialize the monitoring system"""
        try:
            # Connect to Redis
            self.redis_client = redis.from_url(settings.redis_url, db=2)  # Use different DB for monitoring
            await self.redis_client.ping()
            
            # Start background tasks
            self._start_background_tasks()
            
            self.is_initialized = True
            logger.info("Monitoring system initialized")
            
        except Exception as e:
            logger.error(f"Error initializing monitoring system: {e}")
    
    def _setup_alert_rules(self):
        """Setup monitoring alert rules"""
        self.alert_rules = [
            {
                "name": "high_error_rate",
                "condition": "error_rate > 0.1",
                "severity": "warning",
                "message": "Error rate is above 10%"
            },
            {
                "name": "slow_response_time",
                "condition": "avg_response_time > 5.0",
                "severity": "warning",
                "message": "Average response time is above 5 seconds"
            },
            {
                "name": "high_memory_usage",
                "condition": "memory_usage > 0.8",
                "severity": "critical",
                "message": "Memory usage is above 80%"
            },
            {
                "name": "low_cache_hit_rate",
                "condition": "cache_hit_rate < 0.5",
                "severity": "info",
                "message": "Cache hit rate is below 50%"
            },
            {
                "name": "many_active_sessions",
                "condition": "active_sessions > 100",
                "severity": "info",
                "message": "High number of active sessions"
            }
        ]
    
    def _start_background_tasks(self):
        """Start background monitoring tasks"""
        # Event buffer flush task
        asyncio.create_task(self._flush_events_buffer())
        
        # Metrics collection task
        asyncio.create_task(self._collect_system_metrics())
        
        # Alert checking task
        asyncio.create_task(self._check_alerts())
        
        # Data cleanup task
        asyncio.create_task(self._cleanup_old_data())
    
    async def log_event(self, 
                       event_type: EventType,
                       session_id: str,
                       data: Dict[str, Any],
                       user_id: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None):
        """Log a monitoring event"""
        try:
            event = MonitoringEvent(
                event_id=f"{event_type.value}_{int(time.time() * 1000)}",
                event_type=event_type,
                timestamp=datetime.utcnow(),
                session_id=session_id,
                user_id=user_id,
                data=data,
                metadata=metadata or {}
            )
            
            # Add to buffer
            self.events_buffer.append(event)
            
            # Update user session if applicable
            await self._update_user_session(event)
            
            # Flush buffer if it's full
            if len(self.events_buffer) >= self.buffer_size:
                await self._flush_events_buffer()
            
        except Exception as e:
            logger.error(f"Error logging event: {e}")
    
    async def _update_user_session(self, event: MonitoringEvent):
        """Update user session based on event"""
        try:
            session_id = event.session_id
            
            if event.event_type == EventType.USER_SESSION_START:
                self.user_sessions[session_id] = UserSession(
                    session_id=session_id,
                    user_id=event.user_id,
                    start_time=event.timestamp,
                    end_time=None,
                    total_messages=0,
                    successful_steps=0,
                    failed_steps=0,
                    apps_used=[],
                    tasks_completed=[],
                    average_response_time=0.0,
                    user_satisfaction=None
                )
            
            elif event.event_type == EventType.USER_SESSION_END:
                if session_id in self.user_sessions:
                    self.user_sessions[session_id].end_time = event.timestamp
            
            elif session_id in self.user_sessions:
                session = self.user_sessions[session_id]
                
                if event.event_type in [EventType.VOICE_MESSAGE, EventType.SCREEN_SHARE, EventType.COMMAND_MESSAGE]:
                    session.total_messages += 1
                
                elif event.event_type == EventType.STEP_COMPLETED:
                    session.successful_steps += 1
                    if "task" in event.data:
                        session.tasks_completed.append(event.data["task"])
                
                elif event.event_type == EventType.STEP_FAILED:
                    session.failed_steps += 1
                
                elif event.event_type == EventType.AI_RESPONSE:
                    if "response_time" in event.data:
                        # Update average response time
                        total_time = session.average_response_time * (session.total_messages - 1)
                        session.average_response_time = (total_time + event.data["response_time"]) / session.total_messages
                
                elif event.event_type == EventType.USER_FEEDBACK:
                    if "satisfaction" in event.data:
                        session.user_satisfaction = event.data["satisfaction"]
                
                # Update apps used
                if "app_name" in event.data:
                    app_name = event.data["app_name"]
                    if app_name not in session.apps_used:
                        session.apps_used.append(app_name)
            
        except Exception as e:
            logger.error(f"Error updating user session: {e}")
    
    async def _flush_events_buffer(self):
        """Flush events buffer to Redis"""
        while True:
            try:
                await asyncio.sleep(self.flush_interval)
                
                if not self.events_buffer:
                    continue
                
                # Store events in Redis
                events_to_store = self.events_buffer.copy()
                self.events_buffer.clear()
                
                if self.redis_client:
                    # Store events as JSON
                    for event in events_to_store:
                        event_key = f"event:{event.event_id}"
                        event_data = {
                            "event_id": event.event_id,
                            "event_type": event.event_type.value,
                            "timestamp": event.timestamp.isoformat(),
                            "session_id": event.session_id,
                            "user_id": event.user_id,
                            "data": event.data,
                            "metadata": event.metadata
                        }
                        await self.redis_client.setex(event_key, 86400, json.dumps(event_data, cls=DateTimeEncoder))  # Store for 24 hours
                    
                    logger.info(f"Flushed {len(events_to_store)} events to Redis")
                
            except Exception as e:
                logger.error(f"Error flushing events buffer: {e}")
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        while True:
            try:
                await asyncio.sleep(60)  # Collect metrics every minute
                
                # Calculate current metrics
                active_sessions = len([s for s in self.user_sessions.values() if s.end_time is None])
                
                # Get performance metrics from performance optimizer
                from app.services.performance_optimizer import performance_optimizer
                perf_report = performance_optimizer.get_performance_report()
                
                # Get cache metrics
                cache_stats = perf_report.get("cache", {})
                cache_hit_rate = cache_stats.get("hit_rate", 0) / 100
                
                # Create system metrics
                metrics = SystemMetrics(
                    timestamp=datetime.utcnow(),
                    active_sessions=active_sessions,
                    total_requests=perf_report["metrics"]["request_count"],
                    average_response_time=perf_report["metrics"]["avg_response_time"],
                    error_rate=perf_report["metrics"]["error_count"] / max(perf_report["metrics"]["request_count"], 1),
                    cache_hit_rate=cache_hit_rate,
                    memory_usage=0.0,  # Would get from system monitoring
                    cpu_usage=0.0     # Would get from system monitoring
                )
                
                # Store metrics
                self.system_metrics.append(metrics)
                
                # Keep only last 1000 metrics
                if len(self.system_metrics) > 1000:
                    self.system_metrics = self.system_metrics[-1000:]
                
                # Store in Redis
                if self.redis_client:
                    metrics_key = f"metrics:{int(metrics.timestamp.timestamp())}"
                    await self.redis_client.setex(metrics_key, 86400, json.dumps(asdict(metrics), cls=DateTimeEncoder))
                
            except Exception as e:
                logger.error(f"Error collecting system metrics: {e}")
    
    async def _check_alerts(self):
        """Check alert conditions"""
        while True:
            try:
                await asyncio.sleep(300)  # Check alerts every 5 minutes
                
                if not self.system_metrics:
                    continue
                
                # Get latest metrics
                latest_metrics = self.system_metrics[-1]
                
                # Check each alert rule
                for rule in self.alert_rules:
                    if await self._evaluate_alert_condition(rule["condition"], latest_metrics):
                        await self._trigger_alert(rule, latest_metrics)
                
            except Exception as e:
                logger.error(f"Error checking alerts: {e}")
    
    async def _evaluate_alert_condition(self, condition: str, metrics: SystemMetrics) -> bool:
        """Evaluate alert condition"""
        try:
            # Simple condition evaluation - in production, use a proper expression evaluator
            if "error_rate > 0.1" in condition:
                return metrics.error_rate > 0.1
            elif "avg_response_time > 5.0" in condition:
                return metrics.average_response_time > 5.0
            elif "memory_usage > 0.8" in condition:
                return metrics.memory_usage > 0.8
            elif "cache_hit_rate < 0.5" in condition:
                return metrics.cache_hit_rate < 0.5
            elif "active_sessions > 100" in condition:
                return metrics.active_sessions > 100
            
            return False
            
        except Exception as e:
            logger.error(f"Error evaluating alert condition: {e}")
            return False
    
    async def _trigger_alert(self, rule: Dict[str, Any], metrics: SystemMetrics):
        """Trigger an alert"""
        try:
            alert_data = {
                "rule_name": rule["name"],
                "severity": rule["severity"],
                "message": rule["message"],
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": asdict(metrics)
            }
            
            # Log alert
            logger.warning(f"ALERT: {rule['message']} (Severity: {rule['severity']})")
            
            # Store alert in Redis
            if self.redis_client:
                alert_key = f"alert:{rule['name']}:{int(time.time())}"
                await self.redis_client.setex(alert_key, 86400, json.dumps(alert_data, cls=DateTimeEncoder))
            
            # In production, you would also send notifications (email, Slack, etc.)
            
        except Exception as e:
            logger.error(f"Error triggering alert: {e}")
    
    async def _cleanup_old_data(self):
        """Cleanup old monitoring data"""
        while True:
            try:
                await asyncio.sleep(3600)  # Cleanup every hour
                
                # Cleanup old user sessions
                cutoff_time = datetime.utcnow() - timedelta(days=7)
                sessions_to_remove = [
                    session_id for session_id, session in self.user_sessions.items()
                    if session.end_time and session.end_time < cutoff_time
                ]
                
                for session_id in sessions_to_remove:
                    del self.user_sessions[session_id]
                
                if sessions_to_remove:
                    logger.info(f"Cleaned up {len(sessions_to_remove)} old user sessions")
                
                # Cleanup old system metrics
                if len(self.system_metrics) > 1000:
                    self.system_metrics = self.system_metrics[-1000:]
                
            except Exception as e:
                logger.error(f"Error cleaning up old data: {e}")
    
    async def get_analytics_report(self, 
                                 start_time: Optional[datetime] = None,
                                 end_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Get comprehensive analytics report"""
        try:
            if not start_time:
                start_time = datetime.utcnow() - timedelta(days=7)
            if not end_time:
                end_time = datetime.utcnow()
            
            # Filter metrics by time range
            filtered_metrics = [
                m for m in self.system_metrics
                if start_time <= m.timestamp <= end_time
            ]
            
            # Filter sessions by time range
            filtered_sessions = [
                s for s in self.user_sessions.values()
                if s.start_time >= start_time and (s.end_time is None or s.end_time <= end_time)
            ]
            
            # Calculate analytics
            total_sessions = len(filtered_sessions)
            active_sessions = len([s for s in filtered_sessions if s.end_time is None])
            completed_sessions = len([s for s in filtered_sessions if s.end_time is not None])
            
            total_messages = sum(s.total_messages for s in filtered_sessions)
            total_successful_steps = sum(s.successful_steps for s in filtered_sessions)
            total_failed_steps = sum(s.failed_steps for s in filtered_sessions)
            
            success_rate = total_successful_steps / max(total_successful_steps + total_failed_steps, 1) * 100
            
            # App usage statistics
            app_usage = {}
            for session in filtered_sessions:
                for app in session.apps_used:
                    app_usage[app] = app_usage.get(app, 0) + 1
            
            # Task completion statistics
            task_completion = {}
            for session in filtered_sessions:
                for task in session.tasks_completed:
                    task_completion[task] = task_completion.get(task, 0) + 1
            
            # Performance metrics
            if filtered_metrics:
                avg_response_time = sum(m.average_response_time for m in filtered_metrics) / len(filtered_metrics)
                avg_error_rate = sum(m.error_rate for m in filtered_metrics) / len(filtered_metrics)
                avg_cache_hit_rate = sum(m.cache_hit_rate for m in filtered_metrics) / len(filtered_metrics)
            else:
                avg_response_time = 0.0
                avg_error_rate = 0.0
                avg_cache_hit_rate = 0.0
            
            # User satisfaction
            satisfaction_scores = [s.user_satisfaction for s in filtered_sessions if s.user_satisfaction is not None]
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else None
            
            return {
                "time_range": {
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat()
                },
                "sessions": {
                    "total": total_sessions,
                    "active": active_sessions,
                    "completed": completed_sessions
                },
                "interactions": {
                    "total_messages": total_messages,
                    "successful_steps": total_successful_steps,
                    "failed_steps": total_failed_steps,
                    "success_rate": success_rate
                },
                "performance": {
                    "avg_response_time": avg_response_time,
                    "avg_error_rate": avg_error_rate,
                    "avg_cache_hit_rate": avg_cache_hit_rate
                },
                "usage": {
                    "app_usage": app_usage,
                    "task_completion": task_completion
                },
                "user_satisfaction": {
                    "avg_satisfaction": avg_satisfaction,
                    "total_ratings": len(satisfaction_scores)
                },
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            return {"error": str(e)}
    
    async def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get real-time dashboard data"""
        try:
            # Current active sessions
            active_sessions = len([s for s in self.user_sessions.values() if s.end_time is None])
            
            # Recent events (last 100)
            recent_events = self.events_buffer[-100:] if self.events_buffer else []
            
            # Latest system metrics
            latest_metrics = self.system_metrics[-1] if self.system_metrics else None
            
            # Recent alerts
            recent_alerts = []  # Would get from Redis in production
            
            return {
                "active_sessions": active_sessions,
                "recent_events": [
                    {
                        "type": event.event_type.value,
                        "timestamp": event.timestamp.isoformat(),
                        "session_id": event.session_id
                    } for event in recent_events
                ],
                "system_metrics": asdict(latest_metrics) if latest_metrics else None,
                "recent_alerts": recent_alerts,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting real-time dashboard: {e}")
            return {"error": str(e)}
    
    async def cleanup(self):
        """Cleanup monitoring system resources"""
        try:
            # Flush remaining events
            await self._flush_events_buffer()
            
            # Close Redis connection
            if self.redis_client:
                await self.redis_client.close()
            
            logger.info("Monitoring system cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up monitoring system: {e}")


# Global monitoring system instance
monitoring_system = MonitoringSystem()
