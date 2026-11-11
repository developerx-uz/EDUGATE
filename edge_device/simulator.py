"""
EDUGATE Edge Camera Simulator
Bu skript maktab eshigiga qo'yilgan sun'iy intellektli kamera yoki turniketni emulyatsiya qiladi.
U markaziy yadroga (Core API) hodisalarni yuborib, tizimning ishlashini to'liq tekshiradi.
"""

import time
import requests

API_URL = "http://127.0.0.1:8000/api/v1/attendance/event"

# Bu tokenni backend /devices/ orqali ro'yxatdan o'tkazganda olasiz
# Sinov uchun backendda avtomatik o'rnatilgan yoki mavjud token:
DEVICE_TOKEN = "test_camera_token_main_entrance"


def simulate_camera_event(student_code: str, event_type: str = "ENTRY", confidence: float = 0.96):
    headers = {
        "X-Device-Token": DEVICE_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "student_code": student_code,
        "event_type": event_type,
        "confidence": confidence
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=5)
        print(f"[{event_type}] O'quvchi: {student_code} -> Status: {response.status_code}")
        print("Javob:", response.json())
        print("-" * 50)
    except Exception as e:
        print(f"Serverga ulanib bo'lmadi ({API_URL}): {e}")


if __name__ == "__main__":
    print("=== EDUGATE Kamera Emulyatori Boshlandi ===")
    print("1. O'quvchi kirishini simulyatsiya qilish...")
    simulate_camera_event("SCH01-2024-001", event_type="ENTRY")

    print("\n2. SPAM / DEBOUNCE sinovi (O'quvchi kamera oldida 3 soniya turib qoldi):")
    for i in range(3):
        print(f"Takroriy aniqlash #{i+1}...")
        simulate_camera_event("SCH01-2024-001", event_type="ENTRY")
        time.sleep(1)
