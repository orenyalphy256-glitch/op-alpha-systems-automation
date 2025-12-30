# Copyright (c) 2025 Alphonce Liguori Oreny. All rights reserved.
# This software is proprietary and confidential.
# Unauthorized copying of this file, via any medium is strictly prohibited.

"""

Performance profiling examples.
"""

import time
import cProfile
import pstats
import io
from functools import lru_cache
from memory_profiler import profile as memory_profile

from autom8.performance import timeit, timer, cached, function_cache


# EXAMPLE 1: CPU-INTENSIVE FUNCTION
def fibonacci_slow(n):
    """Slow recursive fibonacci (no caching)."""
    if n < 2:
        return n
    return fibonacci_slow(n - 1) + fibonacci_slow(n - 2)


@lru_cache(maxsize=128)
def fibonacci_fast(n):
    """Fast fibonacci with caching."""
    if n < 2:
        return n
    return fibonacci_fast(n - 1) + fibonacci_fast(n - 2)


def test_fibonacci():
    """Compare slow vs fast fibonacci."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: CPU-Intensive Function (Fibonacci)")
    print("=" * 70)

    n = 30

    # Slow version
    print(f"\n❌ Without cache (fibonacci_slow({n})):")
    start = time.time()
    result = fibonacci_slow(n)
    duration_slow = time.time() - start
    print(f"   Result: {result}")
    print(f"   Time: {duration_slow:.4f}s")

    # Fast version
    print(f"\n✅ With cache (fibonacci_fast({n})):")
    start = time.time()
    result = fibonacci_fast(n)
    duration_fast = time.time() - start
    print(f"   Result: {result}")
    print(f"   Time: {duration_fast:.4f}s")

    # Speedup
    speedup = duration_slow / duration_fast if duration_fast > 0 else float("inf")
    print(f"\n🚀 Speedup: {speedup:.0f}x faster")


# EXAMPLE 2: MEMORY-INTENSIVE FUNCTION
@memory_profile
def memory_intensive_bad():
    """Bad: Creates large unnecessary lists."""
    big_list = [i for i in range(1000000)]  # 1M items
    doubled = [x * 2 for x in big_list]  # Another 1M items
    return sum(doubled)


@memory_profile
def memory_intensive_good():
    """Good: Uses generator (lazy evaluation)."""
    return sum(x * 2 for x in range(1000000))  # Generator, no lists


def test_memory():
    """Compare memory usage."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Memory-Intensive Function")
    print("=" * 70)

    print("\n❌ Bad (creates lists):")
    result_bad = memory_intensive_bad()
    print(f"   Result: {result_bad}")

    print("\n✅ Good (uses generator):")
    result_good = memory_intensive_good()
    print(f"   Result: {result_good}")


# EXAMPLE 3: I/O-INTENSIVE FUNCTION
@cached(cache_obj=function_cache)
def expensive_api_call(user_id):
    """Simulate expensive API call."""
    print(f"   [API CALL] Fetching user {user_id}...")
    time.sleep(0.5)  # Simulate network delay
    return {"id": user_id, "name": f"User {user_id}"}


def test_caching():
    """Test caching effectiveness."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Caching External API Calls")
    print("=" * 70)

    user_id = 123

    # First call (cache miss)
    print(f"\n1st call for user {user_id} (cache miss):")
    start = time.time()
    result1 = expensive_api_call(user_id)
    time1 = time.time() - start
    print(f"   Time: {time1:.4f}s")
    print(f"   Result: {result1}")

    # Second call (cache hit)
    print(f"\n2nd call for user {user_id} (cache hit):")
    start = time.time()
    result2 = expensive_api_call(user_id)
    time2 = time.time() - start
    print(f"   Time: {time2:.4f}s")
    print(f"   Result: {result2}")

    # Speedup
    speedup = time1 / time2 if time2 > 0 else float("inf")
    print(f"\n🚀 Speedup: {speedup:.0f}x faster (cached)")


# EXAMPLE 4: DATABASE QUERY OPTIMIZATION
def simulate_n_plus_1_problem():
    """Simulate N+1 query problem."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: N+1 Query Problem")
    print("=" * 70)

    # Simulate getting 10 users
    print("\n❌ Bad: N+1 queries")
    start = time.time()

    # 1 query for users
    print("   Query 1: SELECT * FROM users")
    time.sleep(0.01)  # Simulate query time
    users = list(range(10))

    # N queries for posts (one per user)
    for user_id in users:
        print(f"   Query {user_id + 2}: SELECT * FROM posts WHERE user_id={user_id}")
        time.sleep(0.01)  # Simulate query time

    time_bad = time.time() - start
    print(f"   Total time: {time_bad:.4f}s")
    print("   Total queries: 11")

    # Good: JOIN query
    print("\n✅ Good: Single JOIN query")
    start = time.time()

    print("   Query: SELECT * FROM users JOIN posts ON users.id = posts.user_id")
    time.sleep(0.01)  # Simulate query time

    time_good = time.time() - start
    print(f"   Total time: {time_good:.4f}s")
    print("   Total queries: 1")

    # Speedup
    speedup = time_bad / time_good if time_good > 0 else float("inf")
    print(f"\n🚀 Speedup: {speedup:.0f}x faster (JOIN)")


