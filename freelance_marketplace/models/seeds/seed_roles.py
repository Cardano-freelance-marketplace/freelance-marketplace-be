from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from freelance_marketplace.models.sql.sql_roles import Roles

async def seed_roles(session: AsyncSession):
    default_roles = [
        {
            "role_name": "Admin",
            "role_description": "Administrator",
        },
        {
            "role_name": "User",
            "role_description": "Normal User",
        },
        {
            "role_name": "Guest",
            "role_description": "Un-logged Guest",
        },
    ]
    await session.execute(delete(Roles))
    await session.commit()

    for role in default_roles:
        await Roles.create(session, **role)
