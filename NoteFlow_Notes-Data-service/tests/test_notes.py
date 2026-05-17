def test_note_crud_flow(client):
    create_response = client.post(
        "/internal/notes",
        json={
            "user_id": 1,
            "title": "Prima nota",
            "content": "Continut initial",
        },
    )

    assert create_response.status_code == 201
    created_note = create_response.json()
    note_id = created_note["id"]
    assert created_note["title"] == "Prima nota"
    assert created_note["content"] == "Continut initial"
    assert created_note["is_archived"] is False
    assert created_note["is_pinned"] is False

    list_response = client.get("/internal/notes", params={"user_id": 1})

    assert list_response.status_code == 200
    notes = list_response.json()
    assert len(notes) == 1
    assert notes[0]["id"] == note_id

    update_response = client.put(
        f"/internal/notes/{note_id}",
        json={
            "user_id": 1,
            "title": "Nota actualizata",
            "content": "Continut actualizat",
        },
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Nota actualizata"
    assert update_response.json()["content"] == "Continut actualizat"

    archive_response = client.patch(
        f"/internal/notes/{note_id}/archive",
        json={
            "user_id": 1,
            "is_archived": True,
        },
    )

    assert archive_response.status_code == 200
    assert archive_response.json()["is_archived"] is True

    pin_response = client.patch(
        f"/internal/notes/{note_id}/pin",
        json={
            "user_id": 1,
            "is_pinned": True,
        },
    )

    assert pin_response.status_code == 200
    assert pin_response.json()["is_pinned"] is True

    delete_response = client.delete(f"/internal/notes/{note_id}", params={"user_id": 1})

    assert delete_response.status_code == 204
    assert delete_response.text == ""


def test_note_operations_are_filtered_by_user_id(client):
    create_response = client.post(
        "/internal/notes",
        json={
            "user_id": 1,
            "title": "Nota user 1",
            "content": "Ascunsa pentru altii",
        },
    )

    assert create_response.status_code == 201
    note_id = create_response.json()["id"]

    other_user_list_response = client.get("/internal/notes", params={"user_id": 2})
    assert other_user_list_response.status_code == 200
    assert other_user_list_response.json() == []

    other_user_update_response = client.put(
        f"/internal/notes/{note_id}",
        json={
            "user_id": 2,
            "title": "Nu ar trebui sa mearga",
            "content": "Nu ar trebui sa mearga",
        },
    )

    assert other_user_update_response.status_code == 404
    assert other_user_update_response.json()["detail"] == "Note not found"


def test_note_returns_404_after_delete(client):
    create_response = client.post(
        "/internal/notes",
        json={
            "user_id": 1,
            "title": "Nota temporara",
            "content": "Va fi stearsa",
        },
    )

    assert create_response.status_code == 201
    note_id = create_response.json()["id"]

    delete_response = client.delete(f"/internal/notes/{note_id}", params={"user_id": 1})
    assert delete_response.status_code == 204

    update_response = client.put(
        f"/internal/notes/{note_id}",
        json={
            "user_id": 1,
            "title": "Nu exista",
            "content": "Nu exista",
        },
    )

    assert update_response.status_code == 404
    assert update_response.json()["detail"] == "Note not found"
