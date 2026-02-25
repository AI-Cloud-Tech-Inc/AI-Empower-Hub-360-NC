"""Tests for core configuration module."""

import pytest

from src.core.config import Config


class TestConfig:
    """Test configuration module."""

    def test_config_singleton(self):
        """Test that config is a singleton."""
        config1 = Config()
        config2 = Config()
        assert config1 is config2

    def test_app_name(self):
        """Test app name getter."""
        config = Config()
        assert config.app_name == "AI Empower Hub 360"

    def test_app_version(self):
        """Test app version getter."""
        config = Config()
        assert config.app_version == "0.1.0"

    def test_get_nested_value(self):
        """Test getting nested configuration values."""
        config = Config()
        assert config.get("app.name") == "AI Empower Hub 360"

    def test_get_with_default(self):
        """Test getting config value with default."""
        config = Config()
        assert config.get("nonexistent.key", "default") == "default"

    def test_debug_default(self):
        """Test debug mode default."""
        config = Config()
        assert config.debug is False