# EXAMPLE 5: PROFILING WITH cProfile
def complex_function():
    """Complex function with multiple operations."""
    # Operation 1: String operations (20% time)
    text = "hello " * 1000
    text.upper()

    # Operation 2: List operations (30% time)
    numbers = list(range(10000))
    sorted(numbers, reverse=True)

    # Operation 3: Dictionary operations (50% time)
    data = {i: i**2 for i in range(10000)}
    filtered = {k: v for k, v in data.items() if v % 2 == 0}

    return len(filtered)


def profile_complex_function():
    """Profile complex function to find bottlenecks."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: cProfile - Finding Bottlenecks")
    print("=" * 70)

    # Create profiler
    profiler = cProfile.Profile()
    profiler.enable()

    # Run function
    complex_function()

    profiler.disable()

    # Print statistics
    print("\n📊 Profile Statistics (Top 10 functions by cumulative time):\n")
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.sort_stats("cumulative")
    ps.print_stats(10)
    print(s.getvalue())


# EXAMPLE 6: TIMING DECORATOR
@timeit
def slow_operation():
    """Operation that takes time."""
    time.sleep(0.5)
    return "Done"


@timeit
def fast_operation():
    """Fast operation."""
    return sum(range(1000))


def test_timing_decorator():
    """Test timing decorator."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Timing Decorator")
    print("=" * 70)

    print("\n⏱️  Testing slow_operation:")
    slow_operation()

    print("\n⏱️  Testing fast_operation:")
    fast_operation()


# EXAMPLE 7: CONTEXT MANAGER TIMING
def test_context_timer():
    """Test context manager for timing."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Context Manager Timing")
    print("=" * 70)

    print("\n⏱️  Timing code block:")
    with timer("Database query simulation"):
        time.sleep(0.3)
        sum(range(10000))

    print("\n⏱️  Timing another block:")
    with timer("API call simulation"):
        time.sleep(0.2)


# EXAMPLE 8: BATCH PROCESSING
def test_batch_processing():
    """Test batch processing for large datasets."""
    print("\n" + "=" * 70)
    print("EXAMPLE 8: Batch Processing Large Datasets")
    print("=" * 70)

    from autom8.performance import batch_process

    # Simulate processing 1000 items
    items = list(range(1000))

    print("\n📦 Processing 1000 items in batches of 100:")

    batch_count = 0
    for batch in batch_process(items, batch_size=100):
        batch_count += 1
        time.sleep(0.05)  # Simulate processing time
        print(f"   Processed batch {batch_count}: {len(batch)} items")

    print(f"\n✅ Total batches processed: {batch_count}")


# MAIN
def main():
    """Run all profiling examples."""
    print("\n" + "=" * 70)
    print("🚀 AUTOM8 PERFORMANCE PROFILING EXAMPLES")
    print("=" * 70)

    try:
        test_fibonacci()
        test_caching()
        simulate_n_plus_1_problem()
        profile_complex_function()
        test_timing_decorator()
        test_context_timer()
        test_batch_processing()

        # Note: Memory profiling example requires running separately:
        # python -m memory_profiler profile_examples.py

        print("\n" + "=" * 70)
        print("✅ ALL EXAMPLES COMPLETED!")
        print("=" * 70)
        print("\n💡 To run memory profiling:")
        print("   python -m memory_profiler profile_examples.py")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
