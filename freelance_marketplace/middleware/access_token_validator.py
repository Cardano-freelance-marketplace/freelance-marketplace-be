from hashlib import sha256

import jwt
from fastapi import Request
from starlette.responses import JSONResponse

from freelance_marketplace.api.services.redis import Redis
from freelance_marketplace.core.config import settings

prefix = "/api/v1/"
PUBLIC_ENDPOINTS = {
    (f"/", "GET"),
    (f"/docs", "GET"),
    (f"/openapi.json", "GET"),
    (f"{prefix}login", "POST"),
    (f"{prefix}logout", "POST"),
    (f"{prefix}nonce", "GET"),
    (f"{prefix}roles", "GET"),
}

async def auth_middleware(request: Request, call_next):
    path = request.url.path
    method = request.method.upper()
    # if (path, method) in PUBLIC_ENDPOINTS:
    if True:
        return await call_next(request)

    token = request.cookies.get("access_token")
    if not token:
        return JSONResponse(status_code=401, content={"detail": "Missing access token"})

    try:
        payload = jwt.decode(
            token,
            settings.fastapi.secret_key,
            algorithms=[settings.fastapi.jwt_algorithm]
        )
        user_wallet = payload.get("sub")
        if not user_wallet:
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        session_id = sha256(token.encode()).hexdigest()
        stored_token = await Redis.get_redis_data(f"sessions:{session_id}")
        if not stored_token:
            return JSONResponse(status_code=401, content={"detail": "Session expired or invalid"})


    except Exception as e:
        return JSONResponse(status_code=401, content={"detail": "Invalid or expired token"})

    return await call_next(request)
