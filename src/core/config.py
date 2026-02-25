"""Core configuration module for AI Empower Hub 360."""

import os
from pathlib import Path
from typing import Any, Optional

import yaml
from dotenv import load_dotenv


class Config:
    """Application configuration manager."""

    _instance: Optional["Config"] = None
    _config: dict = {}

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self) -> None:
        """Load configuration from YAML file and environment variables."""
        # Load .env file if exists
        load_dotenv()

        # Get config file path
        config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"

        if config_path.exists():
            with open(config_path, "r") as f:
                self._config = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        # Handle environment variable substitution
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.getenv(env_var, default)

        return value

    @property
    def app_name(self) -> str:
        """Get application name."""
        return self.get("app.name", "AI Empower Hub 360")

    @property
    def app_version(self) -> str:
        """Get application version."""
        return self.get("app.version", "0.1.0")

    @property
    def debug(self) -> bool:
        """Get debug mode."""
        return self.get("app.debug", False)

    @property
    def environment(self) -> str:
        """Get environment."""
        return self.get("app.environment", "development")

    @property
    def server_host(self) -> str:
        """Get server host."""
        return self.get("server.host", "0.0.0.0")

    @property
    def server_port(self) -> int:
        """Get server port."""
        return self.get("server.port", 8000)

    @property
    def api_prefix(self) -> str:
        """Get API prefix."""
        return self.get("api.prefix", "/api/v1")


# Global config instance
config = Config()