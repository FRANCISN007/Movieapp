# schemas.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


    
class UserResponse(BaseModel):
    id: int 
    username: str
    full_name: str
    email: str
    
class UserRating(BaseModel):
    id: int 
    username: str
    full_name: str
    
class UserComment(BaseModel):
    id: int 
    username: str
    full_name: str   
       
    
class UserBase(BaseModel):
    username: str
    full_name: str  
        
    
class UserCreate(UserBase):
    email: str
    password: str

class User(UserBase): 
    email: str
    id: int
    
    model_config = ConfigDict(from_attributes=True)    

    
class UserResponseModel(BaseModel):
    id: int
    username: str
    full_name: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
        

class MovieBase(BaseModel):
    title: str
    description: Optional[str]= None
    genres: Optional[str]= None
    writer: Optional[str]= None
    director: Optional[str]= None
    cast: str
    language: Optional[str]= None
    Runtime: Optional[str]= None
    year_released: int
    

class Movie(MovieBase):
    id: int
    owner_id: int
    created_at: datetime
    owner: Optional[UserResponse] 
    average_rating: Optional[float] 

    class Config:
        orm_mode = True

class MovieCreate(MovieBase):
    pass

class MovieUpdate(MovieBase):
    pass



class RatingBase(BaseModel):
    rating: float
    
class Rate(BaseModel):
    rating: float
    
     
class Rating(Rate):
    id: int
    movie_id: int
    created_at: datetime
    created_by: Optional[UserRating]
    

class RatingCreate(RatingBase):
    pass
    

class CommentBase(BaseModel):
    comment: str
    
    
class Comment(CommentBase):
    id: int
    movie_id: int
    created_at: datetime
    created_by: Optional[UserComment]
    
    
    class Config:
        orm_mode = True

class CommentCreate(CommentBase):
    pass


class ReplyCreate(BaseModel):
    reply: str
    
    
class ReplyResponse(BaseModel):
    id: int
    reply: str
    user_id: int
    comment_id: int
    original_comment: str
    movie_id: int
    created_at: datetime


class CommentResponse(BaseModel):
    id: int
    comment: str
    user: UserResponseModel
    movie: MovieBase
    replies: List[ReplyResponse]

    model_config = ConfigDict(from_attributes=True)
    
    
class MovieCommentResponse(BaseModel):
    
    comments: List[CommentResponse] = []

    model_config = ConfigDict(from_attributes=True)    
    