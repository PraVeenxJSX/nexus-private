from pydantic import BaseModel, ConfigDict, EmailStr, Field
class RegisterIn(BaseModel): email: EmailStr; password: str = Field(min_length=8, max_length=128)
class LoginIn(BaseModel): email: EmailStr; password: str
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: str
    role: str
class TokenOut(BaseModel): access_token: str; token_type: str = "bearer"; user: UserOut
class ChatIn(BaseModel): question: str = Field(min_length=2, max_length=8000); conversation_id: str | None = None
class ChatOut(BaseModel): answer: str; sources: list[dict] = Field(default_factory=list); conversation_id: str | None = None
