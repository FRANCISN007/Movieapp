# models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String)
    email = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    hashed_password = Column(String, nullable=False)
    
    
    movies = relationship("Movie", back_populates="owner")
    ratings = relationship("Rating", back_populates="created_by")
    
    comments = relationship("Comment", back_populates="user", overlaps="created_by")
    

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    genres= Column(String)
    writer= Column(String)
    director= Column(String)
    cast= Column(String)
    language=  Column(String)
    Runtime=  Column(String)
    year_released = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner_id = Column(Integer, ForeignKey("users.id"))
    average_rating = Column(Float, nullable=True)

    owner = relationship("User", back_populates="movies")
    comments = relationship("Comment", back_populates="movie")
    ratings = relationship("Rating", back_populates="movie")
    
    
    

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Float, nullable=False)  
    movie_id = Column(Integer, ForeignKey("movies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    movie = relationship("Movie", back_populates="ratings")
    created_by = relationship("User", back_populates="ratings")
    
    __table_args__ = (UniqueConstraint('user_id', 'movie_id', name='unique_user_movie_rating'),)
    
    
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    comment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    movie_id = Column(Integer, ForeignKey("movies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    #created_by = relationship("User", back_populates="comments")
    
    #user = relationship("User")
    #movie = relationship("Movie", back_populates="comments")
    #replies = relationship("Reply", back_populates="comment")
    
    user = relationship("User", back_populates="comments", overlaps="created_by")
    created_by = relationship("User", overlaps="user, comments")
    movie = relationship("Movie", back_populates="comments")
    replies = relationship("Reply", back_populates="comment")
    
class Reply(Base):
    __tablename__ = "replies"
    
    id = Column(Integer, primary_key=True)
    reply = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    original_comment = Column(String, nullable=False)
    movie_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
 
    comment = relationship("Comment", back_populates="replies")
    user = relationship("User")
    
    