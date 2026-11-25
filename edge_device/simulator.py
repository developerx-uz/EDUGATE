"""
EDUGATE Edge Camera Simulator
Bu skript maktab eshigiga qo'yilgan sun'iy intellektli kamera yoki turniketni emulyatsiya qiladi.
"""

import argparse
import os
import time
from edge_device.camera_client import EdugateEdgeClient


def main():
    parser = argparse.ArgumentParser(description="EDUGATE Edge Camera Simulator")
    parser.add_argument("--url", default=os.getenv("EDUGATE_API_URL", "http://127.0.0.1:8000"))
    parser.add_argument("--token", default=os.getenv("EDUGATE_DEVICE_TOKEN", "test_camera_token_main_entrance"))
    parser.add_argument("--student", default="SCH01-2024-001", help="Student code")
    parser.add_argument("--event", default="ENTRY", choices=["ENTRY", "EXIT"])
    parser.add_argument("--spam-test", action="store_true", help="Run debounce spam test")
    args = parser.parse_args()

    client = EdugateEdgeClient(core_api_url=args.url, device_token=args.token)
    print("=== EDUGATE Kamera Emulyatori Boshlandi ===")
    print("Heartbeat:", "OK" if client.send_heartbeat() else "Ulanmadi")
    client.send_detection(student_code=args.student, event_type=args.event, confidence=0.97)

    if args.spam_test:
        print("\nSPAM / DEBOUNCE sinovi (3 marta ketma-ket):")
        for i in range(3):
            print(f"Takroriy aniqlash #{i + 1}...")
            client.send_detection(student_code=args.student, event_type=args.event, confidence=0.96)
            time.sleep(1)


if __name__ == "__main__":
    main()
