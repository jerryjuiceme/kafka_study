from typing import Literal
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s: %(lineno)-3d %(levelname)-7s - %(message)s"
)

BASE_DIR = Path(__file__).parent.parent


class EmailConfig(BaseModel):
    from_user: str


class GunicornConfig(BaseModel):
    port: int = 8000
    host: str = "0.0.0.0"
    workers: int
    timeout: int = 600  # 10 minutes


class AuthJWT(BaseModel):
    private_key_path: Path = BASE_DIR / "src" / "certs" / "jwt-private.pem"
    public_key_path: Path = BASE_DIR / "src" / "certs" / "jwt-public.pem"
    algorithm: str = "RS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 30


class ModeConfig(BaseModel):
    mode: Literal["TEST", "DEV", "PROD"] = "PROD"


class DatabaseConfig(BaseModel):
    db_host: str
    db_port: int
    db_user: str
    db_pass: str
    db_name: str

    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 50
    max_overflow: int = 10
    naming_convention: dict[str, str] = {
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


class ApiV1Prefix(BaseModel):
    prefix: str = "/v1"


class ApiPrefix(BaseModel):
    prefix: str = "/api"
    v1: ApiV1Prefix = ApiV1Prefix()


class LoggingConfig(BaseModel):
    log_level: Literal["DEBUG", "INFO", "ERROR", "WARNING", "CRITICAL"]
    log_format: str = LOG_DEFAULT_FORMAT
    datefmt: str = "%Y-%m-%d %H:%M:%S"


class AccessToken(BaseModel):
    lifetime_seconds: int = 3600
    reset_password_token_secret: str
    verification_token_secret: str


class StorageConfig(BaseModel):
    storage_type: Literal["local", "google_drive"] = "local"
    local_storage_csv_path: str = "src/static/csv"
    local_storage_template_path: str = "src/static/templates"
    google_drive_csv_folder_id: str
    google_drive_templ_folder_id: str
    google_drive_credentials_path: str
    template_file_path: str | Path = BASE_DIR / "src" / "static"


class BrokerConfig(BaseModel):
    kafka_bootstrap_servers: str
    send_topic: str = "send_mail"
    receive_topic: str = "receive_mail"
    send_csv_topic: str = "send_csv"
    receive_csv_topic: str = "receive_csv"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("../.env.template", "../.env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__",
        extra="allow",
    )

    logging: LoggingConfig
    authjwt: AuthJWT = AuthJWT()
    api: ApiPrefix = ApiPrefix()
    gunicorn: GunicornConfig
    modeconf: ModeConfig
    access_token: AccessToken
    db: DatabaseConfig
    storage: StorageConfig
    email: EmailConfig
    broker: BrokerConfig

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.db.db_user}:{self.db.db_pass}@{self.db.db_host}:{self.db.db_port}/{self.db.db_name}"

    @property
    def DATABASE_URL_psycopg(self):
        return f"postgresql+psycopg://{self.db.db_user}:{self.db.db_pass}@{self.db.db_host}:{self.db.db_port}/{self.db.db_name}"

    project_name: str

    first_superuser_email: str
    first_superuser_name: str
    first_superuser_password: str


settings = Settings()  # type: ignore
