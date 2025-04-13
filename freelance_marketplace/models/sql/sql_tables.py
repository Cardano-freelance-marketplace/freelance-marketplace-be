from datetime import datetime, timezone
from sqlalchemy import Boolean, ForeignKey, VARCHAR, Table, insert, TIMESTAMP, Float, ARRAY, \
    DECIMAL, select
from sqlalchemy.exc import IntegrityError
from freelance_marketplace.db.sql.database import Base
from freelance_marketplace.models.enums.milestoneStatus import MilestoneStatus as MilestoneStatusEnum
from freelance_marketplace.models.enums.userRole import UserRole
from freelance_marketplace.models.enums.walletType import WalletType as WalletTypeEnum
from typing import List
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, Mapped
from starlette.exceptions import HTTPException
from freelance_marketplace.models.enums.proposalStatus import ProposalStatus as ProposalStatusEnum
from freelance_marketplace.models.enums.serviceStatus import ServiceStatus as ServiceStatusEnum
from freelance_marketplace.models.enums.requestStatus import RequestStatus as RequestStatusEnum
from freelance_marketplace.models.enums.orderStatus import OrderStatus as OrderStatusEnum

profile_skills = Table(
    "profile_skills",
    Base.metadata,
    Column("profile_id", ForeignKey("profiles.profile_id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.skill_id"), primary_key=True),
)

order_milestone_association = Table(
    'order_milestone_association',
    Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.order_id')),
    Column('milestone_id', Integer, ForeignKey('milestones.milestone_id'))
)

proposal_milestone_association = Table(
    'proposal_milestone_association',
    Base.metadata,
    Column('proposal_id', Integer, ForeignKey('proposals.proposal_id')),
    Column('milestone_id', Integer, ForeignKey('milestones.milestone_id'))
)

request_milestone_association = Table(
    'request_milestone_association',
    Base.metadata,
    Column('request_id', Integer, ForeignKey('requests.request_id')),
    Column('milestone_id', Integer, ForeignKey('milestones.milestone_id'))
)

