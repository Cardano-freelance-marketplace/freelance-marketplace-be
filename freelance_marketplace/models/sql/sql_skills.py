from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import relationship
from starlette.exceptions import HTTPException

from freelance_marketplace.models.sql.sql_profiles import profile_skills

Base = declarative_base()

class Skills(Base):
    __tablename__ = "skills"

    skill_id = Column(Integer, primary_key=True, autoincrement=True)
    skill = Column(String, nullable=False, unique=True)

    profiles = relationship('Profile', secondary=profile_skills, back_populates="skills")

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