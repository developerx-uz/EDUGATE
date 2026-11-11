"""
EDUGATE Production Edge Client Skeleton
Ushbu modul maktabdagi Mini PC / Nvidia Jetson / Raspberry Pi qurilmasida ishlaydi.
U RTSP kamera oqimini olib, OpenCV / InsightFace orqali yuzni taniydi va EDUGATE Core API ga uzatadi.
"""

import time
import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EdgeClient")


class EdugateEdgeClient:
    def __init__(self, core_api_url: str, device_token: str):
        self.api_url = f"{core_api_url.rstrip('/')}/api/v1/attendance/event"
        self.headers = {
            "X-Device-Token": device_token,
            "Content-Type": "application/json"
        }

    def send_detection(self, student_code: str, event_type: str = "ENTRY", confidence: float = 0.95):
        payload = {
            "student_code": student_code,
            "event_type": event_type,
            "confidence": confidence
        }
        try:
            resp = requests.post(self.api_url, json=payload, headers=self.headers, timeout=3)
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Signal qabul qilindi: {data.get('message')}")
            else:
                logger.warning(f"Kutilmagan javob: {resp.status_code} - {resp.text}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Core API bilan aloqa uzildi. Hodisani lokal buferga yozamiz: {e}")
            self.save_to_offline_buffer(payload)

    def save_to_offline_buffer(self, payload: dict):
        """Internet uzilganda ma'lumotni qurilma xotirasida saqlab turish (Offline resiliency)"""
        # Kelajakda lokal SQLite yoki JSON faylga append qilinadi
        pass


if __name__ == "__main__":
    client = EdugateEdgeClient(
        core_api_url="http://localhost:8000",
        device_token="edugate_dev_sample_token_here"
    )
    logger.info("Edge Client tayyor.")
