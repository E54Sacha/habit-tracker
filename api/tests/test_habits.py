from datetime import UTC, datetime, timedelta

import pytest

from app.routers.habits import MAX_HABITS

TODAY = datetime.now(UTC).date()


@pytest.fixture
def ada(make_client):
    """A logged-in browser."""
    browser = make_client()
    assert browser.post("/auth/signup", json={"email": "ada@example.com", "password": "ada-password"}).status_code == 201
    return browser


@pytest.fixture
def bob(make_client):
    browser = make_client()
    assert browser.post("/auth/signup", json={"email": "bob@example.com", "password": "bob-password"}).status_code == 201
    return browser


def habits(browser, today=TODAY):
    return browser.get("/habits", params={"today": today.isoformat()})


def create(browser, name="Read 10 pages"):
    return browser.post("/habits", json={"name": name})


def test_create_and_list_in_creation_order(ada):
    assert habits(ada).json() == []
    first = create(ada, "Read 10 pages")
    assert first.status_code == 201
    assert first.json() == {"id": first.json()["id"], "name": "Read 10 pages", "done_today": False, "streak": 0, "history": []}
    create(ada, "Drink water")
    assert [h["name"] for h in habits(ada).json()] == ["Read 10 pages", "Drink water"]


def test_names_are_cleaned_and_checked(ada):
    assert create(ada, "  Walk \n the   dog ").json()["name"] == "Walk the dog"
    assert create(ada, "   ").status_code == 422
    assert create(ada, "x" * 61).status_code == 422


def test_rename(ada):
    habit_id = create(ada).json()["id"]
    response = ada.patch(f"/habits/{habit_id}", params={"today": TODAY.isoformat()}, json={"name": "Read 20 pages"})
    assert response.status_code == 200
    assert response.json()["name"] == "Read 20 pages"
    assert habits(ada).json()[0]["name"] == "Read 20 pages"


def test_tick_and_untick_today(ada):
    habit_id = create(ada).json()["id"]
    url = f"/habits/{habit_id}/check-ins/{TODAY.isoformat()}"
    assert ada.put(url).status_code == 204
    assert ada.put(url).status_code == 204  # ticking twice is fine (idempotent)
    assert habits(ada).json()[0]["done_today"] is True
    assert habits(ada).json()[0]["streak"] == 1
    assert habits(ada).json()[0]["history"] == [TODAY.isoformat()]
    assert habits(ada, TODAY + timedelta(days=1)).json()[0]["done_today"] is False  # a new day starts unticked
    assert ada.delete(url).status_code == 204
    assert ada.delete(url).status_code == 204
    assert habits(ada).json()[0]["done_today"] is False


def test_rename_keeps_the_tick(ada):
    habit_id = create(ada).json()["id"]
    ada.put(f"/habits/{habit_id}/check-ins/{TODAY.isoformat()}")
    response = ada.patch(f"/habits/{habit_id}", params={"today": TODAY.isoformat()}, json={"name": "New name"})
    assert response.json()["done_today"] is True


def test_only_today_can_be_ticked(ada):
    habit_id = create(ada).json()["id"]
    # Yesterday and tomorrow (UTC) are fine: it is already or still that day somewhere on Earth.
    for offset in (-1, 1):
        assert ada.put(f"/habits/{habit_id}/check-ins/{(TODAY + timedelta(days=offset)).isoformat()}").status_code == 204
    for offset in (-2, 2, -30):
        day = (TODAY + timedelta(days=offset)).isoformat()
        assert ada.put(f"/habits/{habit_id}/check-ins/{day}").status_code == 422
        assert ada.delete(f"/habits/{habit_id}/check-ins/{day}").status_code == 422
    assert habits(ada, TODAY - timedelta(days=5)).status_code == 422
    assert ada.put(f"/habits/{habit_id}/check-ins/not-a-date").status_code == 422


def test_delete_removes_habit_and_its_check_ins(ada):
    habit_id = create(ada).json()["id"]
    ada.put(f"/habits/{habit_id}/check-ins/{TODAY.isoformat()}")
    assert ada.delete(f"/habits/{habit_id}").status_code == 204
    assert habits(ada).json() == []
    assert ada.delete(f"/habits/{habit_id}").status_code == 404


def test_users_cannot_see_or_touch_each_others_habits(ada, bob):
    habit_id = create(ada).json()["id"]
    assert habits(bob).json() == []
    day = TODAY.isoformat()
    assert bob.patch(f"/habits/{habit_id}", params={"today": day}, json={"name": "Mine now"}).status_code == 404
    assert bob.put(f"/habits/{habit_id}/check-ins/{day}").status_code == 404
    assert bob.delete(f"/habits/{habit_id}/check-ins/{day}").status_code == 404
    assert bob.delete(f"/habits/{habit_id}").status_code == 404
    assert habits(ada).json()[0] == {"id": habit_id, "name": "Read 10 pages", "done_today": False, "streak": 0, "history": []}


def test_habits_need_a_login(client):
    assert habits(client).status_code == 401
    assert create(client).status_code == 401


def test_habit_limit(ada):
    for i in range(MAX_HABITS):
        assert create(ada, f"Habit {i}").status_code == 201
    assert create(ada, "One too many").status_code == 409
