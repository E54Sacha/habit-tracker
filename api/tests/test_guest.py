from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select, update

from app import guest as guest_module
from app.db import SessionLocal
from app.models import CheckIn, Habit, User

TODAY = datetime.now(UTC).date()


def try_as_guest(client, today=TODAY):
    return client.post("/auth/guest", json={"today": today.isoformat()})


def test_guest_gets_a_filled_demo_account(client):
    response = try_as_guest(client)
    assert response.status_code == 201
    assert response.json()["is_guest"] is True
    assert response.json()["email"].endswith("@demo.invalid")
    assert "max-age=86400" in response.headers["set-cookie"].lower()  # 24 hours

    habits = client.get("/habits", params={"today": TODAY.isoformat()}).json()
    by_name = {h["name"]: h for h in habits}
    assert list(by_name) == ["Read 10 pages", "Drink 2 litres of water", "Walk 20 minutes", "Stretch 5 minutes"]
    assert by_name["Read 10 pages"]["done_today"] is False
    assert by_name["Read 10 pages"]["streak"] == 23  # days 1..23 in a row, 24 missed
    assert by_name["Drink 2 litres of water"]["done_today"] is True
    assert by_name["Drink 2 litres of water"]["streak"] == 4  # today..3 days ago, 4 missed
    assert by_name["Stretch 5 minutes"]["streak"] == 3
    assert all(len(h["history"]) > 0 for h in habits)

    # The guest can use the app like anyone: tick today.
    read_id = by_name["Read 10 pages"]["id"]
    assert client.put(f"/habits/{read_id}/check-ins/{TODAY.isoformat()}").status_code == 204
    read = next(h for h in client.get("/habits", params={"today": TODAY.isoformat()}).json() if h["id"] == read_id)
    assert read["streak"] == 24


def test_each_guest_has_their_own_account(make_client):
    a, b = make_client(), make_client()
    assert try_as_guest(a).json()["id"] != try_as_guest(b).json()["id"]
    habit_id = a.get("/habits", params={"today": TODAY.isoformat()}).json()[0]["id"]
    assert b.delete(f"/habits/{habit_id}").status_code == 404


def test_guest_cannot_log_in_with_a_password(client, make_client):
    email = try_as_guest(client).json()["email"]
    response = make_client().post("/auth/login", json={"email": email, "password": "anything-at-all"})
    # 422: email validation already refuses the reserved .invalid domain; the login query also skips guests.
    assert response.status_code in (401, 422)


def test_old_guests_are_deleted_with_their_data(client, make_client):
    old_id = try_as_guest(client).json()["id"]
    with SessionLocal() as db:
        db.execute(update(User).where(User.id == old_id).values(created_at=func.now() - timedelta(hours=25)))
        db.commit()
    try_as_guest(make_client())  # creating a guest cleans up the expired ones
    with SessionLocal() as db:
        assert db.get(User, old_id) is None
        assert db.scalar(select(func.count()).select_from(Habit).where(Habit.user_id == old_id)) == 0
        assert db.scalar(select(func.count()).select_from(CheckIn)) > 0  # the new guest's data is still there
    assert client.get("/auth/me").status_code == 401  # the old guest's cookie no longer works


def test_guest_creation_is_capped(client, monkeypatch):
    monkeypatch.setattr(guest_module, "MAX_GUESTS_PER_HOUR", 2)
    assert try_as_guest(client).status_code == 201
    assert try_as_guest(client).status_code == 201
    assert try_as_guest(client).status_code == 429


def test_guest_needs_a_plausible_today(client):
    assert try_as_guest(client, TODAY - timedelta(days=10)).status_code == 422
