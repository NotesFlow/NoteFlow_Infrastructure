import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from app.api.routes.notes import (
    archive_my_note,
    create_my_note,
    delete_my_note,
    list_my_notes,
    pin_my_note,
    update_my_note,
)
from app.dependencies.auth import get_current_user
from app.schemas.notes import CurrentUser, NoteArchiveUpdate, NoteCreate, NotePinUpdate, NoteUpdate
from app.services import notes_data_client


@pytest.fixture
def current_user():
    return CurrentUser(id=7, username="albert", email="albert@example.com")


@pytest.mark.asyncio
async def test_get_current_user_rejects_missing_authorization_header():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Missing authorization token"


@pytest.mark.asyncio
async def test_get_current_user_rejects_invalid_authorization_header():
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(
            credentials=HTTPAuthorizationCredentials(scheme="Token", credentials="abc")
        )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid authorization header"


@pytest.mark.asyncio
async def test_list_my_notes_uses_authenticated_user_id(current_user, monkeypatch):
    async def fake_list_notes(*, user_id: int):
        assert user_id == current_user.id
        return [{"id": 1, "user_id": user_id}]

    monkeypatch.setattr(notes_data_client, "list_notes", fake_list_notes)

    response = await list_my_notes(current_user=current_user)

    assert response == [{"id": 1, "user_id": current_user.id}]


@pytest.mark.asyncio
async def test_create_my_note_uses_authenticated_user_id(current_user, monkeypatch):
    async def fake_create_note(*, user_id: int, payload: NoteCreate):
        assert user_id == current_user.id
        assert payload.title == "Created through public API"
        assert payload.content == "Body"
        return {"id": 1, "user_id": user_id, "title": payload.title, "content": payload.content}

    monkeypatch.setattr(notes_data_client, "create_note", fake_create_note)

    response = await create_my_note(
        payload=NoteCreate(title="Created through public API", content="Body"),
        current_user=current_user,
    )

    assert response["user_id"] == current_user.id
    assert response["title"] == "Created through public API"


@pytest.mark.asyncio
async def test_update_my_note_propagates_not_found(current_user, monkeypatch):
    async def fake_update_note(*, user_id: int, note_id: int, payload: NoteUpdate):
        raise HTTPException(status_code=404, detail="Note not found")

    monkeypatch.setattr(notes_data_client, "update_note", fake_update_note)

    with pytest.raises(HTTPException) as exc_info:
        await update_my_note(
            note_id=99,
            payload=NoteUpdate(title="Updated title", content="Updated content"),
            current_user=current_user,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Note not found"


@pytest.mark.asyncio
async def test_delete_my_note_returns_204_response(current_user, monkeypatch):
    async def fake_delete_note(*, user_id: int, note_id: int):
        assert user_id == current_user.id
        assert note_id == 5

    monkeypatch.setattr(notes_data_client, "delete_note", fake_delete_note)

    response = await delete_my_note(note_id=5, current_user=current_user)

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_archive_my_note_propagates_downstream_error(current_user, monkeypatch):
    async def fake_archive_note(*, user_id: int, note_id: int, payload: NoteArchiveUpdate):
        raise HTTPException(status_code=503, detail="Notes data service unavailable")

    monkeypatch.setattr(notes_data_client, "archive_note", fake_archive_note)

    with pytest.raises(HTTPException) as exc_info:
        await archive_my_note(
            note_id=3,
            payload=NoteArchiveUpdate(is_archived=True),
            current_user=current_user,
        )

    assert exc_info.value.status_code == 503
    assert exc_info.value.detail == "Notes data service unavailable"


@pytest.mark.asyncio
async def test_pin_my_note_uses_authenticated_user_id(current_user, monkeypatch):
    async def fake_pin_note(*, user_id: int, note_id: int, payload: NotePinUpdate):
        assert user_id == current_user.id
        assert note_id == 3
        assert payload.is_pinned is True
        return {"id": note_id, "user_id": user_id, "is_pinned": True}

    monkeypatch.setattr(notes_data_client, "pin_note", fake_pin_note)

    response = await pin_my_note(
        note_id=3,
        payload=NotePinUpdate(is_pinned=True),
        current_user=current_user,
    )

    assert response["user_id"] == current_user.id
    assert response["is_pinned"] is True
