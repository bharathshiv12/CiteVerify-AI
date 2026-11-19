"""
Shared HTTP client for scholarly APIs (Crossref, OpenAlex, Europe PMC).
Implements: polite pool User-Agent headers, timeout, retries with backoff, and local caching.
"""
import os
import time
import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger("citeverify.research.http")


class PoliteScholarlyHttpClient:
    def __init__(
        self,
        user_agent_prefix: str = "CiteVerify/1.0",
        contact_email: Optional[str] = None,
        timeout: float = 15.0,
        max_retries: int = 3,
    ):
        self.contact_email = (
            contact_email
            or os.getenv("OPENALEX_EMAIL")
            or os.getenv("CROSSREF_EMAIL")
            or "researcher@example.com"
        )
        self.user_agent = f"{user_agent_prefix} (mailto:{self.contact_email})"
        self.timeout = timeout
        self.max_retries = max_retries
        self._cache: Dict[str, Any] = {}

    async def get_json(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes cached, retrying GET request against public scholarly API.
        """
        cache_key = f"{url}?{sorted((params or {}).items())}"
        if use_cache and cache_key in self._cache:
            logger.debug(f"Cache hit for {url}")
            return self._cache[cache_key]

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(1, self.max_retries + 1):
                try:
                    resp = await client.get(url, params=params, headers=headers)
                    if resp.status_code == 200:
                        data = resp.json()
                        if use_cache:
                            self._cache[cache_key] = data
                        return data
                    elif resp.status_code in (404, 410):
                        return {}
                    elif resp.status_code == 429:
                        time.sleep(1.0 * attempt)
                    else:
                        resp.raise_for_status()
                except httpx.RequestError as e:
                    if attempt == self.max_retries:
                        logger.error(f"Failed to fetch {url} after {self.max_retries} attempts: {e}")
                        raise
                    time.sleep(0.5 * attempt)

        return {}


# Shared singleton client
default_research_http_client = PoliteScholarlyHttpClient()

