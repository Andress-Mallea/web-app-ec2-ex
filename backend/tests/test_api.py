from datetime import date, timedelta


def test_health(client):
    assert client.get("/api/health").get_json() == {"status": "ok"}


def test_create_and_list_rooms(client, room):
    assert room["number"] == "101"
    assert room["status"] == "available"
    assert len(client.get("/api/rooms").get_json()) == 1


def test_room_number_is_unique(client, room):
    res = client.post("/api/rooms", json={"number": "101", "type": "single", "price_per_night": 100, "capacity": 1})
    assert res.status_code == 409


def test_room_requires_fields(client):
    res = client.post("/api/rooms", json={"number": "999"})
    assert res.status_code == 400


def test_put_room_to_maintenance(client, room):
    res = client.put(f"/api/rooms/{room['id']}", json={"status": "maintenance"})
    assert res.get_json()["status"] == "maintenance"


def test_create_guest_and_duplicate_email(client, guest):
    assert guest["email"] == "ana@example.com"
    res = client.post("/api/guests", json={"full_name": "Otra", "email": "ANA@example.com", "document": "9"})
    assert res.status_code == 409


def test_create_reservation_computes_total(client, room, guest):
    start = date.today() + timedelta(days=5)
    res = client.post("/api/reservations", json={
        "room_id": room["id"], "guest_id": guest["id"],
        "check_in": start.isoformat(), "check_out": (start + timedelta(days=3)).isoformat(),
        "guests_count": 2,
    })
    body = res.get_json()
    assert res.status_code == 201
    assert body["nights"] == 3
    assert body["total_price"] == 900
    assert body["status"] == "confirmed"


def test_reservation_status_changes(client, room, guest):
    start = date.today()
    created = client.post("/api/reservations", json={
        "room_id": room["id"], "guest_id": guest["id"],
        "check_in": start.isoformat(), "check_out": (start + timedelta(days=1)).isoformat(),
        "guests_count": 1,
    }).get_json()
    rid = created["id"]
    assert client.patch(f"/api/reservations/{rid}/check-in").get_json()["status"] == "checked_in"
    assert client.patch(f"/api/reservations/{rid}/check-out").get_json()["status"] == "checked_out"


def test_reservation_not_found(client):
    assert client.patch("/api/reservations/999/cancel").status_code == 404
