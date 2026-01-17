# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

Performance monitoring and optimization utilities for the autom8 package.
"""

import cProfile
import functools
import io
import pstats
import time
from contextlib import contextmanager
from datetime import datetime
from typing import Callable, Optional

import psutil
from cachetools import LRUCache, TTLCache

from autom8.core import log


# PERFORMANCE MONITORING
class PerformanceMonitor:
    """Monitor and track performance metrics."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = {"requests": [], "slow_queries": [], "cache_hits": 0, "cache_misses": 0}

    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate percentage."""
        total = self.metrics["cache_hits"] + self.metrics["cache_misses"]
        if total == 0:
            return 0.0
        return (self.metrics["cache_hits"] / total) * 100

    def record_request(self, endpoint: str, duration: float):
        """Record a request with its endpoint and duration."""
        self.metrics["requests"].append(
            {"endpoint": endpoint, "duration": duration, "timestamp": datetime.now()}
        )

        # Log slow requests
        if duration > 1.0:  # Slower than 1 second
            log.warning(f"Slow request: {endpoint} took {duration:.2f}s")
            self.metrics["slow_queries"].append(
                {"endpoint": endpoint, "duration": duration, "timestamp": datetime.now()}
            )

    def get_stats(self) -> dict:
        """Get performance statistics."""
        if not self.metrics["requests"]:
            return {"message": "No requests recorded."}

        durations = sorted([r["duration"] for r in self.metrics["requests"]])
        n = len(durations)

        return {
            "total_requests": len(self.metrics["requests"]),
            "average_response_time": sum(durations) / len(durations),
            "min_response_time": min(durations),
            "max_response_time": max(durations),
            "slow_requests": len(self.metrics["slow_queries"]),
            "cache_hit_rate": self._calculate_cache_hit_rate(),
            "p50": durations[int(n * 0.5)] if n > 0 else 0,
            "p90": durations[int(n * 0.9)] if n else 0,
            "p99": durations[int(n * 0.99)] if n else 0,
        }


# Global performance monitor instance
perf_monitor = PerformanceMonitor()


# TIMING DECORATORS
def timeit(func: Callable) -> Callable:
    """Decorator to measure function execution time."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time

        log.info(f"{func.__name__} took {duration:.4f}s")

        return result

    return wrapper


def profile(output_file: Optional[str] = None):
    """Decorator to profile function with cProfile."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            profiler = cProfile.Profile()
            profiler.enable()

            result = func(*args, **kwargs)

            profiler.disable()

            # Print stats
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s).sort_stats("cumulative")
            ps.print_stats(20)  # Top 20 functions

            profile_output = s.getvalue()
            log.info(f"\nProfile for {func.__name__}:\n{profile_output}")

            # Save to file if specified
            if output_file:
                with open(output_file, "w") as f:
                    f.write(profile_output)

            return result

        return wrapper

    return decorator


@contextmanager
def timer(name: str = "Operation"):
    """Context manager for timing blocks."""
    start_time = time.time()
    try:
        yield
    finally:
        duration = time.time() - start_time
        log.info(f"{name} took {duration:.4f}s")


# CACHING

# LRU Cache for function results (in-memory)
function_cache = LRUCache(maxsize=256)

# TTL Cache for time-sensitive data (short duration for responsiveness)
timed_cache = TTLCache(maxsize=128, ttl=10)  # 10 seconds


def cached(cache_obj=None, key_func=None):
    """Decorator for caching function results."""
    if cache_obj is None:
        cache_obj = function_cache

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Include function name to prevent collisions between different decorated functions
                func_path = f"{func.__module__}.{func.__name__}"
                args_str = str((args, tuple(sorted(kwargs.items()))))
                cache_key = f"{func_path}:{args_str}"

            # Check cache
            if cache_key in cache_obj:
                perf_monitor.metrics["cache_hits"] += 1
                log.debug(f"Cache HIT: {func.__name__}")
                return cache_obj[cache_key]

            # Cache miss: Compute result
            perf_monitor.metrics["cache_misses"] += 1
            log.debug(f"Cache MISS: {func.__name__}")
            result = func(*args, **kwargs)

            # Store in cache
            cache_obj[cache_key] = result

            return result

        # Add cache_clear method
        wrapper.cache_clear = lambda: cache_obj.clear()
        wrapper.cache_info = lambda: {"size": len(cache_obj), "maxsize": cache_obj.maxsize}

        return wrapper

    return decorator


# SYSTEM METRICS
def get_system_performance() -> dict:
    """Get current system performance metrics."""
    return {
        "cpu": {
            "percent": psutil.cpu_percent(interval=None),
            "count": psutil.cpu_count(),
        },
        "memory": {
            "percent": psutil.virtual_memory().percent,
            "available_mb": psutil.virtual_memory().available / (1024 * 1024),
            "total_mb": psutil.virtual_memory().total / (1024 * 1024),
        },
        "disk": {
            "percent": psutil.disk_usage("/").percent,
            "free_gb": psutil.disk_usage("/").free / (1024 * 1024 * 1024),
        },
        "timestamp": datetime.now().isoformat(),
    }


def check_system_health() -> dict:
    """Check if system is healthy."""
    metrics = get_system_performance()

    issues = []
    recommendations = []

    # Check CPU
    if metrics["cpu"]["percent"] > 80:
        issues.append("High CPU usage")
        recommendations.append("Consider scaling horizontally or optimizing hot paths")

    # Check memory
    if metrics["memory"]["percent"] > 80:
        issues.append("High memory usage")
        recommendations.append("Check for memory leaks or increase RAM")

    # Check disk
    if metrics["disk"]["percent"] > 90:
        issues.append("Low disk space")
        recommendations.append("Clean up old logs or backups")

    status = "healthy" if not issues else "warning"

    return {
        "status": status,
        "issues": issues,
        "recommendations": recommendations,
        "metrics": metrics,
    }


# QUERY OPTIMIZATION
def log_slow_query(threshold: float = 0.1):
    """Decorator to log slow queries."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time

            if duration > threshold:
                log.warning(
                    f"Slow query detected: {func.__name__} took {duration:.4f}s "
                    f"(threshold: {threshold}s)"
                )
                perf_monitor.record_request(func.__name__, duration)

            return result

        return wrapper

    return decorator


# BATCH PROCESSING
def batch_process(items: list, batch_size: int = 100, process_func: Callable = None):
    """Process large lists in batches to avoid memory issues."""

    def _gen():
        total = len(items)
        for i in range(0, total, batch_size):
            yield items[i : i + batch_size]

    if process_func:
        total = len(items)
        for i, batch in enumerate(_gen()):
            log.info(f"Processing batch {i + 1}/{(total - 1) // batch_size + 1}")
            process_func(batch)
    else:
        return _gen()


# EXPORTS
__all__ = [
    "PerformanceMonitor",
    "perf_monitor",
    "timeit",
    "profile",
    "timer",
    "cached",
    "function_cache",
    "timed_cache",
    "get_system_performance",
    "check_system_health",
    "log_slow_query",
    "batch_process",
]
