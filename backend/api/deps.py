"""
FastAPI dependencies dùng chung cho toàn bộ API.
"""

import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from config import settings

_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(key: str | None = Depends(_API_KEY_HEADER)) -> None:
    """
    Kiểm tra X-API-Key header cho các endpoint ghi (POST / PATCH / DELETE).

    - Nếu settings.api_key rỗng (dev mode) → bỏ qua, cho phép hết.
    - Nếu đã đặt API_KEY trong .env → key phải khớp.
    - Dùng secrets.compare_digest để tránh timing attack.
    """
    configured = settings.api_key.strip()
    if not configured:
        return

    if not key or not secrets.compare_digest(key.strip(), configured):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key không hợp lệ hoặc thiếu header X-API-Key.",
        )
