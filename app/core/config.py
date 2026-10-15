from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import URL


class AppSettings(BaseSettings):
    """Настройки приложения."""

    NAME: str = "Wordle1234"
    DEBUG: bool
    VERSION: str = "1.4.8.8"
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]
    CORS_ORIGINS: list[str] = []


class JWTSettings(BaseSettings):
    """Настройки JWT."""

    ALGORITHM: str
    SECRET_KEY: SecretStr
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7


class DatabaseSettings(BaseSettings):
    """Настройки подключения к БД."""

    USER: str
    PASSWORD: SecretStr
    HOST: str
    PORT: int = 5432
    NAME: str
    ECHO: bool
    POOL_SIZE: int
    MAX_OVERFLOW: int
    POOL_PRE_PING: bool = True

    @property
    def URL(self) -> str:
        """Собрать URL подключения к БД."""

        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.USER,
            password=self.PASSWORD.get_secret_value(),
            host=self.HOST,
            port=self.PORT,
            database=self.NAME,
        ).render_as_string(hide_password=False)


class LLMSettings(BaseSettings):
    BASE_URL: str | None = None
    API_KEY: SecretStr | None = None
    MODEL: str | None = None


class GameSettings(BaseSettings):
    """Настройки игровой механики."""

    WORD_LENGTH: int = 5
    MAX_ATTEMPTS: int = 6
    POINTS_PER_ATTEMPT: int = 100
    LEADERBOARD_SIZE: int = 10
    WORD_PROVIDER: str = "stub"


class Settings(BaseSettings):
    """Корневые настройки приложения."""

    app: AppSettings
    jwt: JWTSettings
    database: DatabaseSettings
    llm: LLMSettings = LLMSettings()
    game: GameSettings

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )


settings = Settings()
