from fastapi import APIRouter
from app.api.v1.endpoints import attendance, devices, students, schools, auth, admin, teachers

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Auth (Superadmin Autentifikatsiya)"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin (Superadmin Boshqaruv & Stats)"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance (Davomat & Kameralar)"])
api_router.include_router(devices.router, prefix="/devices", tags=["Devices (Kameralar & Turniketlar)"])
api_router.include_router(students.router, prefix="/students", tags=["Students (O'quvchilar)"])
api_router.include_router(teachers.router, prefix="/teachers", tags=["Teachers (O'qituvchilar)"])
api_router.include_router(schools.router, prefix="/schools", tags=["Schools (Maktablar)"])
