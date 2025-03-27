from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import relationship
from starlette.exceptions import HTTPException

Base = declarative_base()

class Roles(Base):
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
    ):
        try:
            role = cls(
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
    async def seed_roles(cls, db: AsyncSession):
        default_roles = [
            {"role_name": "Admin", "role_description": "Administrator role"},
            {"role_name": "User", "role_description": "Regular user role"},
            {"role_name": "Guest", "role_description": "Guest user role"},
        ]

        for role in default_roles:
            # Check if role already exists
            query = select(cls).where(cls.role_name == role["role_name"])
            result = await db.execute(query)
            existing_role = result.scalars().first()

            if not existing_role:
                await cls.create(db, role_name=role["role_name"], role_description=role["role_description"])