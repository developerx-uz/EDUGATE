# 🏫 EDUGATE — Maktab Davomati va Kirish-Chiqish Nazorati Tizimi

**EDUGATE** — bu maktablar va ta'lim muassasalari uchun mo'ljallangan ko'p qatlamli (Edge-to-Cloud) aqlli davomat tizimi. U AI kameralar, Face ID terminallari, turniketlar, Telegram bot va Veb admin panelni yagona markaziy yadro (Core API) orqali boshqaradi.

---

## 🏗️ Arxitektura Qismlari

```
EDUGATE/
├── backend/          # Markaziy Yadro (FastAPI, SQLAlchemy 2.0, PostgreSQL/SQLite, Redis)
│                     # - Kameralardan hodisalarni qabul qilish (/api/v1/attendance/event)
│                     # - Debounce / Anti-passback spam filtri
│                     # - Kechikishlarni hisoblash va loglar
│
├── bot/              # Telegram Bot (aiogram 3.x)
│                     # - Ota-onalarni telefon raqami orqali ro'yxatdan o'tkazish
│                     # - Kirish/Chiqish va kechikishlar haqida zudlik bilan bildirishnoma
│
├── edge_device/      # Kameralar va Mini-PC (Jetson/Raspberry Pi) SDK & Simulyator
│                     # - RTSP kamera oqimidan yuzni aniqlash
│                     # - Internet uzilganda xotirada saqlash (offline resiliency)
│
├── docs/             # Tizim dizayni va arxitektura hujjatlari
│   └── ARCHITECTURE.md
│
├── docker-compose.yml# Production deployment (Postgres, Redis, Backend, Bot)
└── .env.example      # Muhit o'zgaruvchilari
```

---

## 🚀 Tezkor Boshlash (Quickstart)

### 1. Muhitni sozlash (.env)
```bash
cp .env.example .env
```

### 2. Backendni ishga tushirish (Lokal rejimda)
```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API Hujjatlari (Swagger UI): `http://127.0.0.1:8000/docs`

### 3. Docker orqali to'liq ishga tushirish (Tavsiya etiladi)
```bash
docker-compose up --build -d
```

### 4. Kamera/Qurilma orqali test qilish
```bash
cd edge_device
python simulator.py
```

---

## 🔒 Xavfsizlik va Muhandislik Imkoniyatlari
* **X-Device-Token:** Har bir kamera alohida xavfsiz token bilan ishlaydi.
* **Anti-Passback & Debounce:** O'quvchi kamera oldida uzoq turib qolsa, ota-onaga takroriy xabarlar bormaydi (15 daqiqa kesh).
* **High Performance:** FastAPI asinxron arxitekturasi tufayli bir vaqtning o'zida yuzlab eshiklardagi kameralarni kechikishlarsiz ko'tara oladi.
