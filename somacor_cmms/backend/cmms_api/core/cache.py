"""
Caching utilities for CMMS API
"""
from django.core.cache import cache
from django.conf import settings
import logging
from typing import Any, Optional, Callable
import hashlib
import json

logger = logging.getLogger(__name__)


class CMMSCache:
    """
    Centralized caching system for CMMS API
    """
    
    DEFAULT_TIMEOUT = 300  # 5 minutes
    LONG_TIMEOUT = 3600    # 1 hour
    SHORT_TIMEOUT = 60     # 1 minute
    
    @staticmethod
    def generate_cache_key(prefix: str, *args, **kwargs) -> str:
        """
        Generate a consistent cache key
        """
        # Convert args and kwargs to string
        key_parts = [prefix]
        
        for arg in args:
            key_parts.append(str(arg))
        
        for key, value in sorted(kwargs.items()):
            key_parts.append(f"{key}:{value}")
        
        # Create hash for long keys
        key_string = ":".join(key_parts)
        if len(key_string) > 200:
            key_hash = hashlib.md5(key_string.encode()).hexdigest()
            return f"{prefix}:hash:{key_hash}"
        
        return key_string
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Get value from cache
        """
        try:
            value = cache.get(key)
            if value is not None:
                logger.debug(f"Cache hit: {key}")
                return value
            else:
                logger.debug(f"Cache miss: {key}")
                return default
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    @staticmethod
    def set(key: str, value: Any, timeout: Optional[int] = None) -> bool:
        """
        Set value in cache
        """
        try:
            if timeout is None:
                timeout = CMMSCache.DEFAULT_TIMEOUT
            
            cache.set(key, value, timeout)
            logger.debug(f"Cache set: {key} (timeout: {timeout}s)")
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    @staticmethod
    def delete(key: str) -> bool:
        """
        Delete value from cache
        """
        try:
            cache.delete(key)
            logger.debug(f"Cache delete: {key}")
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    @staticmethod
    def get_or_set(key: str, callable_func: Callable, timeout: Optional[int] = None) -> Any:
        """
        Get value from cache or set it using callable
        """
        value = CMMSCache.get(key)
        if value is None:
            value = callable_func()
            CMMSCache.set(key, value, timeout)
        return value
    
    @staticmethod
    def invalidate_pattern(pattern: str) -> int:
        """
        Invalidate cache keys matching pattern
        """
        try:
            # This is a simplified implementation
            # In production, you might want to use Redis with pattern matching
            logger.info(f"Cache invalidation requested for pattern: {pattern}")
            return 0
        except Exception as e:
            logger.error(f"Cache invalidation error for pattern {pattern}: {e}")
            return 0


def cache_equipment_data(equipment_id: int, data: dict, timeout: int = None):
    """
    Cache equipment data
    """
    key = CMMSCache.generate_cache_key('equipment', equipment_id)
    CMMSCache.set(key, data, timeout or CMMSCache.DEFAULT_TIMEOUT)


def get_cached_equipment_data(equipment_id: int) -> Optional[dict]:
    """
    Get cached equipment data
    """
    key = CMMSCache.generate_cache_key('equipment', equipment_id)
    return CMMSCache.get(key)


def cache_work_order_data(work_order_id: int, data: dict, timeout: int = None):
    """
    Cache work order data
    """
    key = CMMSCache.generate_cache_key('work_order', work_order_id)
    CMMSCache.set(key, data, timeout or CMMSCache.DEFAULT_TIMEOUT)


def get_cached_work_order_data(work_order_id: int) -> Optional[dict]:
    """
    Get cached work order data
    """
    key = CMMSCache.generate_cache_key('work_order', work_order_id)
    return CMMSCache.get(key)


def cache_dashboard_stats(data: dict, timeout: int = None):
    """
    Cache dashboard statistics
    """
    key = CMMSCache.generate_cache_key('dashboard', 'stats')
    CMMSCache.set(key, data, timeout or CMMSCache.SHORT_TIMEOUT)


def get_cached_dashboard_stats() -> Optional[dict]:
    """
    Get cached dashboard statistics
    """
    key = CMMSCache.generate_cache_key('dashboard', 'stats')
    return CMMSCache.get(key)


def cache_equipment_list(filters: dict, data: list, timeout: int = None):
    """
    Cache equipment list with filters
    """
    key = CMMSCache.generate_cache_key('equipment_list', **filters)
    CMMSCache.set(key, data, timeout or CMMSCache.DEFAULT_TIMEOUT)


def get_cached_equipment_list(filters: dict) -> Optional[list]:
    """
    Get cached equipment list with filters
    """
    key = CMMSCache.generate_cache_key('equipment_list', **filters)
    return CMMSCache.get(key)


def cache_work_order_list(filters: dict, data: list, timeout: int = None):
    """
    Cache work order list with filters
    """
    key = CMMSCache.generate_cache_key('work_order_list', **filters)
    CMMSCache.set(key, data, timeout or CMMSCache.DEFAULT_TIMEOUT)


def get_cached_work_order_list(filters: dict) -> Optional[list]:
    """
    Get cached work order list with filters
    """
    key = CMMSCache.generate_cache_key('work_order_list', **filters)
    return CMMSCache.get(key)


def invalidate_equipment_cache(equipment_id: int):
    """
    Invalidate equipment-related cache
    """
    keys_to_delete = [
        CMMSCache.generate_cache_key('equipment', equipment_id),
        CMMSCache.generate_cache_key('dashboard', 'stats'),
    ]
    
    for key in keys_to_delete:
        CMMSCache.delete(key)
    
    # Invalidate equipment list caches
    CMMSCache.invalidate_pattern('equipment_list:*')


def invalidate_work_order_cache(work_order_id: int):
    """
    Invalidate work order-related cache
    """
    keys_to_delete = [
        CMMSCache.generate_cache_key('work_order', work_order_id),
        CMMSCache.generate_cache_key('dashboard', 'stats'),
    ]
    
    for key in keys_to_delete:
        CMMSCache.delete(key)
    
    # Invalidate work order list caches
    CMMSCache.invalidate_pattern('work_order_list:*')


def invalidate_dashboard_cache():
    """
    Invalidate dashboard cache
    """
    CMMSCache.delete(CMMSCache.generate_cache_key('dashboard', 'stats'))
