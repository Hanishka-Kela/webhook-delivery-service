from pydantic import BaseModel,EmailStr,Field,ConfigDict
from uuid import UUID
import datetime

class CreateUserRequest(BaseModel):
    email:EmailStr
    password:str = Field(min_length=8)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id:UUID
    email:EmailStr
    is_active:bool
    created_at:datetime.datetime

class UserLogin(BaseModel):
    email:EmailStr
    password:str 