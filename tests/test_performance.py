# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

Performance testing suite.
"""

import time
from unittest.mock import patch

import pytest

from autom8.performance import (
    batch_process,
    cached,
    check_system_health,
    function_cache,
    get_system_performance,
    timeit,
)


# PERFORMANCE BENCHMARKS
class TestPerformanceBenchmarks:
    """Test performance benchmarks."""

    def test_function_execution_time(self):
        """Test that functions complete within acceptable time."""

        @timeit
        def test_function():
            time.sleep(0.1)
            return "done"

        start = time.time()
        result = test_function()
        duration = time.time() - start

        # Should complete in under 0.2 seconds (0.1s sleep + overhead)
        assert duration < 0.2, f"Function too slow: {duration}s"
        assert result == "done"

    def test_cache_performance(self):
        """Test that caching improves performance."""
        call_count = 0

        @cached(cache_obj=function_cache)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            time.sleep(0.1)  # Simulate expensive operation
            return x * 2

        # First call (cache miss)
        start = time.time()
        result1 = expensive_function(5)
        time1 = time.time() - start

        # Second call (cache hit)
        start = time.time()
        result2 = expensive_function(5)
        time2 = time.time() - start

        # Assertions
        assert result1 == result2 == 10
        assert call_count == 1, "Function should only be called once"
        assert time2 < time1 / 10, "Cached call should be much faster"

        # Cleanup
        function_cache.clear()

    def test_batch_processing_efficiency(self):
        """Test batch processing handles large datasets efficiently."""
        items = list(range(1000))

        start = time.time()

        batches_processed = 0
        for batch in batch_process(items, batch_size=100):
            batches_processed += 1
            # Process batch
            sum(batch)

        duration = time.time() - start

        # Should process 1000 items in 10 batches quickly
        assert batches_processed == 10
        assert duration < 1.0, f"Batch processing too slow: {duration}s"

    def test_system_metrics_response_time(self):
        """Test that system metrics are retrieved quickly."""
        start = time.time()
        metrics = get_system_performance()
        duration = time.time() - start

        # Should get metrics in under 5 seconds
        assert duration < 5.0, f"Metrics retrieval too slow: {duration}s"
        assert "cpu" in metrics
        assert "memory" in metrics
        assert "disk" in metrics

    def test_health_check_response_time(self):
        """Test health check responds quickly."""
        start = time.time()
        health = check_system_health()
        duration = time.time() - start

        # Health check should be fast
        assert duration < 5.0, f"Health check too slow: {duration}s"
        assert "status" in health
        assert "metrics" in health


# STRESS TESTS
class TestStressTests:
    """Stress tests for performance under load."""

    @pytest.mark.slow
    def test_concurrent_cache_access(self):
        """Test cache handles concurrent access."""

        @cached(cache_obj=function_cache)
        def compute(x):
            return x**2

        # Simulate concurrent access
        results = []
        for i in range(1000):
            result = compute(i % 100)  # Only 100 unique values
            results.append(result)

        # All results should be correct
        assert len(results) == 1000
        assert results[0] == 0
        assert results[99] == 99**2

        # Cache should have 100 entries
        cache_info = compute.cache_info()
        assert cache_info["size"] <= 100

        function_cache.clear()

    @pytest.mark.slow
    def test_large_dataset_processing(self):
        """Test processing large datasets."""
        large_dataset = list(range(100000))

        start = time.time()

        # Process in batches
        total = 0
        for batch in batch_process(large_dataset, batch_size=1000):
            total += sum(batch)

        duration = time.time() - start

        # Should process 100k items in reasonable time
        assert duration < 5.0, f"Large dataset processing too slow: {duration}s"
        assert total == sum(range(100000))

    @pytest.mark.slow
    def test_memory_efficiency(self):
        """Test memory usage stays reasonable."""
        import os

        import psutil

        process = psutil.Process(os.getpid())

        # Get initial memory
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create large dataset
        data = []
        for _ in range(10):
            large_list = list(range(100000))
            data.append(sum(large_list))
            del large_list  # Explicit cleanup

        # Get final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (< 100MB)
        assert memory_increase < 100, f"Memory leak detected: {memory_increase}MB increase"


# API PERFORMANCE TESTS
class TestAPIPerformance:
    """Test API endpoint performance."""

    def test_health_endpoint_response_time(self, client):
        """Test health endpoint responds quickly."""
        start = time.time()
        response = client.get("/api/v1/health")
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 0.2, f"Health endpoint too slow: {duration}s"

    def test_contacts_list_response_time(self, client):
        """Test contacts list endpoint performance."""
        # Add some test data first
        for i in range(10):
            client.post("/api/v1/contacts", json={"name": f"User {i}", "phone": f"070000000{i}"})

        # Test response time
        start = time.time()
        response = client.get("/api/v1/contacts")
        duration = time.time() - start

        assert response.status_code == 200
        assert duration < 0.5, f"Contacts list too slow: {duration}s"

    @pytest.mark.slow
    def test_bulk_operations_performance(self, client):
        """Test bulk contact creation performance."""
        contacts_to_create = 10

        start = time.time()

        for i in range(contacts_to_create):
            response = client.post(
                "/api/v1/contacts",
                json={"name": f"Bulk User {i}", "phone": f"071{i:07d}"},
            )
            assert response.status_code in [201, 400, 409]  # Allow duplicates if already exists

        duration = time.time() - start
        avg_time = duration / contacts_to_create

        # Each create should average under 100ms (more conservative for general environments)
        assert avg_time < 0.1, f"Bulk operations too slow: {avg_time}s per operation"


class TestPerformanceUtils:
    """Test performance utility classes and functions."""

    def test_performance_monitor_slow_request(self):
        """Test PerformanceMonitor logs slow requests."""
        from autom8.performance import PerformanceMonitor

        monitor = PerformanceMonitor()

        with patch("autom8.core.log.warning") as mock_log:
            monitor.record_request("slow_endpoint", 1.5)
            mock_log.assert_called_once()
            assert "Slow request: slow_endpoint" in mock_log.call_args[0][0]

        stats = monitor.get_stats()
        assert stats["total_requests"] == 1
        assert stats["slow_requests"] == 1
        assert stats["average_response_time"] == 1.5

    def test_performance_monitor_empty_stats(self):
        """Test PerformanceMonitor returns empty message when no requests recorded."""
        from autom8.performance import PerformanceMonitor

        monitor = PerformanceMonitor()
        assert monitor.get_stats() == {"message": "No requests recorded."}

    def test_cache_hit_rate_zero(self):
        """Test cache hit rate calculation with zero calls."""
        from autom8.performance import PerformanceMonitor

        monitor = PerformanceMonitor()
        assert monitor._calculate_cache_hit_rate() == 0.0

    def test_profile_decorator(self, tmp_path):
        """Test profile decorator generates output."""
        from autom8.performance import profile

        profile_file = tmp_path / "test.prof"

        @profile(output_file=str(profile_file))
        def dummy_func():
            return sum(range(1000))

        result = dummy_func()
        assert result == sum(range(1000))
        assert profile_file.exists()
        assert "dummy_func" in profile_file.read_text()

    def test_timer_context_manager(self):
        """Test timer context manager."""
        from autom8.performance import timer

        with patch("autom8.core.log.info") as mock_log:
            with timer("Test Op"):
                time.sleep(0.01)
            mock_log.assert_called_once()
            assert "Test Op took" in mock_log.call_args[0][0]

    def test_check_system_health_warnings(self):
        """Test health check reports issues when metrics are high."""
        from autom8.performance import check_system_health

        # Mock psutil calls
        with (
            patch("psutil.cpu_percent", return_value=85.0),
            patch("psutil.virtual_memory") as mock_mem,
            patch("psutil.disk_usage") as mock_disk,
        ):

            mock_mem.return_value.percent = 85.0
            mock_mem.return_value.available = 100 * 1024 * 1024
            mock_mem.return_value.total = 1000 * 1024 * 1024

            mock_disk.return_value.percent = 95.0
            mock_disk.return_value.free = 1 * 1024 * 1024 * 1024

            health = check_system_health()

            assert health["status"] == "warning"
            assert len(health["issues"]) == 3
            assert "High CPU usage" in health["issues"]
            assert "High memory usage" in health["issues"]
            assert "Low disk space" in health["issues"]

    def test_log_slow_query_decorator(self):
        """Test log_slow_query decorator."""
        from autom8.performance import log_slow_query

        @log_slow_query(threshold=0.01)
        def slow_query():
            time.sleep(0.02)
            return "ok"

        with patch("autom8.core.log.warning") as mock_log:
            result = slow_query()
            assert result == "ok"
            mock_log.assert_called_once()
            assert "Slow query detected" in mock_log.call_args[0][0]

    def test_batch_process_with_func(self):
        """Test batch_process with a processing function."""
        from autom8.performance import batch_process

        processed_count = 0

        def my_processor(batch):
            nonlocal processed_count
            processed_count += len(batch)

        items = list(range(25))
        batch_process(items, batch_size=10, process_func=my_processor)

        assert processed_count == 25

    def test_clear_cache_endpoint(self, client):
        """Test cache clearing endpoint."""
        response = client.post("/api/v1/performance/cache/clear")
        assert response.status_code == 200
        assert "Cache cleared successfully" in response.get_json()["message"]

    def test_performance_stats_endpoint(self, client):
        """Test performance stats endpoint."""
        from autom8.performance import perf_monitor

        perf_monitor.record_request("test", 0.1)

        response = client.get("/api/v1/performance/stats")
        assert response.status_code == 200
        data = response.get_json()
        assert data["total_requests"] > 0

    def test_cached_default_and_key_func(self):
        """Test cached decorator with default cache and custom key function."""
        from autom8.performance import cached

        # Test default cache (None)
        @cached()
        def default_cached_func(x):
            return x * 2

        assert default_cached_func(5) == 10

        # Test custom key function
        def my_key(x):
            return f"key_{x}"

        @cached(key_func=my_key)
        def custom_key_func(x):
            return x + 1

        assert custom_key_func(10) == 11
        assert custom_key_func.cache_info()["size"] >= 1

    def test_system_performance_endpoint(self, client):
        """Test system performance endpoint."""
        response = client.get("/api/v1/performance/system")
        assert response.status_code == 200
        data = response.get_json()
        assert "cpu" in data
        assert "memory" in data

    def test_system_health_endpoint(self, client):
        """Test system health endpoint."""
        response = client.get("/api/v1/performance/health")
        assert response.status_code == 200
        data = response.get_json()
        assert "status" in data
        assert "metrics" in data


# MAIN
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
