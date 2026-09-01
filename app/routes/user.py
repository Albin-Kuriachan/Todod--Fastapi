from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.auth_fun import authenticate_user, get_current_user, oauth2_scheme
from app.auth.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
    hash_password,
)
from app.auth.token_blacklist import blacklist_token, is_token_blacklisted
from app.database.connection import get_db
from app.models.user_models import User
from app.schemas.user import (
    LogoutRequest,
    TokenRefreshRequest,
    TokenRefreshResponse,
    UserCreate,
    UserLoginResponse,
    UserLogoutResponse,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


def _token_data(user: User) -> dict:
    return {"sub": user.username, "id": str(user.id), "role": user.role}


@router.post("/register", response_model=UserResponse)
def register_user(
    user: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to register a user",
        )

    existing_user = db.execute(
        select(User).where(
            (User.username == user.username.casefold()) | (User.email == user.email)
        )
    ).scalar_one_or_none()

    if existing_user:
        if existing_user.username == user.username.casefold():
            detail = "Username already exists"
        else:
            detail = "Email already exists"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
    user_data = user.model_dump(exclude={"confirm_password"})
    hashed_password = hash_password(user_data.pop("password"))
    new_user = User(**user_data, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=list[UserResponse])
def get_users(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "admin":
        return db.execute(select(User)).scalars().all()
    return [current_user]


@router.post("/login", response_model=UserLoginResponse)
def login(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.username.casefold(), credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = _token_data(user)
    return {
        "access_token": create_access_token(data=token_data),
        "refresh_token": create_refresh_token(data=token_data),
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_access_token(body: TokenRefreshRequest, db: Session = Depends(get_db)):
    refresh_token = body.refresh_token

    if is_token_blacklisted(refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
        )

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    return {
        "access_token": create_access_token(data=_token_data(user)),
        "token_type": "bearer",
    }


@router.post("/logout", response_model=UserLogoutResponse)
def logout_user(
    token: str = Depends(oauth2_scheme),
    body: LogoutRequest | None = None,
    current_user: User = Depends(get_current_user),
):
    blacklist_token(token)
    if body and body.refresh_token:
        blacklist_token(body.refresh_token)
    return {"message": "Logged out successfully"}
