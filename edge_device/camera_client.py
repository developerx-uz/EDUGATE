"""
EDUGATE Production Edge Client
Ushbu modul maktabdagi Mini PC / Nvidia Jetson / Raspberry Pi qurilmasida ishlaydi.
U RTSP kamera oqimidan olingan aniqlashlarni Core API ga uzatadi hamda
internet uzilganda hodisalarni lokal SQLite buferda saqlab, aloqa tiklangach yuboradi.
"""

from datetime import datetime, timedelta, timezone
import json
import logging
import os
import sqlite3
from typing import Optional
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EdgeClient")


def _tashkent_now_iso() -> str:
    return datetime.now(timezone(timedelta(hours=5))).replace(tzinfo=None).isoformat()


class EdugateEdgeClient:
    def __init__(
        self,
        core_api_url: str,
        device_token: str,
        buffer_db_path: str = "edge_offline_buffer.db",
    ):
        base = core_api_url.rstrip("/")
        self.event_url = f"{base}/api/v1/attendance/event"
        self.heartbeat_url = f"{base}/api/v1/devices/heartbeat"
        self.headers = {
            "X-Device-Token": device_token,
            "Content-Type": "application/json",
        }
        self.buffer_db_path = buffer_db_path
        self._init_buffer_db()

    def _init_buffer_db(self):
        parent = os.path.dirname(os.path.abspath(self.buffer_db_path))
        if parent:
            os.makedirs(parent, exist_ok=True)
        with sqlite3.connect(self.buffer_db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS offline_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    payload_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def send_heartbeat(self, ip_address: Optional[str] = None) -> bool:
        try:
            resp = requests.post(
                self.heartbeat_url,
                json={"ip_address": ip_address},
                headers=self.headers,
                timeout=3,
            )
            return resp.status_code == 200
        except requests.exceptions.RequestException as e:
            logger.debug(f"Heartbeat xatosi: {e}")
            return False

    def send_detection(
        self,
        student_code: Optional[str] = None,
        rfid_card_id: Optional[str] = None,
        event_type: str = "ENTRY",
        confidence: float = 0.95,
        event_time: Optional[str] = None,
    ) -> bool:
        # Avval buferdagi eski hodisalarni uzatishga harakat qilamiz
        self.flush_offline_buffer()

        payload = {
            "event_type": event_type,
            "confidence": confidence,
            "event_time": event_time or _tashkent_now_iso(),
        }
        if student_code:
            payload["student_code"] = student_code
        if rfid_card_id:
            payload["rfid_card_id"] = rfid_card_id

        try:
            resp = requests.post(
                self.event_url, json=payload, headers=self.headers, timeout=3
            )
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"Signal qabul qilindi: {data.get('message')}")
                return True
            if resp.status_code >= 500:
                self.save_to_offline_buffer(payload)
                return False
            logger.warning(f"Kutilmagan javob: {resp.status_code} - {resp.text}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Core API bilan aloqa uzildi. Hodisa lokal buferga yozildi: {e}")
            self.save_to_offline_buffer(payload)
            return False

    def save_to_offline_buffer(self, payload: dict):
        """Internet uzilganda hodisani qurilmaning SQLite xotirasida saqlab turadi."""
        with sqlite3.connect(self.buffer_db_path) as conn:
            conn.execute(
                "INSERT INTO offline_events (payload_json, created_at) VALUES (?, ?)",
                (json.dumps(payload, ensure_ascii=False), _tashkent_now_iso()),
            )
            conn.commit()

    def pending_offline_count(self) -> int:
        with sqlite3.connect(self.buffer_db_path) as conn:
            row = conn.execute("SELECT COUNT(*) FROM offline_events").fetchone()
            return int(row[0] if row else 0)

    def flush_offline_buffer(self, batch_limit: int = 50) -> int:
        """Aloqa tiklanganda buferdagi hodisalarni ketma-ket serverga uzatadi."""
        with sqlite3.connect(self.buffer_db_path) as conn:
            rows = conn.execute(
                "SELECT id, payload_json FROM offline_events ORDER BY id ASC LIMIT ?",
                (batch_limit,),
            ).fetchall()

        if not rows:
            return 0

        sent_ids = []
        for row_id, payload_json in rows:
            try:
                payload = json.loads(payload_json)
                resp = requests.post(
                    self.event_url, json=payload, headers=self.headers, timeout=3
                )
                if resp.status_code < 500:
                    sent_ids.append(row_id)
                else:
                    break
            except requests.exceptions.RequestException:
                break

        if sent_ids:
            with sqlite3.connect(self.buffer_db_path) as conn:
                placeholders = ",".join("?" for _ in sent_ids)
                conn.execute(
                    f"DELETE FROM offline_events WHERE id IN ({placeholders})",
                    sent_ids,
                )
                conn.commit()
            logger.info(f"Buferdan {len(sent_ids)} ta hodisa serverga uzatildi.")

        return len(sent_ids)


if __name__ == "__main__":
    client = EdugateEdgeClient(
        core_api_url=os.getenv("EDUGATE_API_URL", "http://localhost:8000"),
        device_token=os.getenv("EDUGATE_DEVICE_TOKEN", "edugate_dev_sample_token_here"),
    )
    logger.info("Edge Client tayyor. Buferdagi hodisalar: %d", client.pending_offline_count())
