from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "NexusAI"
    environment: str = "development"
    secret_key: str = "CHANGE_ME_TO_A_LONG_RANDOM_SECRET"
    access_token_expire_minutes: int = 60 * 24
    database_url: str = "sqlite+aiosqlite:///./nexusai.db"

    # LLM provider: "nvidia" or "openai"
    llm_provider: str = "nvidia"
    nvidia_api_key: str = ""
    nvidia_base_url: str = "https://integrate.api.nvidia.com/v1"
    nvidia_model: str = "nvidia/nemotron-3-ultra-550b-a55b"

    # Optional OpenAI fallback
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Embeddings run locally; they do not use the LLM API key.
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    vector_store_path: str = "./storage/chroma"
    upload_dir: str = "./storage/uploads"
    max_upload_mb: int = 20
    cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def origins(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
