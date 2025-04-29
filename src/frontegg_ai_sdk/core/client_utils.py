"""
Client Utilities Module

This module provides utility functions to support the AI Agents client.
"""

import asyncio
import time
from typing import Any, Callable, Optional, TypeVar

from .config import ClientRetryConfiguration

T = TypeVar('T')


async def retry_async(
    fn: Callable[..., Any],
    retry_config: ClientRetryConfiguration,
    *args: Any,
    **kwargs: Any
) -> Any:
    """
    Retry an asynchronous function with exponential backoff.

    Args:
        fn: Async function to retry
        retry_config: Configuration for the retry logic
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function call

    Raises:
        The last exception encountered
    """
    last_exception = None
    max_tries = retry_config.tries
    delay_ms = retry_config.delay_in_ms
    retry_if = retry_config.retry_if
    delay_fn = retry_config.delay_fn

    for attempt in range(max_tries):
        try:
            return await fn(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            # Check if we should retry this exception
            if retry_if and not retry_if(e):
                raise
            
            # Don't retry if this was the last attempt
            if attempt >= max_tries - 1:
                raise
            
            # Calculate delay for this attempt
            if delay_fn:
                current_delay = delay_fn(attempt, delay_ms) / 1000  # Convert ms to seconds
            else:
                # Default exponential backoff
                current_delay = (delay_ms * (2 ** attempt)) / 1000
            
            # Wait before retrying
            await asyncio.sleep(current_delay)
    
    # This should never be reached, but just in case
    if last_exception:
        raise last_exception
    return None


def retry_sync(
    fn: Callable[..., T],
    retry_config: ClientRetryConfiguration,
    *args: Any,
    **kwargs: Any
) -> T:
    """
    Retry a synchronous function with exponential backoff.

    Args:
        fn: Function to retry
        retry_config: Configuration for the retry logic
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        The result of the function call

    Raises:
        The last exception encountered
    """
    last_exception = None
    max_tries = retry_config.tries
    delay_ms = retry_config.delay_in_ms
    retry_if = retry_config.retry_if
    delay_fn = retry_config.delay_fn

    for attempt in range(max_tries):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            # Check if we should retry this exception
            if retry_if and not retry_if(e):
                raise
            
            # Don't retry if this was the last attempt
            if attempt >= max_tries - 1:
                raise
            
            # Calculate delay for this attempt
            if delay_fn:
                current_delay = delay_fn(attempt, delay_ms) / 1000  # Convert ms to seconds
            else:
                # Default exponential backoff
                current_delay = (delay_ms * (2 ** attempt)) / 1000
            
            # Wait before retrying
            time.sleep(current_delay)
    
    # This should never be reached, but just in case
    if last_exception:
        raise last_exception
    return None  # type: ignore 