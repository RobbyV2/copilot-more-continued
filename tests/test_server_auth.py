"""
Tests for API key authentication in the server module.
"""

import json
import os
from unittest import mock

import pytest
from fastapi import HTTPException
from fastapi.security import APIKeyHeader

from copilot_more_continued.server import validate_api_key


@pytest.fixture
def mock_settings():
    """Mock settings with various API key configurations"""
    with mock.patch("copilot_more_continued.server.settings") as mock_settings:
        yield mock_settings


def create_mock_request(auth_header: str = None):
    """Helper to create mock request with auth header"""
    mock_request = mock.Mock()
    mock_request.headers = {"Authorization": auth_header} if auth_header else {}
    return mock_request


@pytest.mark.asyncio
async def test_validate_api_key_no_keys_configured(mock_settings):
    """Test that any API key is accepted when no keys are configured"""
    # Configure settings with no API keys
    mock_settings.api_keys = None

    # Test with various inputs
    assert await validate_api_key(create_mock_request()) is True
    assert await validate_api_key(create_mock_request("")) is True
    assert await validate_api_key(create_mock_request("Bearer sk-123")) is True
    assert await validate_api_key(create_mock_request("any-random-key")) is True


@pytest.mark.asyncio
async def test_validate_api_key_with_keys_configured(mock_settings):
    """Test that only configured API keys are accepted when keys are set"""
    # Configure settings with specific API keys
    mock_settings.api_keys = "sk-valid-key,another-key"

    # Test with valid keys
    assert await validate_api_key(create_mock_request("Bearer sk-valid-key")) is True
    assert await validate_api_key(create_mock_request("sk-valid-key")) is True
    assert await validate_api_key(create_mock_request("another-key")) is True

    # Test with invalid key
    with pytest.raises(HTTPException) as exc_info:
        await validate_api_key(create_mock_request("sk-invalid-key"))
    assert exc_info.value.status_code == 401
    assert "Invalid API key" in exc_info.value.detail

    # Test with missing key
    with pytest.raises(HTTPException) as exc_info:
        await validate_api_key(create_mock_request())
    assert exc_info.value.status_code == 401
    assert "API key required" in exc_info.value.detail


@pytest.mark.asyncio
async def test_validate_api_key_bearer_prefix(mock_settings):
    """Test that Bearer prefix is properly handled"""
    # Configure settings with specific API keys
    mock_settings.api_keys = "sk-valid-key"

    # Test with and without Bearer prefix
    assert await validate_api_key(create_mock_request("Bearer sk-valid-key")) is True
    assert await validate_api_key(create_mock_request("sk-valid-key")) is True

    # Test with Bearer prefix on invalid key
    with pytest.raises(HTTPException):
        await validate_api_key(create_mock_request("Bearer sk-invalid-key"))


@pytest.mark.asyncio
async def test_validate_api_key_whitespace_handling(mock_settings):
    """Test that whitespace is properly handled in API keys"""
    # Configure settings with specific API keys
    mock_settings.api_keys = "sk-valid-key"

    # Test with extra spaces
    assert (
        await validate_api_key(create_mock_request("  Bearer sk-valid-key  ")) is True
    )
    assert await validate_api_key(create_mock_request("  sk-valid-key  ")) is True
