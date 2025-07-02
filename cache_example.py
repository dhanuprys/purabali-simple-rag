#!/usr/bin/env python3
"""
Example script to demonstrate the in-memory caching system.
This script shows how the cache works in different environments.
"""

import os
import time
from app.cache import cache, cached
from app.db import get_pura_gambar, get_kabupaten_list_cached
from app.config import CacheConfig

def demonstrate_cache():
    """Demonstrate cache functionality"""
    
    print("=== In-Memory Cache Demonstration ===\n")
    
    # Show environment and cache status
    print(f"Environment: {CacheConfig.ENVIRONMENT}")
    print(f"Cache Enabled: {CacheConfig.get_cache_enabled()}")
    print(f"Default TTL: {CacheConfig.DEFAULT_TTL} seconds")
    print()
    
    # Test cache operations
    print("1. Testing cache set/get operations:")
    cache.set("test_key", "test_value", ttl=10)
    result = cache.get("test_key")
    print(f"   Set 'test_key' -> 'test_value'")
    print(f"   Get 'test_key' -> {result}")
    print()
    
    # Test cache statistics
    print("2. Cache Statistics:")
    stats = cache.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    print()
    
    # Test database function caching
    print("3. Testing database function caching:")
    
    # First call - should hit database
    start_time = time.time()
    kabupaten_list = get_kabupaten_list_cached()
    db_time = time.time() - start_time
    print(f"   First call (database): {db_time:.4f}s, {len(kabupaten_list)} items")
    
    # Second call - should hit cache
    start_time = time.time()
    kabupaten_list_cached = get_kabupaten_list_cached()
    cache_time = time.time() - start_time
    print(f"   Second call (cache): {cache_time:.4f}s, {len(kabupaten_list_cached)} items")
    
    if cache_time < db_time:
        print(f"   ✅ Cache is {db_time/cache_time:.1f}x faster!")
    else:
        print(f"   ⚠️  Cache is slower (this is normal for small datasets)")
    print()
    
    # Test cache invalidation
    print("4. Testing cache invalidation:")
    cache.set("demo_key", "demo_value", ttl=60)
    print(f"   Set 'demo_key' -> 'demo_value'")
    
    # Invalidate by pattern
    invalidated = cache.invalidate_pattern("demo")
    print(f"   Invalidated {invalidated} entries matching 'demo' pattern")
    
    # Check if key is gone
    result = cache.get("demo_key")
    print(f"   Get 'demo_key' -> {result}")
    print()
    
    # Show final statistics
    print("5. Final Cache Statistics:")
    final_stats = cache.get_stats()
    for key, value in final_stats.items():
        print(f"   {key}: {value}")

def test_environment_switching():
    """Test how cache behaves in different environments"""
    
    print("\n=== Environment Switching Test ===\n")
    
    # Save original environment
    original_env = os.getenv("ENVIRONMENT", "development")
    
    # Test development environment
    print("Testing Development Environment:")
    os.environ["ENVIRONMENT"] = "development"
    
    # Recreate cache instance to pick up new environment
    from app.cache import InMemoryCache
    dev_cache = InMemoryCache()
    
    dev_cache.set("dev_key", "dev_value")
    result = dev_cache.get("dev_key")
    print(f"   Development cache enabled: {dev_cache._enabled}")
    print(f"   Get result: {result}")
    print()
    
    # Test production environment
    print("Testing Production Environment:")
    os.environ["ENVIRONMENT"] = "production"
    
    prod_cache = InMemoryCache()
    prod_cache.set("prod_key", "prod_value")
    result = prod_cache.get("prod_key")
    print(f"   Production cache enabled: {prod_cache._enabled}")
    print(f"   Get result: {result}")
    print()
    
    # Restore original environment
    os.environ["ENVIRONMENT"] = original_env
    print(f"Restored environment to: {original_env}")

def performance_comparison():
    """Compare performance with and without cache"""
    
    print("\n=== Performance Comparison ===\n")
    
    if not CacheConfig.get_cache_enabled():
        print("⚠️  Cache is disabled. Set ENVIRONMENT=production to enable.")
        return
    
    print("Testing database function performance:")
    
    # Test without cache (direct database calls)
    print("1. Direct database calls (no cache):")
    start_time = time.time()
    
    for i in range(5):
        get_kabupaten_list_cached()
    
    direct_time = time.time() - start_time
    print(f"   5 calls took: {direct_time:.4f}s")
    print(f"   Average: {direct_time/5:.4f}s per call")
    print()
    
    # Test with cache (should be faster after first call)
    print("2. Cached database calls:")
    start_time = time.time()
    
    for i in range(5):
        get_kabupaten_list_cached()
    
    cached_time = time.time() - start_time
    print(f"   5 calls took: {cached_time:.4f}s")
    print(f"   Average: {cached_time/5:.4f}s per call")
    print()
    
    # Show improvement
    if cached_time < direct_time:
        improvement = ((direct_time - cached_time) / direct_time) * 100
        print(f"✅ Performance improvement: {improvement:.1f}%")
    else:
        print("⚠️  No significant improvement (normal for small datasets)")

if __name__ == "__main__":
    try:
        demonstrate_cache()
        test_environment_switching()
        performance_comparison()
        
        print("\n=== Cache Demo Complete ===")
        print("\nTo test the cache in production:")
        print("1. Set ENVIRONMENT=production")
        print("2. Run the application")
        print("3. Check /api/cache/stats endpoint")
        print("4. Monitor performance improvements")
        
    except Exception as e:
        print(f"Error during cache demonstration: {e}")
        print("Make sure the database is running and accessible.") 