from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db: str = "newsdb"
    backend_port: int = 8000

    crawl_interval_minutes: int = 30
    crawl_concurrency: int = 5
    max_links_per_source: int = 20
    content_max_length: int = 5000
    http_retry_count: int = 2
    http_retry_backoff_seconds: float = 1.0
    http_timeout_seconds: float = 30.0
    playwright_timeout_seconds: float = 60.0
    crawl_lock_ttl_seconds: int = 1800

    log_level: str = "INFO"

    # Bảo vệ các endpoint ghi (POST/PATCH/DELETE).
    # Để trống → bỏ qua kiểm tra (dev mode).
    # Production: đặt chuỗi ngẫu nhiên dài ≥32 ký tự.
    api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
