"""
Shared Shopify API client — token management and HTTP helpers.
Used by shopify/tools.py and any other module that calls the Shopify Admin API.
"""
import json
import os
import logging
import time
import asyncio
from typing import Optional, Any

import httpx

SHOPIFY_STORE         = os.environ.get("SHOPIFY_STORE", "")
SHOPIFY_TOKEN         = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
SHOPIFY_CLIENT_ID     = os.environ.get("SHOPIFY_CLIENT_ID", "")
SHOPIFY_CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET", "")
API_VERSION           = os.environ.get("SHOPIFY_API_VERSION", "2024-10")
TOKEN_REFRESH_BUFFER  = int(os.environ.get("TOKEN_REFRESH_BUFFER", "1800"))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("shopify_mcp")


class TokenManager:
    """
    Manages Shopify Admin API access tokens.

    Two modes:
      1. Static token  — set SHOPIFY_ACCESS_TOKEN (recommended for Custom Apps)
      2. OAuth / client_credentials — set SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET
         Enables auto-refresh before expiry and retry on 401.
    """

    def __init__(self, store, client_id, client_secret, static_token="", refresh_buffer=1800):
        self._store          = store
        self._client_id      = client_id
        self._client_secret  = client_secret
        self._static_token   = static_token
        self._refresh_buffer = refresh_buffer
        self._access_token   = ""
        self._expires_at     = 0.0
        self._lock           = asyncio.Lock()
        self._use_client_credentials = bool(client_id and client_secret)

        if self._use_client_credentials:
            logger.info("Token mode: client_credentials (auto-refresh enabled)")
        elif static_token:
            logger.info("Token mode: static SHOPIFY_ACCESS_TOKEN (no auto-refresh)")
            self._access_token = static_token
            self._expires_at   = float("inf")
        else:
            logger.warning("No credentials configured. Set SHOPIFY_ACCESS_TOKEN or SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET.")

    @property
    def is_expired(self):
        if not self._access_token:
            return True
        return time.time() >= (self._expires_at - self._refresh_buffer)

    async def get_token(self):
        if not self.is_expired:
            return self._access_token
        async with self._lock:
            if not self.is_expired:
                return self._access_token
            if self._use_client_credentials:
                await self._refresh_token()
            elif not self._access_token:
                raise RuntimeError("No valid token. Set SHOPIFY_ACCESS_TOKEN or SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET.")
        return self._access_token

    async def force_refresh(self):
        if not self._use_client_credentials:
            raise RuntimeError("Cannot refresh — using a static token.")
        async with self._lock:
            await self._refresh_token()
        return self._access_token

    async def _refresh_token(self):
        url = f"https://{self._store}.myshopify.com/admin/oauth/access_token"
        logger.info("Refreshing Shopify access token via client_credentials grant...")
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                data={"grant_type": "client_credentials", "client_id": self._client_id, "client_secret": self._client_secret},
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=15.0,
            )
            if resp.status_code != 200:
                raise RuntimeError(f"Token refresh failed ({resp.status_code}). Check credentials.")
            data               = resp.json()
            self._access_token = data["access_token"]
            expires_in         = data.get("expires_in", 86399)
            self._expires_at   = time.time() + expires_in
            logger.info(f"Token refreshed. Expires in {expires_in}s. Scopes: {data.get('scope', '')[:80]}...")


token_manager = TokenManager(
    store=SHOPIFY_STORE,
    client_id=SHOPIFY_CLIENT_ID,
    client_secret=SHOPIFY_CLIENT_SECRET,
    static_token=SHOPIFY_TOKEN,
    refresh_buffer=TOKEN_REFRESH_BUFFER,
)


def _base_url() -> str:
    return f"https://{SHOPIFY_STORE}.myshopify.com/admin/api/{API_VERSION}"


async def _headers() -> dict:
    token = await token_manager.get_token()
    return {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}


async def _request(method: str, path: str, params=None, body=None, _retried: bool = False) -> dict:
    """Central HTTP helper — every Shopify API call flows through here."""
    if not SHOPIFY_STORE:
        raise RuntimeError("Missing SHOPIFY_STORE environment variable.")
    url     = f"{_base_url()}/{path}"
    headers = await _headers()
    async with httpx.AsyncClient() as client:
        resp = await client.request(method, url, headers=headers, params=params, json=body, timeout=30.0)
        if resp.status_code == 401 and not _retried and token_manager._use_client_credentials:
            logger.warning("Got 401 — refreshing token and retrying...")
            await token_manager.force_refresh()
            return await _request(method, path, params=params, body=body, _retried=True)
        resp.raise_for_status()
        if resp.status_code == 204:
            return {}
        return resp.json()


def _error(e: Exception) -> str:
    if isinstance(e, httpx.HTTPStatusError):
        status = e.response.status_code
        try:
            detail = e.response.json()
        except Exception:
            detail = e.response.text[:500]
        messages = {
            401: "Authentication failed — check your SHOPIFY_ACCESS_TOKEN.",
            403: "Permission denied — token missing required API scopes.",
            404: "Resource not found — double-check the ID.",
            422: f"Validation error: {json.dumps(detail)}",
            429: "Rate-limited — wait a moment and retry.",
        }
        return messages.get(status, f"Shopify API error {status}: {json.dumps(detail)}")
    if isinstance(e, httpx.TimeoutException):
        return "Request timed out — try again."
    if isinstance(e, RuntimeError):
        return str(e)
    return f"Unexpected error: {type(e).__name__}: {e}"


def _fmt(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)
