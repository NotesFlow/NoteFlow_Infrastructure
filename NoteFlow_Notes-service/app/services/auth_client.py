import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.notes import CurrentUser


async def validate_token(authorization: str) -> CurrentUser:
    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/me",
                headers={"Authorization": authorization},
            )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable",
        )

    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service error",
        )

    return CurrentUser(**response.json())
