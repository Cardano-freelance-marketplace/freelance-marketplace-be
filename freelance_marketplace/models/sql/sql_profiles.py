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

profile_skills = Table('profile_skills', Base.metadata,
    Column('profile_id', Integer, ForeignKey('profile.profile_id'), primary_key=True),
    Column('skill_id', Integer, ForeignKey('skills.id'), primary_key=True)
)


class Profiles(Base):
    __tablename__ = "profiles"

    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    first_name = Column(VARCHAR(50), nullable=False)
    last_name = Column(VARCHAR(50), nullable=False)
    bio = Column(VARCHAR(1000), nullable=True)

    skills = relationship('Skill', secondary=profile_skills, back_populates="profiles")
    user = relationship("User", back_populates="profile")

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