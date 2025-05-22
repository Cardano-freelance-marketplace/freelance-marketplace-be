import base64
import hashlib
import secrets
import string
from datetime import datetime, timedelta
from hashlib import sha256
import jwt
from fastapi import Response, HTTPException
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from freelance_marketplace.api.routes.users.users_logic import UsersLogic
from freelance_marketplace.api.services.redis import Redis
from freelance_marketplace.core.config import settings
from freelance_marketplace.db.sql.database import AsyncSessionLocal
from freelance_marketplace.models.requests.loginRequest import LoginRequest
from freelance_marketplace.models.sql.request_model.UserRequest import UserRequest
from freelance_marketplace.models.sql.sql_tables import WalletTypes


class Authentication:

    def __init__(self):
        pass

    @classmethod
    async def logout(
            cls,
            response: Response,
            request: Request,
    ):
        token = request.cookies.get("access_token")
        if token:
            session_id = hashlib.sha256(token.encode()).hexdigest()
            await Redis.invalidate_cache(f"sessions:{session_id}")
        response.delete_cookie("access_token")
        return True

    @classmethod
    async def verify_nonce(
            cls,
            login_request: LoginRequest
    ):
        stored_nonce = await Redis.get_redis_data(match=f"nonce:{login_request.wallet_address}")
        if login_request.nonce != stored_nonce:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect nonce",
            )

    @classmethod
    async def verify_signature(
            cls,
            login_request: LoginRequest,
    ):
        try:
            # Convert the public key
            public_key_bytes = bytes.fromhex(login_request.public_key)
            verify_key = VerifyKey(public_key_bytes)

            # Decode signature from base64
            signature_bytes = base64.b64decode(login_request.signature)

            # verify signature
            verify_key.verify(login_request.signed_nonce.encode(), signature_bytes)
            return True
        except BadSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect signature"
            )
        except Exception as e:
            raise e

    @classmethod
    async def create_access_token(
            cls,
            login_request: LoginRequest,
            response: Response
    ):
        payload = {
            "sub": login_request.wallet_address,
            "exp": datetime.utcnow() + timedelta(hours=1),
        }
        jwt_token = jwt.encode(
            payload,
            settings.fastapi.secret_key,
            algorithm=settings.fastapi.jwt_algorithm
        )
        session_id = (
            hashlib.sha256(
            jwt_token.encode())
                      .hexdigest()
        )
        await Redis.set_redis_data(cache_key=f"sessions:{session_id}", data=jwt_token, ex=3600)
        response.set_cookie(
            key="access_token",
            value=jwt_token,
            httponly=True,
            secure=True,
            samesite="Lax"
        )
        return response

    @classmethod
    async def __hash_payload(
            cls,
            payload: dict
    ):
        # Convert the payload into a string and hash it to get a unique session ID
        payload_str = str(payload)  # You can serialize the payload to string here
        return sha256(payload_str.encode('utf-8')).hexdigest()

    @classmethod
    async def generate_nonce(
            cls,
            length=32
    ):
        return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

    @classmethod
    async def user_conditional_register(
            cls,
            db: AsyncSession,
            login_request: LoginRequest,
    ):
        user = await UsersLogic.get_user_by_wallet_address(wallet_public_address=login_request.wallet_address, db=db)
        if not user:
            await cls.__create_user(
                login_request=login_request
            )

    @classmethod
    async def __create_user(
            cls,
            login_request: LoginRequest
    ):
        async with AsyncSessionLocal() as session:
            result = session.execute(
                select(WalletTypes)
                .where(
                    WalletTypes.wallet_type_name.lower() == login_request.wallet_type_name.lower()
                )
            )
            wallet_type = result.scalar().first()
            user_request = UserRequest(
                wallet_type_id=wallet_type.wallet_type_id,
                wallet_public_address=login_request.wallet_address
            )
            await UsersLogic.create(db=session, user=user_request)