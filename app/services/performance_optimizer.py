"""
Performance optimization system for SafeHands backend
"""
import asyncio
import time
import json
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import logging
from functools import wraps
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Performance metrics tracking"""
    def __init__(self):
        self.request_count = 0
        self.total_response_time = 0.0
        self.avg_response_time = 0.0
        self.max_response_time = 0.0
        self.min_response_time = float('inf')
        self.error_count = 0
        self.success_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.last_updated = datetime.utcnow()


class CacheManager:
    """Intelligent caching system"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.local_cache: Dict[str, Any] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0
        }
        self.ttl_default = 300  # 5 minutes
        self.max_local_cache_size = 1000
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(settings.redis_url, db=1)  # Use different DB for cache
            await self.redis_client.ping()
            logger.info("Cache manager connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis cache: {e}")
            self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            # Try local cache first
            if key in self.local_cache:
                self.cache_stats["hits"] += 1
                return self.local_cache[key]
            
            # Try Redis cache
            if self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    try:
                        data = json.loads(value)
                        # Store in local cache for faster access
                        self._set_local_cache(key, data)
                        self.cache_stats["hits"] += 1
                        return data
                    except json.JSONDecodeError:
                        pass
            
            self.cache_stats["misses"] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            self.cache_stats["misses"] += 1
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache"""
        try:
            ttl = ttl or self.ttl_default
            
            # Store in local cache
            self._set_local_cache(key, value)
            
            # Store in Redis cache
            if self.redis_client:
                await self.redis_client.setex(key, ttl, json.dumps(value))
            
            self.cache_stats["sets"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            # Remove from local cache
            if key in self.local_cache:
                del self.local_cache[key]
            
            # Remove from Redis cache
            if self.redis_client:
                await self.redis_client.delete(key)
            
            self.cache_stats["deletes"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    def _set_local_cache(self, key: str, value: Any):
        """Set value in local cache with size management"""
        # Remove oldest entries if cache is full
        if len(self.local_cache) >= self.max_local_cache_size:
            # Remove 10% of oldest entries
            keys_to_remove = list(self.local_cache.keys())[:self.max_local_cache_size // 10]
            for k in keys_to_remove:
                del self.local_cache[k]
        
        self.local_cache[key] = value
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        hit_rate = (self.cache_stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "hits": self.cache_stats["hits"],
            "misses": self.cache_stats["misses"],
            "hit_rate": hit_rate,
            "sets": self.cache_stats["sets"],
            "deletes": self.cache_stats["deletes"],
            "local_cache_size": len(self.local_cache)
        }


class PerformanceOptimizer:
    """Performance optimization system"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.metrics = PerformanceMetrics()
        self.optimization_rules = []
        self.background_tasks = set()
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize the performance optimizer"""
        try:
            await self.cache_manager.connect()
            self._setup_optimization_rules()
            self._start_background_tasks()
            self.is_initialized = True
            logger.info("Performance optimizer initialized")
        except Exception as e:
            logger.error(f"Error initializing performance optimizer: {e}")
    
    def _setup_optimization_rules(self):
        """Setup performance optimization rules"""
        self.optimization_rules = [
            {
                "name": "cache_ai_responses",
                "enabled": True,
                "cache_ttl": 3600,  # 1 hour
                "conditions": ["ai_service", "similar_queries"]
            },
            {
                "name": "cache_screen_analysis",
                "enabled": True,
                "cache_ttl": 1800,  # 30 minutes
                "conditions": ["screen_analysis", "similar_screens"]
            },
            {
                "name": "batch_processing",
                "enabled": True,
                "batch_size": 5,
                "batch_timeout": 1.0,  # 1 second
                "conditions": ["multiple_requests", "similar_operations"]
            },
            {
                "name": "connection_pooling",
                "enabled": True,
                "pool_size": 10,
                "max_overflow": 20,
                "conditions": ["database_operations", "external_api_calls"]
            }
        ]
    
    def _start_background_tasks(self):
        """Start background optimization tasks"""
        # Metrics collection task
        task = asyncio.create_task(self._collect_metrics())
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
        
        # Cache cleanup task
        task = asyncio.create_task(self._cleanup_cache())
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
        
        # Performance analysis task
        task = asyncio.create_task(self._analyze_performance())
        self.background_tasks.add(task)
        task.add_done_callback(self.background_tasks.discard)
    
    async def _collect_metrics(self):
        """Collect performance metrics"""
        while True:
            try:
                await asyncio.sleep(60)  # Collect metrics every minute
                
                # Update metrics
                current_time = datetime.utcnow()
                if self.metrics.request_count > 0:
                    self.metrics.avg_response_time = self.metrics.total_response_time / self.metrics.request_count
                
                self.metrics.last_updated = current_time
                
                # Log performance summary
                logger.info(f"Performance metrics - Avg response time: {self.metrics.avg_response_time:.2f}s, "
                           f"Success rate: {self.metrics.success_count / max(self.metrics.request_count, 1) * 100:.1f}%")
                
            except Exception as e:
                logger.error(f"Error collecting metrics: {e}")
    
    async def _cleanup_cache(self):
        """Cleanup expired cache entries"""
        while True:
            try:
                await asyncio.sleep(300)  # Cleanup every 5 minutes
                
                # Cleanup local cache
                current_time = time.time()
                expired_keys = []
                
                for key, value in self.cache_manager.local_cache.items():
                    if isinstance(value, dict) and "expires_at" in value:
                        if value["expires_at"] < current_time:
                            expired_keys.append(key)
                
                for key in expired_keys:
                    del self.cache_manager.local_cache[key]
                
                if expired_keys:
                    logger.info(f"Cleaned up {len(expired_keys)} expired cache entries")
                
            except Exception as e:
                logger.error(f"Error cleaning up cache: {e}")
    
    async def _analyze_performance(self):
        """Analyze performance and suggest optimizations"""
        while True:
            try:
                await asyncio.sleep(600)  # Analyze every 10 minutes
                
                # Analyze performance trends
                if self.metrics.avg_response_time > 5.0:  # If avg response time > 5s
                    logger.warning("High response time detected, consider optimization")
                
                if self.metrics.error_count / max(self.metrics.request_count, 1) > 0.1:  # If error rate > 10%
                    logger.warning("High error rate detected, check system health")
                
                # Cache hit rate analysis
                cache_stats = self.cache_manager.get_stats()
                if cache_stats["hit_rate"] < 50:  # If cache hit rate < 50%
                    logger.info("Low cache hit rate, consider cache optimization")
                
            except Exception as e:
                logger.error(f"Error analyzing performance: {e}")
    
    def track_performance(self, operation_name: str):
        """Decorator to track performance of operations"""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                start_time = time.time()
                success = False
                
                try:
                    result = await func(*args, **kwargs)
                    success = True
                    return result
                except Exception as e:
                    logger.error(f"Error in {operation_name}: {e}")
                    raise
                finally:
                    end_time = time.time()
                    response_time = end_time - start_time
                    
                    # Update metrics
                    self.metrics.request_count += 1
                    self.metrics.total_response_time += response_time
                    self.metrics.max_response_time = max(self.metrics.max_response_time, response_time)
                    self.metrics.min_response_time = min(self.metrics.min_response_time, response_time)
                    
                    if success:
                        self.metrics.success_count += 1
                    else:
                        self.metrics.error_count += 1
                    
                    # Log slow operations
                    if response_time > 3.0:  # Log operations taking > 3 seconds
                        logger.warning(f"Slow operation: {operation_name} took {response_time:.2f}s")
            
            return wrapper
        return decorator
    
    async def optimize_ai_request(self, prompt: str, model: str, **kwargs) -> Any:
        """Optimize AI requests with caching"""
        try:
            # Create cache key
            cache_key = f"ai_request:{hash(prompt + model + str(kwargs))}"
            
            # Try to get from cache
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                logger.info("AI request served from cache")
                return cached_result
            
            # Make AI request
            from app.services.ai_service import ai_service
            result = await ai_service.generate_text(prompt, model, **kwargs)
            
            # Cache the result
            await self.cache_manager.set(cache_key, result, ttl=3600)  # Cache for 1 hour
            
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing AI request: {e}")
            # Fallback to direct AI request
            from app.services.ai_service import ai_service
            return await ai_service.generate_text(prompt, model, **kwargs)
    
    async def optimize_screen_analysis(self, screenshot_data: bytes, context: Dict[str, Any]) -> Any:
        """Optimize screen analysis with caching"""
        try:
            # Create cache key based on image hash
            import hashlib
            image_hash = hashlib.md5(screenshot_data).hexdigest()
            cache_key = f"screen_analysis:{image_hash}"
            
            # Try to get from cache
            cached_result = await self.cache_manager.get(cache_key)
            if cached_result:
                logger.info("Screen analysis served from cache")
                return cached_result
            
            # Perform screen analysis
            from app.services.screen_analyzer import ScreenAnalyzer
            analyzer = ScreenAnalyzer()
            result = await analyzer.analyze_screen(screenshot_data, context)
            
            # Cache the result
            await self.cache_manager.set(cache_key, result.model_dump(), ttl=1800)  # Cache for 30 minutes
            
            return result
            
        except Exception as e:
            logger.error(f"Error optimizing screen analysis: {e}")
            # Fallback to direct analysis
            from app.services.screen_analyzer import ScreenAnalyzer
            analyzer = ScreenAnalyzer()
            return await analyzer.analyze_screen(screenshot_data, context)
    
    async def batch_process_requests(self, requests: List[Dict[str, Any]]) -> List[Any]:
        """Batch process multiple requests for efficiency"""
        try:
            if len(requests) < 2:
                # Process individually if less than 2 requests
                results = []
                for request in requests:
                    result = await self._process_single_request(request)
                    results.append(result)
                return results
            
            # Group similar requests
            grouped_requests = self._group_similar_requests(requests)
            
            # Process each group
            results = []
            for group in grouped_requests:
                if len(group) > 1:
                    # Batch process
                    batch_result = await self._process_batch(group)
                    results.extend(batch_result)
                else:
                    # Process individually
                    result = await self._process_single_request(group[0])
                    results.append(result)
            
            return results
            
        except Exception as e:
            logger.error(f"Error batch processing requests: {e}")
            # Fallback to individual processing
            results = []
            for request in requests:
                result = await self._process_single_request(request)
                results.append(result)
            return results
    
    def _group_similar_requests(self, requests: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group similar requests for batch processing"""
        groups = []
        current_group = []
        
        for request in requests:
            if not current_group:
                current_group = [request]
            elif self._are_requests_similar(current_group[0], request):
                current_group.append(request)
            else:
                groups.append(current_group)
                current_group = [request]
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _are_requests_similar(self, req1: Dict[str, Any], req2: Dict[str, Any]) -> bool:
        """Check if two requests are similar enough for batch processing"""
        # Simple similarity check - in production, use more sophisticated logic
        return (req1.get("type") == req2.get("type") and 
                req1.get("app_context") == req2.get("app_context"))
    
    async def _process_batch(self, requests: List[Dict[str, Any]]) -> List[Any]:
        """Process a batch of similar requests"""
        # Simplified batch processing - in production, implement actual batching
        results = []
        for request in requests:
            result = await self._process_single_request(request)
            results.append(result)
        return results
    
    async def _process_single_request(self, request: Dict[str, Any]) -> Any:
        """Process a single request"""
        # This would route to appropriate handler based on request type
        return {"processed": True, "request": request}
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        cache_stats = self.cache_manager.get_stats()
        
        return {
            "metrics": {
                "request_count": self.metrics.request_count,
                "avg_response_time": self.metrics.avg_response_time,
                "max_response_time": self.metrics.max_response_time,
                "min_response_time": self.metrics.min_response_time if self.metrics.min_response_time != float('inf') else 0,
                "error_count": self.metrics.error_count,
                "success_count": self.metrics.success_count,
                "success_rate": self.metrics.success_count / max(self.metrics.request_count, 1) * 100
            },
            "cache": cache_stats,
            "optimization_rules": [
                {
                    "name": rule["name"],
                    "enabled": rule["enabled"]
                } for rule in self.optimization_rules
            ],
            "background_tasks": len(self.background_tasks),
            "last_updated": self.metrics.last_updated.isoformat()
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            # Cancel background tasks
            for task in self.background_tasks:
                task.cancel()
            
            # Wait for tasks to complete
            if self.background_tasks:
                await asyncio.gather(*self.background_tasks, return_exceptions=True)
            
            # Close Redis connection
            if self.cache_manager.redis_client:
                await self.cache_manager.redis_client.close()
            
            logger.info("Performance optimizer cleaned up")
            
        except Exception as e:
            logger.error(f"Error cleaning up performance optimizer: {e}")


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()
