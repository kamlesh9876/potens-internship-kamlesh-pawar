import time
from collections import defaultdict
from typing import Dict, Any
from app.cache.cache import cache


class Metrics:
    """Simple metrics collection"""
    
    def __init__(self):
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.response_times = []
        self.endpoint_counts = defaultdict(int)
        self.start_time = time.time()
    
    def record_request(self, endpoint: str, status_code: int, response_time: float):
        """Record a request"""
        self.request_count += 1
        self.endpoint_counts[endpoint] += 1
        
        if 200 <= status_code < 400:
            self.success_count += 1
        else:
            self.error_count += 1
        
        self.response_times.append(response_time)
        
        # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        uptime = time.time() - self.start_time
        
        cache_stats = cache.get_stats()
        
        return {
            "uptime_seconds": int(uptime),
            "uptime_formatted": f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m",
            "total_requests": self.request_count,
            "successful_requests": self.success_count,
            "failed_requests": self.error_count,
            "success_rate": f"{(self.success_count / self.request_count * 100):.2f}%" if self.request_count > 0 else "0%",
            "average_response_time_ms": f"{avg_response_time * 1000:.2f}",
            "requests_per_endpoint": dict(self.endpoint_counts),
            "cache": cache_stats
        }


# Global metrics instance
metrics = Metrics()
