"""
Online LLM API Handler Module

This module provides functions to call online LLM APIs (e.g., OpenAI, Groq)
with API key handling. It serves as a fallback LLM provider when local options fail.

Features:
- Support for multiple LLM providers (OpenAI, Groq, etc.)
- API key management and validation
- Error handling and retry logic
- Request/response formatting
- Rate limiting and timeout handling
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError
import time

logger = logging.getLogger(__name__)


class LLMAPIError(Exception):
    """Custom exception for LLM API errors."""
    pass


class APIHandler:
    """
    Handler for online LLM API calls with support for multiple providers.
    """

    def __init__(self):
        self.providers = {
            'openai': {
                'base_url': 'https://api.openai.com/v1',
                'api_key_env': 'OPENAI_API_KEY',
                'models': ['gpt-4', 'gpt-3.5-turbo', 'gpt-4-turbo-preview']
            },
            'groq': {
                'base_url': 'https://api.groq.com/openai/v1',
                'api_key_env': 'GROQ_API_KEY',
                'models': ['llama2-70b-4096', 'mixtral-8x7b-32768', 'gemma-7b-it']
            }
        }
        self.default_provider = 'openai'
        self.timeout = 30  # seconds
        self.max_retries = 3
        self.retry_delay = 1  # seconds

    def call_api(self, prompt: str, provider: Optional[str] = None,
                 model: Optional[str] = None, **kwargs) -> str:
        """
        Call the LLM API with the given prompt.

        Args:
            prompt: The input prompt for the LLM
            provider: The API provider to use ('openai', 'groq', etc.)
            model: The specific model to use
            **kwargs: Additional parameters for the API call

        Returns:
            The LLM response as a string

        Raises:
            LLMAPIError: If the API call fails
        """
        provider = provider or self.default_provider

        if provider not in self.providers:
            raise LLMAPIError(f"Unsupported provider: {provider}")

        provider_config = self.providers[provider]
        api_key = self._get_api_key(provider_config['api_key_env'])

        if not api_key:
            raise LLMAPIError(f"API key not found for provider: {provider}")

        model = model or provider_config['models'][0]

        url = f"{provider_config['base_url']}/chat/completions"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': prompt}],
            'temperature': kwargs.get('temperature', 0.7),
            'max_tokens': kwargs.get('max_tokens', 1000),
        }

        for attempt in range(self.max_retries):
            try:
                logger.info(f"Making API call to {provider} with model {model} (attempt {attempt + 1})")

                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=self.timeout
                )

                response.raise_for_status()

                result = response.json()
                content = result['choices'][0]['message']['content']

                logger.info(f"Successfully received response from {provider}")
                return content

            except Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1} for {provider}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    raise LLMAPIError(f"Request timeout after {self.max_retries} attempts")

            except ConnectionError as e:
                logger.warning(f"Connection error on attempt {attempt + 1} for {provider}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise LLMAPIError(f"Connection failed after {self.max_retries} attempts: {e}")

            except RequestException as e:
                logger.error(f"Request error for {provider}: {e}")
                raise LLMAPIError(f"API request failed: {e}")

            except (KeyError, IndexError) as e:
                logger.error(f"Invalid response format from {provider}: {e}")
                raise LLMAPIError(f"Invalid API response format: {e}")

    def _get_api_key(self, env_var: str) -> Optional[str]:
        """
        Get API key from environment variables.

        Args:
            env_var: Environment variable name

        Returns:
            API key string or None if not found
        """
        return os.getenv(env_var)

    def list_available_providers(self) -> Dict[str, Any]:
        """
        List all available providers and their configurations.

        Returns:
            Dictionary of provider configurations
        """
        return self.providers.copy()

    def validate_provider(self, provider: str) -> bool:
        """
        Validate if a provider is supported and has API key configured.

        Args:
            provider: Provider name to validate

        Returns:
            True if provider is valid and configured, False otherwise
        """
        if provider not in self.providers:
            return False

        provider_config = self.providers[provider]
        api_key = self._get_api_key(provider_config['api_key_env'])
        return api_key is not None


# Global instance for easy access
api_handler = APIHandler()


def call_llm_api(prompt: str, provider: Optional[str] = None,
                 model: Optional[str] = None, **kwargs) -> str:
    """
    Convenience function to call LLM API.

    This function provides a simple interface for calling LLM APIs
    and is used by other modules in the system.

    Args:
        prompt: The input prompt for the LLM
        provider: The API provider to use
        model: The specific model to use
        **kwargs: Additional parameters

    Returns:
        The LLM response as a string

    Raises:
        LLMAPIError: If the API call fails
    """
    return api_handler.call_api(prompt, provider, model, **kwargs)
