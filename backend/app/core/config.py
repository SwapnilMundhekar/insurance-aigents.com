from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "InsuranceAIGents"
    app_env: str = "local"
    postgres_db: str = "insurance_aigents"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "postgres"
    postgres_port: int = 5432
    redis_host: str = "redis"
    redis_port: int = 6379
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333

    @property
    def postgres_dsn(self):
        return f"host={self.postgres_host} port={self.postgres_port} dbname={self.postgres_db} user={self.postgres_user} password={self.postgres_password}"

settings = Settings()