def rate_limit(limit: int, key=None):
    """Decorator for configuring rate limit and key in different functions."""

    def decorator(func):
        """Sets limit and key attributes to function."""
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator
