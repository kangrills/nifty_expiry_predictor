"""Redis cache for real-time data."""

import redis
import json
import pickle
from typing import Any, Optional
from datetime import timedelta

from config.settings import settings
from config.logging_config import get_logger

logger = get_logger(__name__)


class RedisCache:
    """Redis cache wrapper for real-time data."""

    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.client = redis.from_url(
                settings.database.redis_url,
                decode_responses=False,  # We'll handle encoding
            )
            self.client.ping()
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.client = None

    def set(
        self,
        key: str,
        value: Any,
        expiry: Optional[int] = None,
        serialize: str = "json",
    ) -> bool:
        """Set a value in cache.

        Args:
            key: Cache key
            value: Value to cache
            expiry: Expiry time in seconds
            serialize: Serialization method ('json' or 'pickle')

        Returns:
            True if successful
        """
        if not self.client:
            return False

        try:
            if serialize == "json":
                serialized_value = json.dumps(value)
            elif serialize == "pickle":
                serialized_value = pickle.dumps(value)
            else:
                raise ValueError("serialize must be 'json' or 'pickle'")

            if expiry:
                self.client.setex(key, expiry, serialized_value)
            else:
                self.client.set(key, serialized_value)

            return True
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {e}")
            return False

    def get(self, key: str, serialize: str = "json") -> Optional[Any]:
        """Get a value from cache.

        Args:
            key: Cache key
            serialize: Serialization method used ('json' or 'pickle')

        Returns:
            Cached value or None
        """
        if not self.client:
            return None

        try:
            value = self.client.get(key)
            if value is None:
                return None

            if serialize == "json":
                return json.loads(value)
            elif serialize == "pickle":
                return pickle.loads(value)
            else:
                raise ValueError("serialize must be 'json' or 'pickle'")

        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a key from cache.

        Args:
            key: Cache key

        Returns:
            True if successful
        """
        if not self.client:
            return False

        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if a key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        if not self.client:
            return False

        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Failed to check cache key {key}: {e}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching a pattern.

        Args:
            pattern: Key pattern (e.g., 'option_chain:*')

        Returns:
            Number of keys deleted
        """
        if not self.client:
            return 0

        try:
            keys = self.client.keys(pattern)
            if keys:
                return self.client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Failed to clear pattern {pattern}: {e}")
            return 0


# Global cache instance
cache = RedisCache()
