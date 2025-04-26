from datetime import datetime
from typing import Optional
from pydantic import BaseModel

# Shared properties
class CommentBase(BaseModel):
    text: str

# Properties to receive via API on creation
class CommentCreate(CommentBase):
    movie_id: str

# Properties to receive via API on update
class CommentUpdate(CommentBase):
    pass

# Properties to return via API
class Comment(CommentBase):
    id: str
    movie_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Properties to return via API with user information
class CommentWithUser(Comment):
    user: dict

    class Config:
        from_attributes = True
