from pydantic_settings import BaseSettings

class TestingSettings(BaseSettings):
    addr: str = ""

    class Config:
        env_prefix = "TEST_"
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields

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
    access_key_id: str = "test"
    secret_access_key: str = "test"
    region_name: str = "us-east-1"
    endpoint_url: str = "http://localhost:4566"

    class Config:
        env_prefix = "AWS_"
        env_file = ".env"
        extra = "ignore"

class FastAPISettings(BaseSettings):
    debug: bool = True
    title: str = "Freelancing Marketplace"
    version: str = "0.1.0"
    description: str = ""

    class Config:
        env_prefix = "FASTAPI_"
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields

class Settings(BaseSettings):
    fastapi: FastAPISettings = FastAPISettings()
    test: TestingSettings = TestingSettings()
    mongo: Mongo = Mongo()
    sql: SQL = SQL()
    aws: AWS = AWS()
    redis: Redis = Redis()

    class Config:
        env_nested_delimiter = "__"
        env_file = ".env"
        extra = "ignore"

settings = Settings()

if __name__ == "__main__":
    print(settings.test)
    print(settings.fastapi)
