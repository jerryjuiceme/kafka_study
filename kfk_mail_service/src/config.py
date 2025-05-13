from typing import Literal
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

LOG_DEFAULT_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(module)10s: %(lineno)-3d %(levelname)-7s - %(message)s"
)

BASE_DIR = Path(__file__).parent.parent


class LoggingConfig(BaseModel):
    log_level: Literal["DEBUG", "INFO", "ERROR", "WARNING", "CRITICAL"]
    log_format: str = LOG_DEFAULT_FORMAT
    datefmt: str = "%Y-%m-%d %H:%M:%S"


class SmtpConfig(BaseModel):
    smtp_host: str
    smtp_port: int
    smtp_user: str
    smtp_pass: str
    smtp_timeout: int
    maildev_host: str
    maildev_port: int
    smtp_type: Literal["maildev", "smtp"]


class StorageConfig(BaseModel):
    storage_type: Literal["local", "google_drive"] = "local"
    local_storage_csv_path: str = "src/static/csv"
    local_storage_template_path: str = "src/static/templates/template.html"
    global_path: str = "/Users/jerry/Projects/Study/Kafka Study/kfk_client"


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

    smtp: SmtpConfig
    logging: LoggingConfig
    project_name: str
    mode: Literal["DEV", "PROD", "TEST"] = "DEV"
    storage: StorageConfig = StorageConfig()
    broker: BrokerConfig


settings = Settings()  # type: ignore
