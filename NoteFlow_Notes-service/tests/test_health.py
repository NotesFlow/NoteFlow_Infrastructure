from app.api.routes.health import health


def test_health():
    response = health()

    assert response["status"] == "ok"
    assert response["service"] == "NoteFlow Notes Service"
