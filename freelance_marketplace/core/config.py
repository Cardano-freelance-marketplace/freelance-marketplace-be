from dotenv import load_dotenv
from pydantic_settings import BaseSettings
load_dotenv()

class Services(BaseSettings):
    frontend_url: str = ""
    authorization_url: str = ""
    backend_url: str = ""

    class Config:
        env_file = ".env"
        env_prefix = "SERVICES_"
        extra = "ignore"

class Mongo(BaseSettings):
    connection_string: str = ""
    database_name: str = ""

    class Config:
        env_prefix = "MONGO_"
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields

class Redis(BaseSettings):
    port: str = "6379"
    host: str = "localhost"
    decode_responses: bool = True

    class Config:
        env_prefix = "REDIS_"
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields

class SQL(BaseSettings):
    connection_string: str = ""

    class Config:
        env_prefix = "SQL_"
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields

class AWS(BaseSettings):
    access_key_id: str = ""
    secret_access_key: str = ""
    region_name: str = "us-east-1"
    endpoint_url: str = "http://localhost:4566"
    bucket_name: str = "freelance-marketplace"

    class Config:
        env_prefix = "AWS_"
        env_file = ".env"
        extra = "ignore"

class FastAPISettings(BaseSettings):
    debug: bool = True
    title: str = "Freelancing Marketplace"
    version: str = "0.1.0"
    description: str = ""
    secret_key: str = "test"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_prefix = "FASTAPI_"
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields

class CardanoSubmitAPI(BaseSettings):
    url: str = ""

    class Config:
        env_prefix = "SUBMIT_API_"
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields

class Ogmios(BaseSettings):
    url: str = ""

    class Config:
        env_prefix = "OGMIOS_"
        env_file = ".env"
        extra = "ignore"

class CardanoNode(BaseSettings):
    socket_path: str = ""
    class Config:
        env_prefix = "CARDANO_NODE_"

class WalletKeys(BaseSettings):
    skey_encrypted: str = ""
    vkey: str = ""

    class Config:
        env_prefix = "KEY_"
        env_file = ".env"
        extra = "ignore"

class Settings(BaseSettings):
    fastapi: FastAPISettings = FastAPISettings()
    mongo: Mongo = Mongo()
    sql: SQL = SQL()
    aws: AWS = AWS()
    redis: Redis = Redis()
    cardano_submit_api: CardanoSubmitAPI = CardanoSubmitAPI()
    services: Services = Services()
    cardano_node: CardanoNode = CardanoNode()
    ogmios: Ogmios = Ogmios()
    wallet_keys: WalletKeys = WalletKeys()


    class Config:
        env_nested_delimiter = "__"
        env_file = ".env"
        extra = "ignore"


settings = Settings()

if __name__ == "__main__":
    print(settings)
