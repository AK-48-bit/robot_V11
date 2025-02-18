from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


class Settings(AppBaseSettings):
    BACK_HOST: str = Field(..., env='BACK_HOST')
    BACK_PORT: str = Field(..., env='BACK_PORT')
    ROBOT_HOST: str = Field(..., env='ROBOT_HOST')
    JETSON_HOST: str = Field(..., env='JETSON_HOST')
    JETSON_USER: str = Field(..., env='JETSON_USER')
    JETSON_PASSWORD: str = Field(..., env='JETSON_PASSWORD')


settings = Settings()
