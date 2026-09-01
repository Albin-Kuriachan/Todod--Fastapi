from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, ValidationInfo, field_validator


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    first_name: str = Field(min_length=3, max_length=50)
    last_name: str = Field(min_length=3, max_length=50)
    role: str = Field(default="user")
    password: str = Field(min_length=8, max_length=100)
    confirm_password: str = Field(min_length=8, max_length=100)

    @field_validator("confirm_password")
    @classmethod
    def confirm_password_validator(cls, v: str, info: ValidationInfo) -> str:
        if v != info.data.get("password"):
            raise ValueError("Passwords do not match")
        return v


class UserLogin(BaseModel):
    email: EmailStr = Field(None)
    username: str = Field(None)
    password: str = Field(min_length=8, max_length=100)


class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    message: str = "Login successful"


class TokenRefreshRequest(BaseModel):
    refresh_token: str


class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LogoutRequest(BaseModel):
    refresh_token: str | None = None


class UserLogoutResponse(BaseModel):
    message: str = "Logged out successfully"
