from fastapi import APIRouter
from app.api.v1.endpoints import attendance, devices, students, schools

api_router = APIRouter()

api_router.include_router(attendance.router, prefix="/attendance", tags=["Attendance (Davomat & Kameralar)"])
api_router.include_router(devices.router, prefix="/devices", tags=["Devices (Kameralar & Turniketlar)"])
api_router.include_router(students.router, prefix="/students", tags=["Students (O'quvchilar)"])
api_router.include_router(schools.router, prefix="/schools", tags=["Schools (Maktablar)"])