service_milestone_association = Table(
    'service_milestone_association',
    Base.metadata,
    Column('service_id', Integer, ForeignKey('services.service_id')),
    Column('milestone_id', Integer, ForeignKey('milestones.milestone_id'))
)

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    creation_date = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    deleted = Column(Boolean, nullable=False, default=False)
    wallet_public_address = Column(VARCHAR(100), unique=True, nullable=False)
    wallet_type_id = Column(Integer, ForeignKey("wallet_types.wallet_type_id", ondelete="SET NULL"), default=WalletTypeEnum.Lace.value)
    last_login = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    role_id = Column(Integer, ForeignKey("roles.role_id", ondelete="SET NULL"), default=UserRole.User.value)

    freelancer_order_milestones = relationship("Milestones",  foreign_keys=lambda: [Milestones.freelancer_id], back_populates="freelancers_orders")
    client_order_milestones = relationship("Milestones", foreign_keys=lambda: [Milestones.client_id], back_populates="clients_orders")

    freelancer_proposal_milestones = relationship("Milestones", foreign_keys=lambda: [Milestones.freelancer_id], back_populates="freelancers_proposals")
    client_proposal_milestones = relationship("Milestones", foreign_keys=lambda: [Milestones.client_id], back_populates="clients_proposals")

    freelancer_service_milestones = relationship("Milestones", foreign_keys=lambda: [Milestones.freelancer_id], back_populates="freelancers_services")
    client_service_milestones = relationship("Milestones", foreign_keys=lambda: [Milestones.client_id], back_populates="clients_services")

    freelancer_request_milestones = relationship("Milestones", foreign_keys=lambda: [Milestones.freelancer_id], back_populates="freelancers_requests")
    client_request_milestones = relationship("Milestones", foreign_keys=lambda: [Milestones.client_id], back_populates="clients_requests")

    client_transactions = relationship("Transaction", foreign_keys="[Transaction.client_id]", back_populates="client")
    freelancer_transactions = relationship("Transaction", foreign_keys="[Transaction.freelancer_id]", back_populates="freelancer")
    role = relationship("Role", back_populates="users")
    profile = relationship("Profiles", back_populates="user", cascade="all, delete-orphan", uselist=False)
    proposals = relationship("Proposal", back_populates="freelancer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="client")
    requests = relationship("Requests", back_populates="client")
    services = relationship("Services", back_populates="freelancer")
    wallet_type = relationship("WalletTypes", back_populates="users")
    received_reviews = relationship("Review", foreign_keys="[Review.reviewee_id]", back_populates="reviewee")
    given_reviews = relationship("Review", foreign_keys="[Review.reviewer_id]", back_populates="reviewer")


    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     wallet_public_address: str,
                     wallet_type_id: int = WalletTypeEnum.Lace.value,

    ):
        try:
            user = cls(
                wallet_public_address=wallet_public_address,
                wallet_type_id=wallet_type_id,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(
            cls,
            db: AsyncSession,
            user,
            data: dict,
            request_user
    ) -> bool:
        try:
            if data:
                if "user_id" in data:
                    data.pop("user_id")  # Prevent changing user ID

                for key, value in data.items():
                    if value is None:
                        continue

                    if key == "wallet_public_address":
                        query = await db.execute(
                            select(User).where(
                                User.wallet_public_address == value,
                                User.user_id != user.user_id
                            )
                        )
                        existing_user = query.scalars().first()
                        if existing_user:
                            raise HTTPException(
                                status_code=400,
                                detail="Wallet public address already exists."
                            )

                    if hasattr(user, key):
                        setattr(user, key, value)

            user.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(user)
            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    @classmethod
    async def seed_users(cls, db: AsyncSession) -> bool:
        default_users = [
            {"wallet_public_address": "testewalletaddress123", "wallet_type_id": 1}
        ]
        try:

            existing_users = await db.execute(
                select(cls.wallet_public_address).where(cls.wallet_public_address.in_([m["wallet_public_address"] for m in default_users]))
            )
            existing_wallets_ids = {m[0] for m in existing_users.fetchall()}

            new_users = [m for m in default_users if m["wallet_public_address"] not in existing_wallets_ids]

            if new_users:
                stmt = insert(cls).values(new_users)
                await db.execute(stmt)
                await db.commit()

            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class WalletTypes(Base):
    __tablename__ = "wallet_types"

    wallet_type_id = Column(Integer, primary_key=True, autoincrement=True)
    deleted = Column(Boolean, nullable=False, default=False)
    wallet_type_name = Column(VARCHAR(50), nullable=False)

    users = relationship("User", back_populates="wallet_type")

    @classmethod
    async def seed_types(cls, db: AsyncSession) -> bool:
        default_types = [
            {"wallet_type_id": WalletTypeEnum.Lace.value, "wallet_type_name": WalletTypeEnum.Lace.name},
            {"wallet_type_id": WalletTypeEnum.Yoroi.value, "wallet_type_name": WalletTypeEnum.Yoroi.name},
            {"wallet_type_id": WalletTypeEnum.Daedalus.value, "wallet_type_name": WalletTypeEnum.Daedalus.name},
            {"wallet_type_id": WalletTypeEnum.Nami.value, "wallet_type_name": WalletTypeEnum.Nami.name},
            {"wallet_type_id": WalletTypeEnum.Flint.value, "wallet_type_name": WalletTypeEnum.Flint.name},
            {"wallet_type_id": WalletTypeEnum.WalletConnect.value,
             "wallet_type_name": WalletTypeEnum.WalletConnect.name},
            {"wallet_type_id": WalletTypeEnum.Exodus.value, "wallet_type_name": WalletTypeEnum.Exodus.name},
            {"wallet_type_id": WalletTypeEnum.AdaLite.value, "wallet_type_name": WalletTypeEnum.AdaLite.name},
            {"wallet_type_id": WalletTypeEnum.CardanoWalletConnect.value,
             "wallet_type_name": WalletTypeEnum.CardanoWalletConnect.name},
            {"wallet_type_id": WalletTypeEnum.TrustWallet.value, "wallet_type_name": WalletTypeEnum.TrustWallet.name},
            {"wallet_type_id": WalletTypeEnum.Typhon.value, "wallet_type_name": WalletTypeEnum.Typhon.name},
            {"wallet_type_id": WalletTypeEnum.Blockfrost.value, "wallet_type_name": WalletTypeEnum.Blockfrost.name},
            {"wallet_type_id": WalletTypeEnum.GeroWallet.value, "wallet_type_name": WalletTypeEnum.GeroWallet.name},
        ]

        try:
            existing_types = await db.execute(
                select(cls.wallet_type_id).where(cls.wallet_type_id.in_([m["wallet_type_id"] for m in default_types]))
            )
            existing_wallet_type_ids = {m[0] for m in existing_types.fetchall()}

            new_types = [m for m in default_types if m["wallet_type_id"] not in existing_wallet_type_ids]

            if new_types:
                stmt = insert(cls).values(new_types)
                await db.execute(stmt)
                await db.commit()

            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class Skills(Base):
    __tablename__ = "skills"

    skill_id = Column(Integer, primary_key=True, autoincrement=True)
    skill = Column(String, nullable=False, unique=True)
    deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
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

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(cls, db: AsyncSession, skill_id: int, data: dict):
        try:
            # Fetch the skill by ID
            query = await db.execute(select(cls).where(cls.skill_id == skill_id))
            skill = query.scalars().first()

            if not skill:
                raise HTTPException(status_code=404, detail="Skill not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(skill, key) and value is not None:
                    setattr(skill, key, value)

            await db.commit()
            await db.refresh(skill)
            return skill

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


class Role(Base):
    __tablename__ = "roles"

    role_id = Column(Integer, primary_key=True, autoincrement=True)
    deleted = Column(Boolean, nullable=False, default=False)
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

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(cls, db: AsyncSession, role_id: int, data: dict):
        try:
            # Fetch the role by ID
            query = await db.execute(select(cls).where(cls.role_id == role_id))
            role = query.scalars().first()

            if not role:
                raise HTTPException(status_code=404, detail="Role not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(role, key) and value is not None:
                    setattr(role, key, value)

            await db.commit()
            await db.refresh(role)
            return role

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

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
            existing_roles = await db.execute(
                select(cls.role_id).where(cls.role_id.in_([m["role_id"] for m in default_roles]))
            )
            existing_role_ids = {m[0] for m in existing_roles.fetchall()}

            new_roles = [m for m in default_roles if m["role_id"] not in existing_role_ids]

            if new_roles:
                stmt = insert(cls).values(new_roles)
                await db.execute(stmt)
                await db.commit()

            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


class Profiles(Base):
    __tablename__ = "profiles"

    profile_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), unique=True, nullable=False)
    first_name = Column(VARCHAR(50), nullable=False)
    last_name = Column(VARCHAR(50), nullable=False)
    bio = Column(VARCHAR(1000), nullable=True)
    profile_picture_identifier = Column(VARCHAR(255), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))

    ##MANY TO MANY
    skills: Mapped[List[Skills]] = relationship(
        secondary=profile_skills, back_populates="profiles"
    )

    user = relationship("User", back_populates="profile", foreign_keys=[user_id])

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     first_name: str,
                     user_id: int,
                     last_name: str,
                     bio: str = None,

    ):
        try:
            profile = cls(
                user_id=user_id,
                first_name=first_name,
                last_name=last_name,
                bio=bio,
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)
            return profile

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(
            cls,
            db: AsyncSession,
            profile_id: int,
            data: dict
    ):
        try:
            # Fetch the profile by ID
            query = await db.execute(select(cls).where(cls.profile_id == profile_id))
            profile = query.scalars().first()

            if not profile:
                raise HTTPException(status_code=404, detail="Profile not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(profile, key) and value is not None:
                    setattr(profile, key, value)

            await db.commit()
            await db.refresh(profile)
            return profile

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


class Requests(Base):
    __tablename__ = "requests"

    request_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    sub_category_id = Column(Integer, ForeignKey("sub_categories.sub_category_id", ondelete='SET NULL'), nullable=False)
    total_price = Column(Float, nullable=False)
    tags = Column(ARRAY(String), nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)
    client_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=False)

    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    request_status_id = Column(Integer, ForeignKey("request_status.request_status_id", ondelete="SET NULL"), default=RequestStatusEnum.DRAFT.value, nullable=True)

    # Relationships
    request_status = relationship("RequestStatus", back_populates="requests")
    client = relationship("User", foreign_keys=[client_id], back_populates="requests")
    sub_category = relationship("SubCategory", back_populates="requests")
    milestones = relationship("Milestones", secondary=request_milestone_association, back_populates="requests", cascade="all")
    proposals = relationship("Proposal", back_populates="request", cascade="all, delete-orphan")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     title: str,
                     description: str,
                     sub_category_id: int,
                     total_price: float,
                     tags: list,
                     client_id: int,
     ):
        try:
            request = cls(
                title=title,
                description=description,
                sub_category_id=sub_category_id,
                total_price=total_price,
                tags=tags,
                client_id=client_id,
            )
            db.add(request)
            await db.commit()
            await db.refresh(request)
            return request

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(cls, db: AsyncSession, request_id: int, data: dict):
        try:
            # Fetch the request by ID
            query = await db.execute(select(cls).where(cls.request_id == request_id))
            request = query.scalars().first()

            if not request:
                raise HTTPException(status_code=404, detail="Request not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(request, key) and value is not None:
                    setattr(request, key, value)

            await db.commit()
            await db.refresh(request)
            return request

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class RequestStatus(Base):
    __tablename__ = "request_status"
    request_status_id = Column(Integer, primary_key=True, autoincrement=True)
    request_status_name = Column(String(50), nullable=False)
    request_status_description = Column(Text, nullable=False)

    requests = relationship("Requests", back_populates="request_status")

    @classmethod
    async def seed_status(cls, db: AsyncSession) -> bool:
        default_status = [
            {"request_status_id": RequestStatusEnum.CANCELED.value, "request_status_name": RequestStatusEnum.CANCELED.name, "request_status_description": f""},
            {"request_status_id": RequestStatusEnum.DRAFT.value, "request_status_name": RequestStatusEnum.DRAFT.name, "request_status_description": f""},
            {"request_status_id": RequestStatusEnum.REQUESTING_FREELANCER.value, "request_status_name": RequestStatusEnum.REQUESTING_FREELANCER.name, "request_status_description": f""},
            {"request_status_id": RequestStatusEnum.IN_PROGRESS.value, "request_status_name": RequestStatusEnum.IN_PROGRESS.name, "request_status_description": f""},
            {"request_status_id": RequestStatusEnum.COMPLETED.value, "request_status_name": RequestStatusEnum.COMPLETED.name, "request_status_description": f""},
        ]
        try:

            existing_status = await db.execute(
                select(cls.request_status_id).where(cls.request_status_id.in_([m["request_status_id"] for m in default_status]))
            )
            existing_request_status_ids = {m[0] for m in existing_status.fetchall()}

            new_statuses = [m for m in default_status if m["request_status_id"] not in existing_request_status_ids]

            if new_statuses:
                stmt = insert(cls).values(new_statuses)
                await db.execute(stmt)
                await db.commit()

            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class Services(Base):
    __tablename__ = "services"

    service_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    sub_category_id = Column(Integer, ForeignKey("sub_categories.sub_category_id", ondelete='SET NULL'), nullable=False)
    total_price = Column(Float, nullable=True)
    tags = Column(ARRAY(String), nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)
    freelancer_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    service_status_id = Column(Integer, ForeignKey("service_status.service_status_id", ondelete="SET NULL"), default=ServiceStatusEnum.DRAFT.value,  nullable=True)

    # Relationships
    status = relationship("ServiceStatus", back_populates="services")
    freelancer = relationship("User", foreign_keys=[freelancer_id], back_populates="services")
    sub_category = relationship("SubCategory", back_populates="services")
    milestones = relationship("Milestones", secondary=service_milestone_association, back_populates="services", cascade="all")
    orders = relationship("Order", back_populates="service", cascade="all, delete-orphan")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     title: str,
                     description: str,
                     sub_category_id: int,
                     total_price: float,
                     tags: list,
                     freelancer_id: int,
     ):
        try:
            service = cls(
                title=title,
                description=description,
                sub_category_id=sub_category_id,
                total_price=total_price,
                tags=tags,
                freelancer_id=freelancer_id,
            )
            db.add(service)
            await db.commit()
            await db.refresh(service)
            return service

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(cls, db: AsyncSession, service_id: int, data: dict):
        try:
            # Fetch the service by ID
            query = await db.execute(select(cls).where(cls.service_id == service_id))
            service = query.scalars().first()

            if not service:
                raise HTTPException(status_code=404, detail="Service not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(service, key) and value is not None:
                    setattr(service, key, value)

            await db.commit()
            await db.refresh(service)
            return service

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class ServiceStatus(Base):
    __tablename__ = "service_status"
    service_status_id = Column(Integer, primary_key=True, autoincrement=True)
    service_status_name = Column(String(50), nullable=False)
    service_status_description = Column(Text, nullable=False)

    services = relationship("Services", back_populates="status")

    @classmethod
    async def seed_status(cls, db: AsyncSession) -> bool:
        default_status = [
            {"service_status_id": ServiceStatusEnum.CANCELED.value, "service_status_name": ServiceStatusEnum.CANCELED.name, "service_status_description": f""},
            {"service_status_id": ServiceStatusEnum.DRAFT.value, "service_status_name": ServiceStatusEnum.DRAFT.name, "service_status_description": f""},
            {"service_status_id": ServiceStatusEnum.AVAILABLE.value, "service_status_name": ServiceStatusEnum.AVAILABLE.name, "service_status_description": f""},
            {"service_status_id": ServiceStatusEnum.CLOSED.value, "service_status_name": ServiceStatusEnum.CLOSED.name, "service_status_description": f""},
        ]
        try:

            existing_status = await db.execute(
                select(cls.service_status_id).where(cls.service_status_id.in_([m["service_status_id"] for m in default_status]))
            )
            existing_service_status_ids = {m[0] for m in existing_status.fetchall()}

            new_statuses = [m for m in default_status if m["service_status_id"] not in existing_service_status_ids]

            if new_statuses:
                stmt = insert(cls).values(new_statuses)
                await db.execute(stmt)
                await db.commit()

            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


class Milestones(Base):
    __tablename__ = "milestones"

    milestone_id = Column(Integer, primary_key=True, autoincrement=True)
    client_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=False)
    freelancer_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=False)

    milestone_tx_hash = Column(String(4096), nullable=False)
    milestone_text = Column(Text, nullable=False)
    reward_amount = Column(Float, nullable=False)
    deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    client_approved = Column(Boolean, nullable=False, default=False)
    freelancer_approved = Column(Boolean, nullable=False, default=False)
    milestone_status_id = Column(Integer, ForeignKey("milestone_status.milestone_status_id", ondelete="SET NULL"), nullable=True)

    # Relationships
    milestone_status = relationship("MilestoneStatus", back_populates="milestones")

    freelancers_orders = relationship("User", foreign_keys=[client_id], back_populates="freelancer_order_milestones")
    clients_orders = relationship("User", foreign_keys=[freelancer_id], back_populates="client_order_milestones")

    freelancers_proposals = relationship("User", foreign_keys=[client_id], back_populates="freelancer_proposal_milestones")
    clients_proposals = relationship("User", foreign_keys=[freelancer_id], back_populates="client_proposal_milestones")

    freelancers_requests = relationship("User", foreign_keys=[client_id], back_populates="freelancer_request_milestones")
    clients_requests = relationship("User", foreign_keys=[freelancer_id], back_populates="client_request_milestones")

    freelancers_services = relationship("User", foreign_keys=[client_id], back_populates="freelancer_service_milestones")
    clients_services = relationship("User", foreign_keys=[freelancer_id], back_populates="client_service_milestones")

    requests = relationship("Requests", secondary=request_milestone_association, back_populates="milestones")
    services = relationship("Services", secondary=service_milestone_association, back_populates="milestones")
    orders = relationship("Order", secondary=order_milestone_association, back_populates="milestones")
    proposals = relationship("Proposal", secondary=proposal_milestone_association, back_populates="milestones")
    transaction = relationship("Transaction", back_populates="milestone")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     milestone_tx_hash: str,
                     client_id: int,
                     freelancer_id: int,
                     milestone_text: str,
                     reward_amount: float,
                     milestone_status_id: int = MilestoneStatusEnum.DRAFT.value,
                     proposal_id: int = None,
                     order_id: int = None,
                     service_id: int = None,
                     request_id: int = None,
                     ):
        try:
            milestone = cls(
                milestone_tx_hash=milestone_tx_hash,
                client_id=client_id,
                freelancer_id=freelancer_id,
                milestone_text=milestone_text,
                reward_amount=reward_amount,
                milestone_status_id=milestone_status_id,
            )
            db.add(milestone)
            await db.flush() ## USE FLUSH TO REFRESH MILESTONE WITH THE MILESTONE_ID PROPERTY BUT WITHOUT NEEDING TO COMMIT FIRST
            if proposal_id:
                await db.execute(proposal_milestone_association.insert().values(proposal_id=proposal_id, milestone_id=milestone.milestone_id))
            if order_id:
                await db.execute(order_milestone_association.insert().values(order_id=order_id, milestone_id=milestone.milestone_id))
            if service_id:
                await db.execute(service_milestone_association.insert().values(service_id=service_id, milestone_id=milestone.milestone_id))
            if request_id:
                await db.execute(request_milestone_association.insert().values(request_id=request_id, milestone_id=milestone.milestone_id))
            await db.commit()
            await db.refresh(milestone)
            return milestone

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(cls, db: AsyncSession, milestone_id: int, data: dict):
        try:
            # Fetch the milestone by ID
            query = await db.execute(select(cls).where(cls.milestone_id == milestone_id))
            milestone = query.scalars().first()

            if not milestone:
                raise HTTPException(status_code=404, detail="Milestone not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(milestone, key) and value is not None:
                    setattr(milestone, key, value)

            await db.commit()
            await db.refresh(milestone)
            return milestone

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class MilestoneStatus(Base):
    __tablename__ = "milestone_status"
    milestone_status_id = Column(Integer, primary_key=True, autoincrement=True)
    milestone_status_name = Column(String(50), nullable=False)
    milestone_status_description = Column(Text, nullable=False)

    milestones = relationship("Milestones", back_populates="milestone_status")

    @classmethod
    async def seed_status(cls, db: AsyncSession) -> bool:
        default_status = [
            {"milestone_status_id": MilestoneStatusEnum.DRAFT.value, "milestone_status_name": MilestoneStatusEnum.DRAFT.name, "milestone_status_description": f"Milestone of status DRAFT is a milestone that is still not finished and changes are still pending"},
            {"milestone_status_id": MilestoneStatusEnum.IN_PROGRESS.value, "milestone_status_name": MilestoneStatusEnum.IN_PROGRESS.name, "milestone_status_description": f"Milestone of status IN PROGRESS is a milestone that changes have been submitted and is being actively worked on"},
            {"milestone_status_id": MilestoneStatusEnum.COMPLETED.value, "milestone_status_name": MilestoneStatusEnum.COMPLETED.name, "milestone_status_description": f"Milestone of status COMPLETED is a milestone that has been completed"},
        ]
        try:

            existing_status = await db.execute(
                select(cls.milestone_status_id).where(cls.milestone_status_id.in_([m["milestone_status_id"] for m in default_status]))
            )
            existing_milestone_status_ids = {m[0] for m in existing_status.fetchall()}

            new_statuses = [m for m in default_status if m["milestone_status_id"] not in existing_milestone_status_ids]

            if new_statuses:
                stmt = insert(cls).values(new_statuses)
                await db.execute(stmt)
                await db.commit()

            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))



