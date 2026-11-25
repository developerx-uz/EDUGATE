import base64
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

# Point tests to an isolated temporary SQLite database before importing app modules
TEST_DB_PATH = Path(__file__).parent / "_test_edugate.db"
os.environ["USE_SQLITE"] = "True"
os.environ["SQLITE_DB_PATH"] = str(TEST_DB_PATH)
os.environ["DEBUG"] = "False"
os.environ["SECRET_KEY"] = "test-secret-key-edugate-2026-verified"

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))
sys.path.insert(0, str(ROOT_DIR))

from app.main import app  # noqa: E402
from app.core.config import get_local_now  # noqa: E402
from app.core.redis import debounce_manager  # noqa: E402
from app.core.security import get_password_hash, verify_password, needs_password_rehash  # noqa: E402
from edge_device.camera_client import EdugateEdgeClient  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()
    yield
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except OSError:
            pass


@pytest.fixture()
def client():
    debounce_manager.fallback._cache.clear()
    with TestClient(app) as c:
        yield c


def _login(client: TestClient, username: str, password: str) -> str:
    res = client.post(
        "/api/v1/auth/login-json",
        json={"username": username, "password": password},
    )
    assert res.status_code == 200, res.text
    return res.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_health_and_blocked_docs(client: TestClient):
    r_health = client.get("/health")
    assert r_health.status_code == 200
    body = r_health.json()
    assert body["status"] == "online"
    assert body["database"]["connected"] is True

    for blocked in ["/docs", "/redoc", "/openapi.json", "/edugate/docs"]:
        assert client.get(blocked).status_code == 404


def test_path_traversal_blocked(client: TestClient):
    assert client.get("/css/../../core/config.py").status_code == 404
    assert client.get("/js/../../main.py").status_code == 404
    assert client.get("/assets/../../../README.md").status_code == 404


def test_password_hashing_bcrypt_and_legacy_upgrade():
    hashed = get_password_hash("StrongPass123!")
    assert hashed.startswith("$2")
    assert verify_password("StrongPass123!", hashed)
    assert not verify_password("WrongPass", hashed)
    assert not needs_password_rehash(hashed)


def test_unauthenticated_endpoints_rejected(client: TestClient):
    assert client.post("/api/v1/students/verify-gov-id", json={"doc_number": "12345"}).status_code == 401
    assert client.post(
        "/api/v1/students/upload-photo-base64",
        json={"student_id": "abc", "image_base64": "AAAA"},
    ).status_code == 401
    assert client.get("/api/v1/attendance/today").status_code == 401
    assert client.get("/api/v1/admin/stats").status_code == 401


