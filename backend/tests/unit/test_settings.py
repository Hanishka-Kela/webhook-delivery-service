
import pytest

from pydantic import ValidationError

from webhook_delivery_service.infrastructure.config.settings import (
    Settings,
    get_settings,
)


@pytest.fixture
def valid_env(monkeypatch):
    # Prevent tests from reading the real .env file.
    monkeypatch.setattr(
        Settings,
        "model_config",
        {
            **Settings.model_config,
            "env_file": None,
        },
    )

    # Supply isolated test configuration.
    env = {
        "DATABASE_URL": "postgresql+psycopg://test:test@localhost:5432/test_db",
        "REDIS_URL": "redis://localhost:6379/0",
        "JWT_SECRET_KEY": "test-secret-not-for-production",
    }

    for key, value in env.items():
        monkeypatch.setenv(key, value)

    # Remove optional overrides from the host environment.
    optional_keys = [
        "APP_NAME",
        "DEBUG",
        "ENVIRONMENT",
        "REDIS_STREAM_NAME",
        "JWT_ALGORITHM",
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "REFRESH_TOKEN_EXPIRE_DAYS",
        "WEBHOOK_TIMEOUT_SECONDS",
        "MAX_RETRY_ATTEMPTS",
        "CORS_ORIGINS",
        "LOG_LEVEL",
    ]

    for key in optional_keys:
        monkeypatch.delenv(key, raising=False)

    get_settings.cache_clear()

    yield env

    get_settings.cache_clear()


def test_valid_configuration(valid_env):
    settings = Settings()

    assert settings.APP_NAME == "Webhook Delivery Service"
    assert settings.ENVIRONMENT == "development"
    assert settings.DATABASE_URL == valid_env["DATABASE_URL"]
    assert settings.REDIS_URL == valid_env["REDIS_URL"]


def test_default_values(valid_env):
    settings = Settings()

    assert settings.DEBUG is False
    assert settings.REDIS_STREAM_NAME == "webhook:deliveries"
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 7
    assert settings.WEBHOOK_TIMEOUT_SECONDS == 10
    assert settings.MAX_RETRY_ATTEMPTS == 5
    assert settings.CORS_ORIGINS == ["http://localhost:5173"]
    assert settings.LOG_LEVEL == "INFO"


@pytest.mark.parametrize(
    "missing_key",
    [
        "DATABASE_URL",
        "REDIS_URL",
        "JWT_SECRET_KEY",
    ],
)
def test_missing_required_settings(valid_env, monkeypatch, missing_key):
    monkeypatch.delenv(missing_key)

    with pytest.raises(ValidationError):
        Settings()


@pytest.mark.parametrize(
    "environment",
    ["invalid", "prod", "local", ""],
)
def test_invalid_environment(valid_env, monkeypatch, environment):
    monkeypatch.setenv("ENVIRONMENT", environment)

    with pytest.raises(ValidationError):
        Settings()


@pytest.mark.parametrize(
    "timeout",
    ["0", "-1", "-10"],
)
def test_invalid_webhook_timeout(valid_env, monkeypatch, timeout):
    monkeypatch.setenv("WEBHOOK_TIMEOUT_SECONDS", timeout)

    with pytest.raises(ValidationError):
        Settings()


@pytest.mark.parametrize(
    "retry_count",
    ["-1", "-5"],
)
def test_invalid_retry_count(valid_env, monkeypatch, retry_count):
    monkeypatch.setenv("MAX_RETRY_ATTEMPTS", retry_count)

    with pytest.raises(ValidationError):
        Settings()


def test_zero_retries_allowed(valid_env, monkeypatch):
    monkeypatch.setenv("MAX_RETRY_ATTEMPTS", "0")

    settings = Settings()

    assert settings.MAX_RETRY_ATTEMPTS == 0


def test_environment_variable_override(valid_env, monkeypatch):
    monkeypatch.setenv("APP_NAME", "Test Webhook Service")
    monkeypatch.setenv("ENVIRONMENT", "testing")

    settings = Settings()

    assert settings.APP_NAME == "Test Webhook Service"
    assert settings.ENVIRONMENT == "testing"


def test_boolean_parsing(valid_env, monkeypatch):
    monkeypatch.setenv("DEBUG", "true")

    settings = Settings()

    assert settings.DEBUG is True


def test_cors_origins_parsing(valid_env, monkeypatch):
    monkeypatch.setenv(
        "CORS_ORIGINS",
        '["http://localhost:5173", "http://localhost:3000"]',
    )

    settings = Settings()

    assert settings.CORS_ORIGINS == [
        "http://localhost:5173",
        "http://localhost:3000",
    ]


def test_invalid_log_level(valid_env, monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "VERBOSE")

    with pytest.raises(ValidationError):
        Settings()


def test_secret_is_masked(valid_env):
    settings = Settings()

    representation = repr(settings)

    assert "test-secret-not-for-production" not in representation
    assert settings.JWT_SECRET_KEY.get_secret_value() == (
        "test-secret-not-for-production"
    )


def test_cached_settings(valid_env):
    first = get_settings()
    second = get_settings()

    assert first is second