class Proposal(Base):
    __tablename__ = "proposals"

    proposal_id = Column(Integer, primary_key=True, autoincrement=True)
    request_id = Column(Integer, ForeignKey("requests.request_id", ondelete="CASCADE"), nullable=False)
    freelancer_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    proposal_status_id = Column(Integer, ForeignKey("proposal_status.proposal_status_id", ondelete="CASCADE"), default=ProposalStatusEnum.DRAFT.value, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    deleted = Column(Boolean, nullable=False, default=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))

    # Relationships
    status = relationship("ProposalStatus", back_populates="proposals")
    request = relationship("Requests", back_populates="proposals")
    freelancer = relationship("User", back_populates="proposals")
    milestones = relationship("Milestones", secondary=proposal_milestone_association, back_populates="proposals", cascade="all")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     request_id: int,
                     freelancer_id: int,
                     ):
        try:
            proposal = cls(
                request_id=request_id,
                freelancer_id=freelancer_id,
            )
            db.add(proposal)
            await db.commit()
            await db.refresh(proposal)
            return proposal

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(cls, db: AsyncSession, proposal_id: int, data: dict):
        try:
            # Fetch the proposal by ID
            query = await db.execute(select(cls).where(cls.proposal_id == proposal_id))
            proposal = query.scalars().first()

            if not proposal:
                raise HTTPException(status_code=404, detail="Proposal not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(proposal, key) and value is not None:
                    setattr(proposal, key, value)

            await db.commit()
            await db.refresh(proposal)
            return proposal

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")


        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class ProposalStatus(Base):
    __tablename__ = "proposal_status"
    proposal_status_id = Column(Integer, primary_key=True, autoincrement=True)
    proposal_status_name = Column(String(50), nullable=False)
    proposal_status_description = Column(Text, nullable=False)

    proposals = relationship("Proposal", back_populates="status")

    @classmethod
    async def seed_status(cls, db: AsyncSession) -> bool:
        default_status = [
            {"proposal_status_id": ProposalStatusEnum.CANCELED.value, "proposal_status_name": ProposalStatusEnum.CANCELED.name, "proposal_status_description": f""},
            {"proposal_status_id": ProposalStatusEnum.DRAFT.value, "proposal_status_name": ProposalStatusEnum.DRAFT.name, "proposal_status_description": f""},
            {"proposal_status_id": ProposalStatusEnum.PENDING.value, "proposal_status_name": ProposalStatusEnum.PENDING.name, "proposal_status_description": f""},
            {"proposal_status_id": ProposalStatusEnum.ACCEPTED.value, "proposal_status_name": ProposalStatusEnum.ACCEPTED.name, "proposal_status_description": f""},
            {"proposal_status_id": ProposalStatusEnum.IN_PROGRESS.value, "proposal_status_name": ProposalStatusEnum.IN_PROGRESS.name, "proposal_status_description": f""},
            {"proposal_status_id": ProposalStatusEnum.COMPLETED.value, "proposal_status_name": ProposalStatusEnum.COMPLETED.name, "proposal_status_description": f""},
            {"proposal_status_id": ProposalStatusEnum.DENIED_BY_CLIENT.value, "proposal_status_name": ProposalStatusEnum.DENIED_BY_CLIENT.name, "proposal_status_description": f""},
        ]
        try:

            existing_status = await db.execute(
                select(cls.proposal_status_id).where(cls.proposal_status_id.in_([m["proposal_status_id"] for m in default_status]))
            )
            existing_proposal_status_ids = {m[0] for m in existing_status.fetchall()}

            new_statuses = [m for m in default_status if m["proposal_status_id"] not in existing_proposal_status_ids]

            if new_statuses:
                stmt = insert(cls).values(new_statuses)
                await db.execute(stmt)
                await db.commit()

            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    service_id = Column(Integer, ForeignKey("services.service_id", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    deleted = Column(Boolean, nullable=False, default=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    order_status_id = Column(Integer, ForeignKey("order_status.order_status_id", ondelete="CASCADE"), default=OrderStatusEnum.DRAFT.value, nullable=False)

    # Relationships
    status = relationship("OrderStatus", back_populates="orders")
    service = relationship("Services", back_populates="orders")
    milestones = relationship("Milestones", secondary=order_milestone_association, back_populates="orders", cascade="all")
    client = relationship("User", back_populates="orders")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     service_id: int,
                     client_id: int,
                     ):
        try:
            order = cls(
                service_id=service_id,
                client_id=client_id,
            )
            db.add(order)
            await db.commit()
            await db.refresh(order)
            return order

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(cls, db: AsyncSession, order_id: int, data: dict):
        try:
            # Fetch the order by ID
            query = await db.execute(select(cls).where(cls.order_id == order_id))
            order = query.scalars().first()

            if not order:
                raise HTTPException(status_code=404, detail="Order not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(order, key) and value is not None:
                    setattr(order, key, value)

            # Commit the changes and refresh
            await db.commit()
            await db.refresh(order)
            return order

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class OrderStatus(Base):
    __tablename__ = "order_status"
    order_status_id = Column(Integer, primary_key=True, autoincrement=True)
    order_status_name = Column(String(50), nullable=False)
    order_status_description = Column(Text, nullable=False)

    orders = relationship("Order", back_populates="status")

    @classmethod
    async def seed_status(cls, db: AsyncSession) -> bool:
        default_status = [
            {"order_status_id": OrderStatusEnum.CANCELED.value, "order_status_name": OrderStatusEnum.CANCELED.name, "order_status_description": f""},
            {"order_status_id": OrderStatusEnum.DRAFT.value, "order_status_name": OrderStatusEnum.DRAFT.name, "order_status_description": f""},
            {"order_status_id": OrderStatusEnum.PENDING.value, "order_status_name": OrderStatusEnum.PENDING.name, "order_status_description": f""},
            {"order_status_id": OrderStatusEnum.IN_PROGRESS.value, "order_status_name": OrderStatusEnum.IN_PROGRESS.name, "order_status_description": f""},
            {"order_status_id": OrderStatusEnum.COMPLETED.value, "order_status_name": OrderStatusEnum.COMPLETED.name, "order_status_description": f""},
            {"order_status_id": OrderStatusEnum.DENIED_BY_FREELANCER.value, "order_status_name": OrderStatusEnum.DENIED_BY_FREELANCER.name, "order_status_description": f""},
        ]
        try:

            existing_status = await db.execute(
                select(cls.order_status_id).where(cls.order_status_id.in_([m["order_status_id"] for m in default_status]))
            )
            existing_order_status_ids = {m[0] for m in existing_status.fetchall()}

            new_statuses = [m for m in default_status if m["order_status_id"] not in existing_order_status_ids]

            if new_statuses:
                stmt = insert(cls).values(new_statuses)
                await db.execute(stmt)
                await db.commit()

            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    milestone_id = Column(Integer, ForeignKey("milestones.milestone_id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    token_name = Column(String(50), nullable=False) ## TODO Maybe in the future this will need to be a table with all valid tokens.
    deleted = Column(Boolean, nullable=False, default=False)
    receiver_address = Column(Text, nullable=False)
    client_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=False)
    freelancer_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))

    # Relationships
    milestone = relationship("Milestones", back_populates="transaction", uselist=False)
    client = relationship("User", foreign_keys=[client_id], back_populates="client_transactions")
    freelancer = relationship("User", foreign_keys=[freelancer_id], back_populates="freelancer_transactions")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     milestone_id: int,
                     amount: float,
                     client_id: int,
                     freelancer_id: int,
                     token_name: str = None,
                     receiver_address: str = None):
        try:
            transaction = cls(
                milestone_id=milestone_id,
                amount=amount,
                client_id=client_id,
                freelancer_id=freelancer_id,
                token_name=token_name,
                receiver_address=receiver_address
            )
            db.add(transaction)
            await db.commit()
            await db.refresh(transaction)
            return transaction

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(cls, db: AsyncSession, transaction_id: int, data: dict):
        try:
            # Fetch the transaction by ID
            query = await db.execute(select(cls).where(cls.transaction_id == transaction_id))
            transaction = query.scalars().first()

            if not transaction:
                raise HTTPException(status_code=404, detail="Transaction not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(transaction, key) and value is not None:
                    setattr(transaction, key, value)

            # Commit the changes and refresh
            await db.commit()
            await db.refresh(transaction)
            return transaction

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(50), nullable=True, unique=True)
    category_description = Column(Text, nullable=True)
    deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))

    sub_categories = relationship("SubCategory", back_populates="category", cascade="all, delete-orphan")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     category_name: str,
                     category_description: str = None):
        try:
            category = cls(
                category_name=category_name,
                category_description=category_description
            )
            db.add(category)
            await db.commit()
            await db.refresh(category)
            return category

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(cls, db: AsyncSession, category_id: int, data: dict):
        try:
            # Fetch the category by ID
            query = await db.execute(select(cls).where(cls.category_id == category_id))
            category = query.scalars().first()

            if not category:
                raise HTTPException(status_code=404, detail="Category not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(category, key) and value is not None:
                    setattr(category, key, value)

            # Commit the changes and refresh
            await db.commit()
            await db.refresh(category)
            return category

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def seed_categories(cls, db: AsyncSession) -> bool:
        default_categories = [
            {"category_name": "Software Development", "category_description": "This is the description"},
            {"category_name": "Web Design", "category_description": "This is the description"},
            {"category_name": "Finance", "category_description": "This is the description"},
            {"category_name": "Crypto", "category_description": "This is the description"},
            {"category_name": "Language learning", "category_description": "This is the description"}
        ]
        try:

            existing_categories = await db.execute(
                select(cls.category_name).where(
                    cls.category_name.in_([m["category_name"] for m in default_categories]))
            )
            existing_category_names = {m[0] for m in existing_categories.fetchall()}

            new_categories = [m for m in default_categories if m["category_name"] not in existing_category_names]

            if new_categories:
                stmt = insert(cls).values(new_categories)
                await db.execute(stmt)
                await db.commit()

            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class SubCategory(Base):
    __tablename__ = "sub_categories"

    sub_category_id = Column(Integer, primary_key=True, autoincrement=True)
    sub_category_name = Column(String(50), nullable=False, unique=True)
    sub_category_description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    deleted = Column(Boolean, nullable=False, default=False)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))

    category = relationship("Category", back_populates="sub_categories")
    services = relationship("Services", back_populates="sub_category", cascade="all, delete-orphan")
    requests = relationship("Requests", back_populates="sub_category", cascade="all, delete-orphan")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     sub_category_name: str,
                     category_id: int,
                     sub_category_description: str = None):
        try:
            sub_category = cls(
                sub_category_name=sub_category_name,
                sub_category_description=sub_category_description,
                category_id=category_id
            )
            db.add(sub_category)
            await db.commit()
            await db.refresh(sub_category)
            return sub_category


        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(cls, db: AsyncSession, sub_category_id: int, data: dict):
        try:
            # Fetch the subcategory by ID
            query = await db.execute(select(cls).where(cls.sub_category_id == sub_category_id))
            sub_category = query.scalars().first()

            if not sub_category:
                raise HTTPException(status_code=404, detail="SubCategory not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(sub_category, key) and value is not None:
                    setattr(sub_category, key, value)

            # Commit changes and refresh
            await db.commit()
            await db.refresh(sub_category)
            return sub_category

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def seed_sub_categories(cls, db: AsyncSession) -> bool:
        default_sub_categories = [
            {"category_id": 1, "sub_category_name": "Software Development sub_category", "sub_category_description": "This is the description"},
            {"category_id": 2, "sub_category_name": "Web Design sub_category", "sub_category_description": "This is the description"},
            {"category_id": 3, "sub_category_name": "Finance sub_category", "sub_category_description": "This is the description"},
            {"category_id": 4, "sub_category_name": "Crypto sub_category", "sub_category_description": "This is the description"},
            {"category_id": 5, "sub_category_name": "Language learning sub_category", "sub_category_description": "This is the description"}
        ]
        try:

            existing_categories = await db.execute(
                select(cls.sub_category_name).where(
                    cls.sub_category_name.in_([m["sub_category_name"] for m in default_sub_categories]))
            )
            existing_sub_category_names = {m[0] for m in existing_categories.fetchall()}

            new_sub_categories = [m for m in default_sub_categories if m["sub_category_name"] not in existing_sub_category_names]

            if new_sub_categories:
                stmt = insert(cls).values(new_sub_categories)
                await db.execute(stmt)
                await db.commit()

            return True

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    reviewee_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)  # Person being reviewed
    reviewer_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)  # Person giving the review
    rating = Column(DECIMAL(2, 1), nullable=False)  # Rating between 1.0 and 5.0
    comment = Column(Text, nullable=True)
    deleted = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))

    # Relationships
    reviewee = relationship("User", foreign_keys=[reviewee_id], back_populates="received_reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="given_reviews")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     reviewee_id: int,
                     reviewer_id: int,
                     rating: float,
                     comment: str = None
         ):
        if rating < 1.0 or rating > 5.0:
            raise HTTPException(status_code=400, detail="Rating must be between 1.0 and 5.0")

        try:
            review = cls(
                reviewee_id=reviewee_id,
                reviewer_id=reviewer_id,
                rating=rating,
                comment=comment
            )
            db.add(review)
            await db.commit()
            await db.refresh(review)
            return review
        
        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(cls, db: AsyncSession, review_id: int, data: dict):
        try:
            # Fetch the review by ID
            query = await db.execute(select(cls).where(cls.review_id == review_id))
            review = query.scalars().first()

            if not review:
                raise HTTPException(status_code=404, detail="Review not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(review, key) and value is not None:
                    setattr(review, key, value)

            # Commit changes and refresh
            await db.commit()
            await db.refresh(review)
            return review

        except IntegrityError as e:
            await db.rollback()
            print(f"IntegrityError: {e}")
            raise HTTPException(status_code=500, detail="Database integrity error.")

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
