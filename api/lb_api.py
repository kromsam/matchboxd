"""Modules to handle the Letterboxd API."""

import logging

from fastapi import HTTPException
import httpx
from httpx import ReadTimeout


# Logging
logger = logging.getLogger(__name__)


async def fetch_external_data(client, external_api_url):
    """Function to handle external API requests"""
    try:
        response = await client.get(external_api_url, timeout=50)
        response.raise_for_status()
        return response.json()
    except ReadTimeout as e:
        logger.error("The request to the external API timed out.")
        raise HTTPException(
            status_code=504, detail="The request to the external API timed out."
        ) from e
    except httpx.HTTPStatusError as e:
        logger.error(
            "Failed to fetch data from external API. Status code: %s",
            e.response.status_code,
        )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Failed to fetch data from external API. Status code: {e.response.status_code}",
        ) from e
    except Exception as e:
        logger.error("An unexpected error occurred: %s", str(e))
        raise HTTPException(
            status_code=500, detail=f"An unexpected error occurred: {str(e)}"
        ) from e
