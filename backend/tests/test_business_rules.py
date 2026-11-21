from datetime import date, timedelta


def _create_reservation(client, room_id, guest_id, check_in, check_out, guests_count=1):
    return client.post(
        "/api/reservations",
        json={
            "room_id": room_id,
            "guest_id": guest_id,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "guests_count": guests_count,
        },
    )


def test_r1_rejects_overlapping_reservations(client, room, guest):
    start = date.today() + timedelta(days=5)
    assert _create_reservation(client, room["id"], guest["id"], start, start + timedelta(days=3)).status_code == 201

    res = _create_reservation(client, room["id"], guest["id"], start + timedelta(days=1), start + timedelta(days=4))
    assert res.status_code == 422
    assert "error" in res.get_json()


def test_r2_rejects_checkout_before_or_equal_checkin(client, room, guest):
    start = date.today() + timedelta(days=5)
    res = _create_reservation(client, room["id"], guest["id"], start, start - timedelta(days=1))
    assert res.status_code == 422
    assert "error" in res.get_json()


def test_r3_rejects_checkin_in_the_past(client, room, guest):
    yesterday = date.today() - timedelta(days=1)
    res = _create_reservation(client, room["id"], guest["id"], yesterday, date.today() + timedelta(days=1))
    assert res.status_code == 422
    assert "error" in res.get_json()


def test_r4_rejects_guests_count_exceeding_room_capacity(client, room, guest):
    start = date.today() + timedelta(days=5)
    res = _create_reservation(client, room["id"], guest["id"], start, start + timedelta(days=2), guests_count=5)
    assert res.status_code == 422
    assert "error" in res.get_json()


def test_r5_rejects_room_in_maintenance(client, room, guest):
    client.put(f"/api/rooms/{room['id']}", json={"status": "maintenance"})
    start = date.today() + timedelta(days=5)
    res = _create_reservation(client, room["id"], guest["id"], start, start + timedelta(days=2))
    assert res.status_code == 422
    assert "error" in res.get_json()


def test_r6_applies_long_stay_discount_for_seven_or_more_nights(client, room, guest):
    start = date.today() + timedelta(days=5)
    res = _create_reservation(client, room["id"], guest["id"], start, start + timedelta(days=7), guests_count=2)
    body = res.get_json()
    assert res.status_code == 201
    assert body["nights"] == 7
    assert body["total_price"] == 1890.0  # 7 * 300 * 0.90


def test_r7_cancellation_penalty_under_48h_and_free_over_48h(client, room, guest):
    # Menos de 48h: cobra primera noche
    soon = date.today() + timedelta(days=1)
    r_late = _create_reservation(client, room["id"], guest["id"], soon, soon + timedelta(days=3)).get_json()
    cancelled_late = client.patch(f"/api/reservations/{r_late['id']}/cancel")
    assert cancelled_late.status_code == 200
    assert cancelled_late.get_json()["total_price"] == 300.0

    # 48h o más: sin costo
    later = date.today() + timedelta(days=5)
    r_early = _create_reservation(client, room["id"], guest["id"], later, later + timedelta(days=3)).get_json()
    cancelled_early = client.patch(f"/api/reservations/{r_early['id']}/cancel")
    assert cancelled_early.status_code == 200
    assert cancelled_early.get_json()["total_price"] == 0.0


def test_r8_rejects_invalid_status_transitions(client, room, guest):
    today = date.today()
    r = _create_reservation(client, room["id"], guest["id"], today, today + timedelta(days=2)).get_json()

    # Check-out sin check-in previo
    res_checkout = client.patch(f"/api/reservations/{r['id']}/check-out")
    assert res_checkout.status_code == 422

    # Cancelar y luego intentar check-in
    assert client.patch(f"/api/reservations/{r['id']}/cancel").status_code == 200
    res_checkin = client.patch(f"/api/reservations/{r['id']}/check-in")
    assert res_checkin.status_code == 422


def test_r9_rejects_early_checkin_before_checkin_date(client, room, guest):
    future = date.today() + timedelta(days=3)
    r = _create_reservation(client, room["id"], guest["id"], future, future + timedelta(days=2)).get_json()

    res = client.patch(f"/api/reservations/{r['id']}/check-in")
    assert res.status_code == 422
    assert "error" in res.get_json()


def test_r10_rejects_more_than_three_active_reservations_per_guest(client, room, guest):
    base = date.today() + timedelta(days=1)
    for i in range(3):
        start = base + timedelta(days=i * 5)
        res = _create_reservation(client, room["id"], guest["id"], start, start + timedelta(days=2))
        assert res.status_code == 201

    fourth_start = base + timedelta(days=20)
    res = _create_reservation(client, room["id"], guest["id"], fourth_start, fourth_start + timedelta(days=2))
    assert res.status_code == 422
    assert "error" in res.get_json()