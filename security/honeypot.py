"""
security/honeypot.py — Honeypot endpoint for bot detection.

Hidden endpoint that flags and blocks suspicious IPs probing
common attack surfaces.
"""

import logging
from fastapi import Request, HTTPException

logger = logging.getLogger("security.honeypot")


async def honeypot(request: Request):
    """Honeypot handler for /admin/config.

    Never documented — any access is suspicious.
    Logs the IP and returns 403 Forbidden.
    """
    ip = request.client.host if request.client else "unknown"
    logger.warning(f"Honeypot triggered by IP: {ip} on path: {request.url.path}")
    raise HTTPException(status_code=403, detail="Forbidden")
