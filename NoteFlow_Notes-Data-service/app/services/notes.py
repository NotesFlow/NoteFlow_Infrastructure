from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.note import Note
from app.schemas.note import (
    NoteArchiveRequest,
    NoteCreateRequest,
    NotePinRequest,
    NoteUpdateRequest,
)


def list_notes(db: Session, user_id: int) -> list[Note]:
    return (
        db.query(Note)
        .filter(Note.user_id == user_id)
        .order_by(Note.is_pinned.desc(), Note.updated_at.desc(), Note.id.desc())
        .all()
    )


def create_note(db: Session, payload: NoteCreateRequest) -> Note:
    note = Note(
        user_id=payload.user_id,
        title=payload.title,
        content=payload.content,
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return note


def update_note(db: Session, note_id: int, payload: NoteUpdateRequest) -> Note:
    note = _get_note_for_user(db=db, note_id=note_id, user_id=payload.user_id)

    note.title = payload.title
    note.content = payload.content

    db.commit()
    db.refresh(note)

    return note


def delete_note(db: Session, note_id: int, user_id: int) -> None:
    note = _get_note_for_user(db=db, note_id=note_id, user_id=user_id)

    db.delete(note)
    db.commit()


def set_note_archive(db: Session, note_id: int, payload: NoteArchiveRequest) -> Note:
    note = _get_note_for_user(db=db, note_id=note_id, user_id=payload.user_id)

    note.is_archived = payload.is_archived

    db.commit()
    db.refresh(note)

    return note


def set_note_pin(db: Session, note_id: int, payload: NotePinRequest) -> Note:
    note = _get_note_for_user(db=db, note_id=note_id, user_id=payload.user_id)

    note.is_pinned = payload.is_pinned

    db.commit()
    db.refresh(note)

    return note


def _get_note_for_user(db: Session, note_id: int, user_id: int) -> Note:
    note = (
        db.query(Note)
        .filter(Note.id == note_id, Note.user_id == user_id)
        .first()
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    return note
