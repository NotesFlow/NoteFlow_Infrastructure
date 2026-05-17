from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.dependencies.db import get_db
from app.schemas.note import (
    NoteArchiveRequest,
    NoteCreateRequest,
    NotePinRequest,
    NoteResponse,
    NoteUpdateRequest,
)
from app.services.notes import (
    create_note,
    delete_note,
    list_notes,
    set_note_archive,
    set_note_pin,
    update_note,
)

router = APIRouter(prefix="/internal/notes", tags=["internal-notes"])


@router.get("", response_model=list[NoteResponse])
def get_notes(
    user_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
):
    return list_notes(db=db, user_id=user_id)


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def post_note(
    payload: NoteCreateRequest,
    db: Session = Depends(get_db),
):
    return create_note(db=db, payload=payload)


@router.put("/{note_id}", response_model=NoteResponse)
def put_note(
    note_id: int,
    payload: NoteUpdateRequest,
    db: Session = Depends(get_db),
):
    return update_note(db=db, note_id=note_id, payload=payload)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_note(
    note_id: int,
    user_id: int = Query(..., gt=0),
    db: Session = Depends(get_db),
):
    delete_note(db=db, note_id=note_id, user_id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{note_id}/archive", response_model=NoteResponse)
def patch_note_archive(
    note_id: int,
    payload: NoteArchiveRequest,
    db: Session = Depends(get_db),
):
    return set_note_archive(db=db, note_id=note_id, payload=payload)


@router.patch("/{note_id}/pin", response_model=NoteResponse)
def patch_note_pin(
    note_id: int,
    payload: NotePinRequest,
    db: Session = Depends(get_db),
):
    return set_note_pin(db=db, note_id=note_id, payload=payload)
