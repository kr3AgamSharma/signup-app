from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import List, Optional

class UserBase(BaseModel):
    username: str = Field(..., max_length=30)
    first_name: str = Field(..., max_length=50)
    last_name: str = Field(..., max_length=50)
    email: str = Field(..., max_length=100)
    address: str = Field(..., max_length=200)

class UserCreate(UserBase):#this is used strictly for the incomming signup request
    password: str=Field(..., min_length=6, max_length=100)

class User(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class userlogin(BaseModel):
    username: str=Field(...,min_length=3, max_length=30)
    password: str=Field(..., min_length=6, max_length=100)

class passwordreset(BaseModel):
    username: str=Field(...,min_length=3, max_length=30)
    email: str=Field(..., max_length=100)
    new_password: str=Field(..., min_length=6, max_length=100)

class accountdelete(BaseModel):
    username: str=Field(...,min_length=3, max_length=30)
    password: str=Field(..., min_length=6, max_length=100)

    
