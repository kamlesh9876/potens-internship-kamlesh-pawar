import pytest
import time
from app.cache.cache import SimpleCache, cache


def test_cache_set_and_get():
    """Test cache set and get operations"""
    test_cache = SimpleCache()
    
    test_cache.set("test_key", "test_value")
    value = test_cache.get("test_key")
    
    assert value == "test_value"


def test_cache_get_nonexistent_key():
    """Test getting a non-existent key"""
    test_cache = SimpleCache()
    
    value = test_cache.get("nonexistent_key")
    
    assert value is None


def test_cache_delete():
    """Test cache delete operation"""
    test_cache = SimpleCache()
    
    test_cache.set("test_key", "test_value")
    test_cache.delete("test_key")
    
    value = test_cache.get("test_key")
    assert value is None


def test_cache_clear():
    """Test cache clear operation"""
    test_cache = SimpleCache()
    
    test_cache.set("key1", "value1")
    test_cache.set("key2", "value2")
    test_cache.clear()
    
    assert test_cache.get("key1") is None
    assert test_cache.get("key2") is None


def test_cache_ttl():
    """Test cache TTL (time to live)"""
    test_cache = SimpleCache()
    test_cache.default_ttl = 1  # 1 second TTL
    
    test_cache.set("test_key", "test_value")
    
    # Should be available immediately
    assert test_cache.get("test_key") == "test_value"
    
    # Wait for TTL to expire
    time.sleep(1.5)
    
    # Should be None after TTL expires
    assert test_cache.get("test_key") is None


def test_cache_custom_ttl():
    """Test cache with custom TTL"""
    test_cache = SimpleCache()
    
    test_cache.set("test_key", "test_value", ttl=2)
    
    # Should be available immediately
    assert test_cache.get("test_key") == "test_value"
    
    # Wait for custom TTL to expire
    time.sleep(2.5)
    
    # Should be None after TTL expires
    assert test_cache.get("test_key") is None


def test_cache_stats():
    """Test cache statistics"""
    test_cache = SimpleCache()
    
    test_cache.set("key1", "value1")
    test_cache.set("key2", "value2")
    test_cache.set("key3", "value3")
    
    stats = test_cache.get_stats()
    
    assert stats["total_keys"] == 3
    assert "key1" in stats["keys"]
    assert "key2" in stats["keys"]
    assert "key3" in stats["keys"]


def test_cache_update_existing_key():
    """Test updating an existing cache key"""
    test_cache = SimpleCache()
    
    test_cache.set("test_key", "value1")
    test_cache.set("test_key", "value2")
    
    value = test_cache.get("test_key")
    assert value == "value2"


def test_cache_complex_data():
    """Test caching complex data structures"""
    test_cache = SimpleCache()
    
    complex_data = {
        "name": "Test",
        "items": [1, 2, 3],
        "nested": {"key": "value"}
    }
    
    test_cache.set("complex_key", complex_data)
    retrieved_data = test_cache.get("complex_key")
    
    assert retrieved_data == complex_data
    assert retrieved_data["items"] == [1, 2, 3]


def test_global_cache_instance():
    """Test global cache instance"""
    global cache
    
    cache.set("global_test", "global_value")
    value = cache.get("global_test")
    
    assert value == "global_value"
    
    # Clean up
    cache.delete("global_test")


def test_cache_delete_nonexistent_key():
    """Test deleting a non-existent key (should not raise error)"""
    test_cache = SimpleCache()
    
    # Should not raise an error
    test_cache.delete("nonexistent_key")


def test_cache_multiple_operations():
    """Test multiple cache operations in sequence"""
    test_cache = SimpleCache()
    
    # Set multiple keys
    for i in range(10):
        test_cache.set(f"key_{i}", f"value_{i}")
    
    # Get all keys
    for i in range(10):
        assert test_cache.get(f"key_{i}") == f"value_{i}"
    
    # Delete some keys
    for i in range(5):
        test_cache.delete(f"key_{i}")
    
    # Verify deleted keys are gone
    for i in range(5):
        assert test_cache.get(f"key_{i}") is None
    
    # Verify remaining keys still exist
    for i in range(5, 10):
        assert test_cache.get(f"key_{i}") == f"value_{i}"


def test_cache_stats_after_operations():
    """Test cache stats reflect current state"""
    test_cache = SimpleCache()
    
    # Initial state
    stats = test_cache.get_stats()
    assert stats["total_keys"] == 0
    
    # Add keys
    test_cache.set("key1", "value1")
    test_cache.set("key2", "value2")
    stats = test_cache.get_stats()
    assert stats["total_keys"] == 2
    
    # Delete key
    test_cache.delete("key1")
    stats = test_cache.get_stats()
    assert stats["total_keys"] == 1
    
    # Clear all
    test_cache.clear()
    stats = test_cache.get_stats()
    assert stats["total_keys"] == 0
