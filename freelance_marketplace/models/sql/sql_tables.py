from datetime import datetime, timezone
from sqlalchemy import Boolean, ForeignKey, VARCHAR, Table, insert, TIMESTAMP, Float, ARRAY, \
    DECIMAL, select, CheckConstraint
from freelance_marketplace.db.sql.database import Base
from freelance_marketplace.models.enums.jobStatus import JobStatus as JobStatusEnum
from freelance_marketplace.models.enums.jobType import JobType
from freelance_marketplace.models.enums.milestoneType import MilestoneType
from freelance_marketplace.models.enums.milestoneStatus import MilestoneStatus as MilestoneStatusEnum
from freelance_marketplace.models.enums.userRole import UserRole
from freelance_marketplace.models.enums.userType import UserType as UserTypeEnum
from freelance_marketplace.models.enums.walletType import WalletType as WalletTypeEnum
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
    wallet_type_id = Column(Integer, ForeignKey("wallet_types.wallet_type_id", ondelete="SET NULL"), default=WalletTypeEnum.Lace.value)
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
    wallet_type = relationship("WalletTypes", back_populates="users")
    received_reviews = relationship("Review", foreign_keys="[Review.reviewee_id]", back_populates="reviewee")
    given_reviews = relationship("Review", foreign_keys="[Review.reviewer_id]", back_populates="reviewer")


    @classmethod
    async def create(cls,
                     db: AsyncSession,
                     wallet_public_address: str,
                     wallet_type_id: int = WalletTypeEnum.Lace.value,
                     type_id: int = UserTypeEnum.Freelancer_Client.value,

    ):
        try:
            user = cls(
                wallet_public_address=wallet_public_address,
                wallet_type_id=wallet_type_id,
                type_id=type_id,
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
            {"wallet_public_address": "testewalletaddress123", "wallet_type_id": 1, "type_id": UserTypeEnum.Freelancer_Client.value},
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

class WalletTypes(Base):
    __tablename__ = "wallet_types"

    wallet_type_id = Column(Integer, primary_key=True, autoincrement=True)
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
    profile_picture = Column(VARCHAR(1000), nullable=True)

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
    job_type_id = Column(Integer, ForeignKey("job_types.job_type_id", ondelete="SET NULL"), nullable=True)
    job_status_id = Column(Integer, ForeignKey("job_status.job_status_id", ondelete="SET NULL"), nullable=True)

    # Relationships
    job_type = relationship("JobTypes", back_populates="jobs")
    job_status = relationship("JobStatus", back_populates="jobs")
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
                     job_type: int
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

class JobStatus(Base):
    __tablename__ = "job_status"
    job_status_id = Column(Integer, primary_key=True, autoincrement=True)
    job_status_name = Column(String(50), nullable=False)
    job_status_description = Column(Text, nullable=False)

    jobs = relationship("Jobs", back_populates="job_status")

    @classmethod
    async def seed_status(cls, db: AsyncSession) -> bool:
        default_status = [
            {"job_status_id": JobStatusEnum.PENDING_APPROVAL.value, "job_status_name": JobStatusEnum.PENDING_APPROVAL.name, "job_status_description": f"When a job of type request or service is created, needs to be approved by platform, to see if it follows ToS"},
            {"job_status_id": JobStatusEnum.APPROVED.value, "job_status_name": JobStatusEnum.APPROVED.name, "job_status_description": f" Ready to be displayed on the platform"},
            {"job_status_id": JobStatusEnum.DRAFT.value, "job_status_name": JobStatusEnum.DRAFT.name, "job_status_description": f"When a job has found a freelancer/client, and is approving milestones and rewards defined by the client/freelancer."},
            {"job_status_id": JobStatusEnum.IN_PROGRESS.value, "job_status_name": JobStatusEnum.IN_PROGRESS.name, "job_status_description": f"After the job is created and the funds are allocated on the smart contract"},
            {"job_status_id": JobStatusEnum.COMPLETED.value, "job_status_name": JobStatusEnum.COMPLETED.name, "job_status_description": f"When all milestones are completed"},
            {"job_status_id": JobStatusEnum.CANCELED.value, "job_status_name": JobStatusEnum.CANCELED.name, "job_status_description": f"When Job is canceled by the client or the freelancer"},
        ]
        try:

            existing_status = await db.execute(
                select(cls.job_status_id).where(cls.job_status_id.in_([m["job_status_id"] for m in default_status]))
            )
            existing_job_status_ids = {m[0] for m in existing_status.fetchall()}

            new_statuses = [m for m in default_status if m["job_status_id"] not in existing_job_status_ids]

            if new_statuses:
                stmt = insert(cls).values(new_statuses)
                await db.execute(stmt)
                await db.commit()

            return True
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

class JobTypes(Base):
    __tablename__ = "job_types"
    job_type_id = Column(Integer, primary_key=True, autoincrement=True)
    job_type_name = Column(String(50), nullable=False)
    job_type_description = Column(Text, nullable=False)

    jobs = relationship("Jobs", back_populates="job_type")

    @classmethod
    async def seed_types(cls, db: AsyncSession) -> bool:
        default_types = [
            {"job_type_id": JobType.REQUEST.value, "job_type_name": JobType.REQUEST.name, "job_type_description": f"Job of type request is a job created by a client looking for a freelancer to complete the work"},
            {"job_type_id": JobType.SERVICE.value, "job_type_name": JobType.SERVICE.name, "job_type_description": f"Job of type service is a job created by a freelancer, so that clients can order the freelancer's work"},
        ]
        try:

            existing_types = await db.execute(
                select(cls.job_type_id).where(cls.job_type_id.in_([m["job_type_id"] for m in default_types]))
            )
            existing_job_type_ids = {m[0] for m in existing_types.fetchall()}

            new_types = [m for m in default_types if m["job_type_id"] not in existing_job_type_ids]

            if new_types:
                stmt = insert(cls).values(new_types)
                await db.execute(stmt)
                await db.commit()

            return True
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
    milestone_type_id = Column(Integer, ForeignKey("milestone_types.milestone_type_id", ondelete="SET NULL"), nullable=True)
    milestone_status_id = Column(Integer, ForeignKey("milestone_status.milestone_status_id", ondelete="SET NULL"), nullable=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=True, unique=True)
    proposal_id = Column(Integer, ForeignKey("proposals.proposal_id", ondelete="CASCADE"), nullable=True, unique=True)

    __table_args__ = (
        CheckConstraint(
            "(order_id IS NOT NULL AND proposal_id IS NULL) OR (order_id IS NULL AND proposal_id IS NOT NULL)",
            name="check_milestone_has_one_parent"
        ),
    )
    # Relationships
    milestone_type = relationship("MilestoneTypes", back_populates="milestones")
    milestone_status = relationship("MilestoneStatus", back_populates="milestones")
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
                     milestone_status_id: int = MilestoneStatusEnum.DRAFT.value,
                     milestone_type_id: int = MilestoneType.REQUEST.value
                     ):
        try:
            milestone = cls(
                job_id=job_id,
                milestone_tx_hash=milestone_tx_hash,
                client_id=client_id,
                freelancer_id=freelancer_id,
                milestone_text=milestone_text,
                reward_amount=reward_amount,
                milestone_status_id=milestone_status_id,
                milestone_type_id=milestone_type_id
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

class MilestoneTypes(Base):
    __tablename__ = "milestone_types"
    milestone_type_id = Column(Integer, primary_key=True, autoincrement=True)
    milestone_type_name = Column(String(50), nullable=False)
    milestone_type_description = Column(Text, nullable=False)

    milestones = relationship("Milestones", back_populates="milestone_type")

    @classmethod
    async def seed_types(cls, db: AsyncSession) -> bool:
        default_types = [
            {"milestone_type_id": MilestoneType.REQUEST.value, "milestone_type_name": MilestoneType.REQUEST.name, "milestone_type_description": f"Milestone of type request is a milestone created by a client looking for a freelancer to complete the work"},
            {"milestone_type_id": MilestoneType.SERVICE.value, "milestone_type_name": MilestoneType.SERVICE.name, "milestone_type_description": f"Milestone of type service is a milestone created by a freelancer, so that clients can order the freelancer's work"},
        ]
        try:

            existing_types = await db.execute(
                select(cls.milestone_type_id).where(cls.milestone_type_id.in_([m["milestone_type_id"] for m in default_types]))
            )
            existing_milestone_type_ids = {m[0] for m in existing_types.fetchall()}

            new_types = [m for m in default_types if m["milestone_type_id"] not in existing_milestone_type_ids]

            if new_types:
                stmt = insert(cls).values(new_types)
                await db.execute(stmt)
                await db.commit()

            return True
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
