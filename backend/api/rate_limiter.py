"""
Simple rate limiter for authentication endpoints
"""
from datetime import datetime, timedelta
from collections import defaultdict

class RateLimiter:
    def __init__(self, max_attempts=5, window_minutes=15):
        self.max_attempts = max_attempts
        self.window = timedelta(minutes=window_minutes)
        self.attempts = defaultdict(list)  # {ip: [timestamp1, timestamp2, ...]}

    def is_allowed(self, identifier: str) -> bool:
        """Check if request from identifier is allowed"""
        now = datetime.now()

        # Clean old attempts
        self.attempts[identifier] = [
            ts for ts in self.attempts[identifier]
            if now - ts < self.window
        ]

        # Check if under limit
        if len(self.attempts[identifier]) >= self.max_attempts:
            return False

        # Record this attempt
        self.attempts[identifier].append(now)
        return True

    def reset(self, identifier: str):
        """Reset attempts for identifier (e.g., after successful login)"""
        if identifier in self.attempts:
            del self.attempts[identifier]

# Global rate limiter instance
login_limiter = RateLimiter(max_attempts=5, window_minutes=15)
signup_limiter = RateLimiter(max_attempts=3, window_minutes=60)