def test_full_school_student_attendance_rbac_and_reports_flow(client: TestClient):
    admin_token = _login(client, "admin", "Daminol007$")
    ministry_token = _login(client, "xalq_talimi", "XalqTalimi2026!")

    # 1. Create two schools (each gets 1 unique login atomically)
    s1_res = client.post(
        "/api/v1/schools/",
        headers=_auth_header(admin_token),
        json={
            "name": "101-IDUM Maktabi",
            "code": "SCH101",
            "address": "Toshkent",
            "phone": "+998712000101",
            "admin_username": "maktab_101",
            "admin_password": "School101Pass!",
        },
    )
    assert s1_res.status_code == 201, s1_res.text
    school1_id = s1_res.json()["id"]

    s2_res = client.post(
        "/api/v1/schools/",
        headers=_auth_header(admin_token),
        json={
            "name": "202-Maktab",
            "code": "SCH202",
            "admin_username": "maktab_202",
            "admin_password": "School202Pass!",
        },
    )
    assert s2_res.status_code == 201, s2_res.text
    school2_id = s2_res.json()["id"]

    school1_token = _login(client, "maktab_101", "School101Pass!")
    school2_token = _login(client, "maktab_202", "School202Pass!")

    # 2. Ministry viewer cannot mutate data
    assert (
        client.post(
            "/api/v1/students/",
            headers=_auth_header(ministry_token),
            json={
                "school_id": school1_id,
                "first_name": "Test",
                "last_name": "User",
                "student_code": "M-1",
                "class_name": "7-A",
            },
        ).status_code
        == 403
    )

    # 3. School 1 creates students (including CSV formula injection payload test)
    st1_res = client.post(
        "/api/v1/students/",
        headers=_auth_header(school1_token),
        json={
            "first_name": "=Malika",
            "last_name": "Karimova",
            "student_code": "S101-001",
            "class_name": "10-A",
            "gender": "F",
            "rfid_card_id": "RF-1001",
        },
    )
    assert st1_res.status_code == 201, st1_res.text
    st1_id = st1_res.json()["id"]

    # School 2 creates a student
    st2_res = client.post(
        "/api/v1/students/",
        headers=_auth_header(school2_token),
        json={
            "first_name": "Jasur",
            "last_name": "Aliyev",
            "student_code": "S202-001",
            "class_name": "9-B",
            "gender": "M",
        },
    )
    assert st2_res.status_code == 201, st2_res.text
    st2_id = st2_res.json()["id"]

    # School 1 cannot delete or edit School 2's student
    assert client.delete(f"/api/v1/admin/students/{st2_id}", headers=_auth_header(school1_token)).status_code == 403
    assert (
        client.put(
            f"/api/v1/admin/students/{st2_id}",
            headers=_auth_header(school1_token),
            json={"class_name": "11-A"},
        ).status_code
        == 403
    )

    # 4. Reject invalid image upload
    bad_photo = client.post(
        "/api/v1/students/upload-photo-base64",
        headers=_auth_header(school1_token),
        json={
            "student_id": st1_id,
            "image_base64": base64.b64encode(b"not-a-real-image").decode(),
        },
    )
    assert bad_photo.status_code == 400

    # Valid 1x1 PNG upload succeeds
    valid_png = base64.b64encode(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
    ).decode()
    good_photo = client.post(
        "/api/v1/students/upload-photo-base64",
        headers=_auth_header(school1_token),
        json={"student_id": st1_id, "image_base64": f"data:image/png;base64,{valid_png}"},
    )
    assert good_photo.status_code == 200, good_photo.text
    assert good_photo.json()["photo_path"].startswith("/static/uploads/students/")

    # 5. Create bidirectional device for School 1
    dev_res = client.post(
        "/api/v1/devices/",
        headers=_auth_header(school1_token),
        json={
            "name": "Bosh Kirish Turniket",
            "device_type": "TURNSTILE",
            "direction": "BIDIRECTIONAL",
            "ip_address": "192.168.1.50",
        },
    )
    assert dev_res.status_code == 201, dev_res.text
    dev_token = dev_res.json()["device_token"]

    # Heartbeat marks device online
    hb = client.post("/api/v1/devices/heartbeat", headers={"X-Device-Token": dev_token}, json={})
    assert hb.status_code == 200

    # Cross-school scan blocked
    cross_scan = client.post(
        "/api/v1/attendance/event",
        headers={"X-Device-Token": dev_token},
        json={"student_code": "S202-001", "event_type": "ENTRY"},
    )
    assert cross_scan.status_code == 200
    assert cross_scan.json()["status"] == "ERROR"

    # Update School 1 settings: start at 08:00, late threshold 10 min, end at 15:00
    set_res = client.put(
        "/api/v1/admin/settings",
        headers=_auth_header(school1_token),
        json={
            "school_start_time": "08:00",
            "late_threshold_minutes": 10,
            "school_end_time": "15:00",
            "debounce_minutes": 15,
        },
    )
    assert set_res.status_code == 200, set_res.text

    now_day = get_local_now().date()
    late_dt = datetime.combine(now_day, datetime.strptime("08:25:00", "%H:%M:%S").time())
    exit_dt = datetime.combine(now_day, datetime.strptime("13:30:00", "%H:%M:%S").time())

    # Late ENTRY scan
    ev1 = client.post(
        "/api/v1/attendance/event",
        headers={"X-Device-Token": dev_token},
        json={"student_code": "S101-001", "event_type": "ENTRY", "event_time": late_dt.isoformat(), "confidence": 0.99},
    )
    assert ev1.status_code == 200, ev1.text
    assert ev1.json()["status"] == "SUCCESS"
    assert ev1.json()["attendance_status"] == "LATE"

    # Immediate duplicate ENTRY debounced
    ev_dup = client.post(
        "/api/v1/attendance/event",
        headers={"X-Device-Token": dev_token},
        json={"student_code": "S101-001", "event_type": "ENTRY", "event_time": (late_dt + timedelta(seconds=10)).isoformat()},
    )
    assert ev_dup.json()["status"] == "IGNORED_DEBOUNCED"

    # EXIT on same BIDIRECTIONAL device is NOT blocked by ENTRY debounce and marks EARLY_LEAVE
    ev_exit = client.post(
        "/api/v1/attendance/event",
        headers={"X-Device-Token": dev_token},
        json={"student_code": "S101-001", "event_type": "EXIT", "event_time": exit_dt.isoformat()},
    )
    assert ev_exit.status_code == 200
    assert ev_exit.json()["status"] == "SUCCESS"
    assert ev_exit.json()["attendance_status"] == "EARLY_LEAVE"

    # 6. Verify admin analytics, realtime pulse, CSV export, notifications, audit logs
    pulse = client.get("/api/v1/admin/realtime/pulse", headers=_auth_header(school1_token))
    assert pulse.status_code == 200
    p_data = pulse.json()
    assert p_data["stats"]["students_count"] == 1
    assert p_data["stats"]["girls_count"] == 1
    assert p_data["stats"]["today_lates"] == 1
    assert p_data["stats"]["today_early_leaves"] == 1
    assert p_data["stats"]["online_devices_count"] == 1
    assert p_data["today_logs"][0]["school_id"] == school1_id

    csv_res = client.get("/api/v1/admin/reports/export-csv", headers=_auth_header(school1_token))
    assert csv_res.status_code == 200
    assert "'=Malika Karimova" in csv_res.text

    notifs = client.get("/api/v1/admin/notifications", headers=_auth_header(admin_token))
    assert notifs.status_code == 200
    assert any(n["type"] == "late" for n in notifs.json())

    audits = client.get("/api/v1/admin/audit-logs", headers=_auth_header(school1_token))
    assert audits.status_code == 200
    assert len(audits.json()) >= 2

    # 7. Parent link + bot API + absence request workflow
    link_admin = client.post(
        "/api/v1/parents/link-student",
        headers=_auth_header(school1_token),
        json={"full_name": "Karimov Bahodir", "phone_number": "901234567", "student_id": st1_id},
    )
    assert link_admin.status_code == 201, link_admin.text

    link_bot = client.post(
        "/api/v1/parents/link",
        json={"phone_number": "+998901234567", "telegram_chat_id": 777888999, "full_name": "Karimov Bahodir"},
    )
    assert link_bot.status_code == 200
    assert link_bot.json()["children_count"] == 1

    children_res = client.get("/api/v1/parents/777888999/children")
    assert children_res.status_code == 200
    assert len(children_res.json()) == 1
    assert children_res.json()[0]["entry_time"] == "08:25:00"

    monthly_res = client.get("/api/v1/parents/777888999/monthly-report")
    assert monthly_res.status_code == 200
    assert monthly_res.json()["children"][0]["late_days"] == 1

    abs_res = client.post(
        "/api/v1/attendance/absence-reason",
        json={"student_id": st1_id, "reason": "Shifokor ko'rigi", "parent_chat_id": 777888999},
    )
    assert abs_res.status_code == 201
    abs_id = abs_res.json()["id"]

    approve_res = client.patch(
        f"/api/v1/attendance/absence-reasons/{abs_id}",
        headers=_auth_header(school1_token),
        json={"status": "APPROVED"},
    )
    assert approve_res.status_code == 200
    assert approve_res.json()["status"] == "APPROVED"

    # 8. Landing contact & calculator orders persisted
    c_res = client.post(
        "/api/contact",
        json={"full_name": "Direktor Ali", "phone": "+998901112233", "region": "Toshkent", "school_info": "5-maktab"},
    )
    assert c_res.status_code == 200
    o_res = client.post(
        "/api/v1/orders/new",
        json={"school_name": "99-maktab", "contact_name": "Vali", "phone_number": "+998909998877", "students_count": 1200, "source": "landing_calculator"},
    )
    assert o_res.status_code == 201
    assert o_res.json()["recommended_turnstiles"] == 4
    assert o_res.json()["recommended_cameras"] == 8

    orders_list = client.get("/api/v1/orders/", headers=_auth_header(admin_token))
    assert orders_list.status_code == 200
    assert len(orders_list.json()) >= 2


def test_edge_client_offline_buffer_and_flush(tmp_path):
    buf_db = tmp_path / "edge_buf.db"
    edge = EdugateEdgeClient(
        core_api_url="http://127.0.0.1:9999",
        device_token="tok_123",
        buffer_db_path=str(buf_db),
    )

    import requests as req_lib

    with patch("edge_device.camera_client.requests.post", side_effect=req_lib.ConnectionError("offline")):
        ok = edge.send_detection(student_code="SCH01-001", event_type="ENTRY")
        assert ok is False
        assert edge.pending_offline_count() == 1

    class FakeResp:
        status_code = 200

        def json(self):
            return {"message": "OK"}

    with patch("edge_device.camera_client.requests.post", return_value=FakeResp()):
        flushed = edge.flush_offline_buffer()
        assert flushed == 1
        assert edge.pending_offline_count() == 0
