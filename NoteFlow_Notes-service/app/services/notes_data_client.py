from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.notes import NoteArchiveUpdate, NoteCreate, NotePinUpdate, NoteUpdate


def _raise_from_data_service(response: httpx.Response) -> None:
    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response.json())

    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Notes data service error",
        )


async def list_notes(user_id: int) -> list[dict[str, Any]]:
    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(
                f"{settings.NOTES_DATA_SERVICE_URL}/internal/notes",
                params={"user_id": user_id},
            )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Notes data service unavailable")

    _raise_from_data_service(response)
    return response.json()


async def create_note(user_id: int, payload: NoteCreate) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(
                f"{settings.NOTES_DATA_SERVICE_URL}/internal/notes",
                json={"user_id": user_id, "title": payload.title, "content": payload.content},
            )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Notes data service unavailable")

    _raise_from_data_service(response)
    return response.json()


async def update_note(user_id: int, note_id: int, payload: NoteUpdate) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.put(
                f"{settings.NOTES_DATA_SERVICE_URL}/internal/notes/{note_id}",
                json={"user_id": user_id, "title": payload.title, "content": payload.content},
            )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Notes data service unavailable")

    _raise_from_data_service(response)
    return response.json()


async def delete_note(user_id: int, note_id: int) -> None:
    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.delete(
                f"{settings.NOTES_DATA_SERVICE_URL}/internal/notes/{note_id}",
                params={"user_id": user_id},
            )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Notes data service unavailable")

    _raise_from_data_service(response)


async def archive_note(user_id: int, note_id: int, payload: NoteArchiveUpdate) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.patch(
                f"{settings.NOTES_DATA_SERVICE_URL}/internal/notes/{note_id}/archive",
                json={"user_id": user_id, "is_archived": payload.is_archived},
            )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Notes data service unavailable")

    _raise_from_data_service(response)
    return response.json()


async def pin_note(user_id: int, note_id: int, payload: NotePinUpdate) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=settings.REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.patch(
                f"{settings.NOTES_DATA_SERVICE_URL}/internal/notes/{note_id}/pin",
                json={"user_id": user_id, "is_pinned": payload.is_pinned},
            )
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Notes data service unavailable")

    _raise_from_data_service(response)
    return response.json()
