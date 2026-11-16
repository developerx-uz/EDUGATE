from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: str = "SUPERADMIN"
    school_id: Optional[str] = None
    school_name: Optional[str] = None
    is_superadmin: bool = True


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str = "SUPERADMIN"
    full_name: Optional[str] = "Hokimlik Bosh Superadmini"
    school_id: Optional[str] = None
    school_name: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

