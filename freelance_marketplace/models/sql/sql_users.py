from datetime import datetime, timezone

from sqlalchemy import Column, Integer, DateTime, Boolean, ForeignKey, VARCHAR, Enum, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
from starlette.exceptions import HTTPException

from freelance_marketplace.models.enums.userRole import UserRole
from freelance_marketplace.models.enums.userType import UserType
from freelance_marketplace.models.enums.walletType import WalletType

Base = declarative_base()

class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    role_id = Column(Integer, ForeignKey("roles.role_id"), default=UserRole.User.value)
    wallet_public_address = Column(VARCHAR(100), unique=True, nullable=False)
    wallet_type = Column(Enum(WalletType), nullable=False)
    last_login = Column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    user_type = Column(Enum(UserType), nullable=False)

    role = relationship("Role", back_populates="users")
    profile = relationship("Profile", back_populates="user", uselist=False)


    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     wallet_public_address: str,
                     wallet_type: WalletType,
                     user_type: UserType,

    ):
        try:
            user = cls(
                wallet_public_address=wallet_public_address,
                wallet_type=wallet_type,
                user_type=user_type,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))