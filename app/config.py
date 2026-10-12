import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")


settings = Settings()
