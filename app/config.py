import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres.ulicowevlqkplhwkqfvj:K7mQ9xT4vN8pL2zR6@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres",
)

SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
