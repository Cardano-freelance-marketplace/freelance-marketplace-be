from datetime import datetime, timezone
from sqlalchemy import DateTime, Boolean, ForeignKey, VARCHAR, Enum, Table, delete, insert, TIMESTAMP
from freelance_marketplace.db.sql.database import Base
from freelance_marketplace.models.enums.userRole import UserRole
from freelance_marketplace.models.enums.userType import UserType
from freelance_marketplace.models.enums.walletType import WalletType
from typing import List
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, Mapped
from starlette.exceptions import HTTPException

profile_skills = Table(
    "profile_skills",
    Base.metadata,
    Column("profile_id", ForeignKey("profiles.profile_id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.skill_id"), primary_key=True),
)

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    wallet_public_address = Column(VARCHAR(100), unique=True, nullable=False)
    wallet_type = Column(Enum(WalletType), nullable=False)
    last_login = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    user_type = Column(Enum(UserType), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.role_id"), default=UserRole.User.value)

    role = relationship("Role", back_populates="users")
    profile = relationship("Profiles", back_populates="user")


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

class Skills(Base):
    __tablename__ = "skills"

    skill_id = Column(Integer, primary_key=True, autoincrement=True)
    skill = Column(String, nullable=False, unique=True)
    profiles: Mapped[List["Profiles"]] = relationship(
        secondary=profile_skills, back_populates="skills"
    )

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     skill: str,
    ):
        try:
            skill = cls(
                skill=skill,
            )
            db.add(skill)
            await db.commit()
            await db.refresh(skill)
            return skill

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), nullable=False, unique=True)
    role_description = Column(Text, nullable=True)
    users = relationship("User", back_populates="role")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     role_name: str,
                     role_description: str,
                     role_id: int = None
    ):
        try:
            role = cls(
                role_id=role_id,
                role_name=role_name,
                role_description=role_description,
            )
            db.add(role)
            await db.commit()
            await db.refresh(role)
            return role

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def seed_roles(cls, db: AsyncSession) -> bool:
        default_roles = [
            {"role_id": UserRole.Admin.value, "role_name": UserRole.Admin.name, "role_description": f"{UserRole.Admin.name} role"},
            {"role_id": UserRole.User.value, "role_name": UserRole.User.name, "role_description": f"{UserRole.User.name} role"},
            {"role_id": UserRole.Guest.value, "role_name": UserRole.Guest.name, "role_description": f"{UserRole.Guest.name} role"},
        ]
        try:
            stmt = insert(cls).values(default_roles)  # Prepare the insert statement
            await db.execute(stmt)  # Execute the statement
            await db.commit()  # Commit the transaction
            return True
        except Exception as e:
            await db.rollback()
            return False


class Profiles(Base):
    __tablename__ = "profiles"

    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True, nullable=False)
    first_name = Column(VARCHAR(50), nullable=False)
    last_name = Column(VARCHAR(50), nullable=False)
    bio = Column(VARCHAR(1000), nullable=True)

    ##MANY TO MANY
    skills: Mapped[List[Skills]] = relationship(
        secondary=profile_skills, back_populates="profiles"
    )

    user = relationship("User", back_populates="profile", foreign_keys=[user_id])

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