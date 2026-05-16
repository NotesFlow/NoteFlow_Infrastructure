from fastapi import APIRouter, Depends, Response, status

from app.dependencies.auth import get_current_user
from app.schemas.notes import (
    CurrentUser,
    NoteArchiveUpdate,
    NoteCreate,
    NotePinUpdate,
    NoteResponse,
    NoteUpdate,
)
from app.services import notes_data_client

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[NoteResponse])
async def list_my_notes(current_user: CurrentUser = Depends(get_current_user)):
    return await notes_data_client.list_notes(user_id=current_user.id)


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_my_note(
    payload: NoteCreate,
    current_user: CurrentUser = Depends(get_current_user),
):
    return await notes_data_client.create_note(user_id=current_user.id, payload=payload)


@router.put("/{note_id}", response_model=NoteResponse)
async def update_my_note(
    note_id: int,
    payload: NoteUpdate,
    current_user: CurrentUser = Depends(get_current_user),
):
    return await notes_data_client.update_note(user_id=current_user.id, note_id=note_id, payload=payload)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_note(
    note_id: int,
    current_user: CurrentUser = Depends(get_current_user),
):
    await notes_data_client.delete_note(user_id=current_user.id, note_id=note_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{note_id}/archive", response_model=NoteResponse)
async def archive_my_note(
    note_id: int,
    payload: NoteArchiveUpdate,
    current_user: CurrentUser = Depends(get_current_user),
):
    return await notes_data_client.archive_note(user_id=current_user.id, note_id=note_id, payload=payload)


@router.patch("/{note_id}/pin", response_model=NoteResponse)
async def pin_my_note(
    note_id: int,
    payload: NotePinUpdate,
    current_user: CurrentUser = Depends(get_current_user),
):
    return await notes_data_client.pin_note(user_id=current_user.id, note_id=note_id, payload=payload)
