import uuid
from datetime import datetime, timezone
from sqlalchemy import DateTime, Boolean, ForeignKey, VARCHAR, Enum, Table, delete, insert, TIMESTAMP, Float, ARRAY, \
    DECIMAL, select, CheckConstraint
from freelance_marketplace.db.sql.database import Base
from freelance_marketplace.models.enums.jobStatus import JobStatus
from freelance_marketplace.models.enums.jobType import JobType
from freelance_marketplace.models.enums.milestoneStatus import MilestoneStatus
from freelance_marketplace.models.enums.milestoneType import MilestoneType
from freelance_marketplace.models.enums.userRole import UserRole
from freelance_marketplace.models.enums.userType import UserType as UserTypeEnum
from freelance_marketplace.models.enums.walletType import WalletType
from typing import List
from sqlalchemy import Column, Integer, String, Text
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
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    is_active = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=False, default=False)
    wallet_public_address = Column(VARCHAR(100), unique=True, nullable=False)
    wallet_type = Column(Enum(WalletType), nullable=False)
    last_login = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.now(timezone.utc))
    role_id = Column(Integer, ForeignKey("roles.role_id", ondelete="SET NULL"), default=UserRole.User.value)
    type_id = Column(Integer, ForeignKey("user_types.type_id", ondelete="SET NULL"), default=UserTypeEnum.Freelancer_Client.value)

    client_jobs = relationship("Jobs", foreign_keys="[Jobs.client_id]", back_populates="client")
    freelancer_jobs = relationship("Jobs", foreign_keys="[Jobs.freelancer_id]", back_populates="freelancer")
    client_milestones = relationship("Milestones", foreign_keys="[Milestones.client_id]", back_populates="client")
    freelancer_milestones = relationship("Milestones", foreign_keys="[Milestones.freelancer_id]", back_populates="freelancer")
    client_transactions = relationship("Transaction", foreign_keys="[Transaction.client_id]", back_populates="client")
    freelancer_transactions = relationship("Transaction", foreign_keys="[Transaction.freelancer_id]", back_populates="freelancer")
    role = relationship("Role", back_populates="users")
    type = relationship("UserType", back_populates="users")
    profile = relationship("Profiles", back_populates="user", cascade="all, delete-orphan", uselist=False)
    proposals = relationship("Proposal", back_populates="freelancer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="client")

    received_reviews = relationship("Review", foreign_keys="[Review.reviewee_id]", back_populates="reviewee")
    given_reviews = relationship("Review", foreign_keys="[Review.reviewer_id]", back_populates="reviewer")


    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     wallet_public_address: str,
                     wallet_type: WalletType,
                     user_type: UserTypeEnum,

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

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
    @classmethod
    async def seed_users(cls, db: AsyncSession) -> bool:
        default_users = [
            {"wallet_public_address": "testewalletaddress123", "wallet_type": 'Lace', "type_id": UserTypeEnum.Freelancer_Client.value},
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
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class UserType(Base):
    __tablename__ = "user_types"

    type_id = Column(Integer, primary_key=True, autoincrement=True)
    type_name = Column(String(50), nullable=False, unique=True)
    type_description = Column(Text, nullable=True)
    users = relationship("User", back_populates="type")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     type_name: str,
                     type_description: str,
                     type_id: int = None
    ):
        try:
            type = cls(
                type_id=type_id,
                type_name=type_name,
                type_description=type_description,
            )
            db.add(type)
            await db.commit()
            await db.refresh(type)
            return type

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(cls, db: AsyncSession, type_id: int, data: dict):
        try:
            # Fetch the type by ID
            query = await db.execute(select(cls).where(cls.type_id == type_id))
            type = query.scalars().first()

            if not type:
                raise HTTPException(status_code=404, detail="Role not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(type, key) and value is not None:
                    setattr(type, key, value)

            await db.commit()
            await db.refresh(type)
            return type

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def seed_types(cls, db: AsyncSession) -> bool:
        default_types = [
            {"type_id": UserTypeEnum.Freelancer_Client.value, "type_name": UserTypeEnum.Freelancer_Client.name, "type_description": f"{UserTypeEnum.Freelancer_Client.name} type"},
            {"type_id": UserTypeEnum.Client.value, "type_name": UserTypeEnum.Client.name, "type_description": f"{UserTypeEnum.Client.name} type"},
            {"type_id": UserTypeEnum.Freelancer.value, "type_name": UserTypeEnum.Freelancer.name, "type_description": f"{UserTypeEnum.Freelancer.name} type"},
            {"type_id": UserTypeEnum.Unknown.value, "type_name": UserTypeEnum.Unknown.name, "type_description": f"{UserTypeEnum.Unknown.name} type"},
        ]
        try:

            existing_types = await db.execute(
                select(cls.type_id).where(cls.type_id.in_([m["type_id"] for m in default_types]))
            )
            existing_type_ids = {m[0] for m in existing_types.fetchall()}

            new_types = [m for m in default_types if m["type_id"] not in existing_type_ids]

            if new_types:
                stmt = insert(cls).values(new_types)
                await db.execute(stmt)
                await db.commit()

            return True
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

    @classmethod
    async def edit(cls, db: AsyncSession, profile_id: int, data: dict):
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

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


class Jobs(Base):
    __tablename__ = "jobs"

    job_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    sub_category_id = Column(Integer, ForeignKey("sub_categories.sub_category_id", ondelete='SET NULL'), nullable=False)
    total_price = Column(Float, nullable=True)
    tags = Column(ARRAY(String), nullable=False)
    client_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=False)
    freelancer_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    type = Column(Enum(JobType), nullable=False)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.Pending_Approval.value)

    # Relationships
    client = relationship("User", foreign_keys=[client_id], back_populates="client_jobs")
    freelancer = relationship("User", foreign_keys=[freelancer_id], back_populates="freelancer_jobs")
    sub_category = relationship("SubCategory", back_populates="jobs")
    milestones = relationship("Milestones", back_populates="job", cascade="all, delete-orphan")
    proposals = relationship("Proposal", back_populates="job", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="job", cascade="all, delete-orphan")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     title: str,
                     description: str,
                     sub_category_id: int,
                     total_price: float,
                     tags: list,
                     client_id: int,
                     freelancer_id: int,
                     job_type: JobType
     ):
        try:
            job = cls(
                title=title,
                description=description,
                sub_category_id=sub_category_id,
                total_price=total_price,
                tags=tags,
                client_id=client_id,
                freelancer_id=freelancer_id,
                type=job_type
            )
            db.add(job)
            await db.commit()
            await db.refresh(job)
            return job

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @classmethod
    async def edit(cls, db: AsyncSession, job_id: int, data: dict):
        try:
            # Fetch the job by ID
            query = await db.execute(select(cls).where(cls.job_id == job_id))
            job = query.scalars().first()

            if not job:
                raise HTTPException(status_code=404, detail="Job not found")

            # Update fields dynamically
            for key, value in data.items():
                if hasattr(job, key) and value is not None:
                    setattr(job, key, value)

            await db.commit()
            await db.refresh(job)
            return job

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class Milestones(Base):
    __tablename__ = "milestones"

    milestone_id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False)
    milestone_tx_hash = Column(String(4096), nullable=False)
    client_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=False)
    freelancer_id = Column(Integer, ForeignKey("users.user_id", ondelete="SET NULL"), nullable=False)
    milestone_text = Column(Text, nullable=False)
    reward_amount = Column(Float, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.now(timezone.utc))
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))
    client_approved = Column(Boolean, nullable=False, default=False)
    freelancer_approved = Column(Boolean, nullable=False, default=False)
    status = Column(Enum(MilestoneStatus), nullable=False, default=MilestoneStatus.Draft.value)
    type = Column(Enum(MilestoneType), nullable=False, default=MilestoneType.Request_Milestone.value)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=True, unique=True)
    proposal_id = Column(Integer, ForeignKey("proposals.proposal_id", ondelete="CASCADE"), nullable=True, unique=True)

    __table_args__ = (
        CheckConstraint(
            "(order_id IS NOT NULL AND proposal_id IS NULL) OR (order_id IS NULL AND proposal_id IS NOT NULL)",
            name="check_milestone_has_one_parent"
        ),
    )
    # Relationships
    job = relationship("Jobs", back_populates="milestones")
    client = relationship("User", foreign_keys=[client_id], back_populates="client_milestones")
    freelancer = relationship("User", foreign_keys=[freelancer_id], back_populates="freelancer_milestones")
    order = relationship("Order", back_populates="milestones")
    proposal = relationship("Proposal", back_populates="milestones")
    transaction = relationship("Transaction", back_populates="milestone")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     job_id: int,
                     milestone_tx_hash: str,
                     client_id: int,
                     freelancer_id: int,
                     milestone_text: str,
                     reward_amount: float,
                     milestone_status: MilestoneStatus = MilestoneStatus.Draft,
                     milestone_type: MilestoneType = MilestoneType.Request_Milestone
                     ):
        try:
            milestone = cls(
                job_id=job_id,
                milestone_tx_hash=milestone_tx_hash,
                client_id=client_id,
                freelancer_id=freelancer_id,
                milestone_text=milestone_text,
                reward_amount=reward_amount,
                status=milestone_status,
                type=milestone_type
            )
            db.add(milestone)
            await db.commit()
            await db.refresh(milestone)
            return milestone

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

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


