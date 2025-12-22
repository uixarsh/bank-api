import asyncio
import jwt
import uuid
from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from backend.app.auth.models import User
from backend.app.auth.schema import AccountStatusSchema, UserCreateSchema
from backend.app.auth.utils import generate_password_hash, generate_username, verify_password, create_activation_token, generate_otp
from datetime import datetime, timedelta, timezone
from backend.app.core.services.activation_email import send_activation_email
from backend.app.core.config import settings
from backend.app.core.logging import get_logger

logger = get_logger()

class UserAuthService:
    async def get_user_by_email(self, email: str, session: AsyncSession, include_inactive: bool = False) -> User | None:
        statement = select(User).where(User.email == email)

        if not include_inactive:
            statement = statement.where(User.is_active)
        
        result = await session.exec(statement)
        user = result.first()
        return user
    
    async def get_user_by_id(self, user_id: uuid.UUID, session: AsyncSession, include_inactive: bool = False) -> User | None:
        statement = select(User).where(User.id == user_id)

        if not include_inactive:
            statement = statement.where(User.is_active)
        
        result = await session.exec(statement)
        user = result.first()
        return user