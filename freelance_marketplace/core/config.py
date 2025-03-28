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

class SQL(BaseSettings):
    connection_string: str = ""

    class Config:
        env_prefix = "SQL_"
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields

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

    class Config:
        env_nested_delimiter = "__"
        env_file = ".env"
        extra = "ignore"

settings = Settings()

if __name__ == "__main__":
    print(settings.test)
    print(settings.fastapi)