class Proposal(Base):
    __tablename__ = "proposals"

    proposal_id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False)
    freelancer_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)

    # Relationships
    job = relationship("Jobs", back_populates="proposals")
    freelancer = relationship("User", back_populates="proposals")
    milestones = relationship("Milestones", back_populates="proposal", cascade="all, delete-orphan")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     job_id: int,
                     freelancer_id: int,
                     milestone_id: int = None
                     ):
        try:
            proposal = cls(
                job_id=job_id,
                freelancer_id=freelancer_id,
                milestone_id=milestone_id
            )
            db.add(proposal)
            await db.commit()
            await db.refresh(proposal)
            return proposal

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

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class OrderMilestones(Base):
    __tablename__ = "order_milestones"

    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), primary_key=True)
    milestone_id = Column(Integer, ForeignKey("milestones.milestone_id", ondelete="CASCADE"), primary_key=True)


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey("jobs.job_id", ondelete="CASCADE"), nullable=False)
    client_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), nullable=True, onupdate=datetime.now(timezone.utc))

    # Relationships
    job = relationship("Jobs", back_populates="orders")
    milestones = relationship("Milestones", back_populates="order", cascade="all, delete-orphan")
    client = relationship("User", back_populates="orders")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     job_id: int,
                     client_id: int,
                     milestone_id: int = None
                     ):
        try:
            order = cls(
                job_id=job_id,
                client_id=client_id,
                milestone_id=milestone_id
            )
            db.add(order)
            await db.commit()
            await db.refresh(order)
            return order

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

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    milestone_id = Column(Integer, ForeignKey("milestones.milestone_id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    token_name = Column(String(50), nullable=True)
    receiver_address = Column(Text, nullable=True)
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

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    category_name = Column(String(50), nullable=True)
    category_description = Column(Text, nullable=True)

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

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class SubCategory(Base):
    __tablename__ = "sub_categories"

    sub_category_id = Column(Integer, primary_key=True, autoincrement=True)
    sub_category_name = Column(String(50), nullable=True)
    sub_category_description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="CASCADE"), nullable=False)

    category = relationship("Category", back_populates="sub_categories")
    jobs = relationship("Jobs", back_populates="sub_category", cascade="all, delete-orphan")

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
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    # Relationships
    reviewee = relationship("User", foreign_keys=[reviewee_id], back_populates="received_reviews")
    reviewer = relationship("User", foreign_keys=[reviewer_id], back_populates="given_reviews")

    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     reviewee_id: int,
                     reviewer_id: int,
                     rating: float,
                     comment: str = None):
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

        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
