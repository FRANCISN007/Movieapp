# crud.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
import models, schemas
from sqlalchemy.orm import Session, joinedload
from models import Rating


def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        username=user.username, 
        full_name=user.full_name, 
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_movie(db: Session, movie: schemas.MovieCreate, user_id: int):
    db_movie = models.Movie(**movie.dict(), owner_id=user_id)
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie
    
def get_movies(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Movie).offset(skip).limit(limit).all()

# Read User Movies
def get_user_movies(db: Session, user_id: int):
    return db.query(models.Movie).filter(models.Movie.owner_id == user_id).all()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_movie_by_id(db: Session, movie_id: int):
    return db.query(models.Movie).filter(models.Movie.id == movie_id).first()


def update_movie(db: Session, movie_id: int, movie: schemas.MovieUpdate):
    db_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if db_movie:
        for var, value in vars(movie).items():
            setattr(db_movie, var, value)
        db.commit()
        db.refresh(db_movie)
    return db_movie

def delete_movie(db: Session, movie_id: int):
    db.query(models.Movie).filter(models.Movie.id == movie_id).delete()
    db.commit()
    
def get_comments_for_movie(db: Session, movie_id: int):
    return db.query(models.Comment).filter(models.Comment.movie_id == movie_id).all()    


def create_comment(db:Session, payload:schemas.CommentCreate, current_user: int, movie_id):
    db_comment = models.Comment(**payload.model_dump(),
                                user_id=current_user,
                                movie_id=movie_id
                             )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comments(db: Session, movie_id: int ):
     # Fetch the movie with its comments and their replies
    movie_with_comments = db.query(models.Movie).options(joinedload(models.Movie.comments).joinedload(models.Comment.replies)
    ).filter(models.Movie.id == movie_id).first()
    return movie_with_comments

def get_comment_by_id(db: Session, comment_id: int):
    return db.query(models.Comment).filter(models.Comment.id == comment_id).first()

def get_reply_by_id(db: Session, reply_id: int):
    return db.query(models.Reply).filter(models.Reply.id == reply_id).first()

# reply
def create_reply(db: Session, reply: schemas.ReplyCreate, comment_id: int, current_user: int, original_comment: str, movie_id: int):
    db_reply_comment = models.Reply(**reply.model_dump(),
                                    user_id = current_user,
                                    comment_id=comment_id,
                                    original_comment=original_comment,
                                    movie_id=movie_id
                                    )
    db.add(db_reply_comment)
    db.commit()
    db.refresh(db_reply_comment)
    return db_reply_comment


def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if db_comment:
        db.delete(db_comment)
        db.commit()


def delete_reply(db: Session, reply_id: int):
    db_reply = db.query(models.Reply).filter(models.Reply.id == reply_id).first()
    if db_reply:
        db.delete(db_reply)
        db.commit()


def create_rating(db: Session, rating: schemas.RatingCreate, movie_id: int, user_id: int):
    # Check if the user has already rated this movie
    existing_rating = db.query(models.Rating).filter(models.Rating.movie_id == movie_id, models.Rating.user_id == user_id).first()
    
    if existing_rating:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"You have already rated movie_id {movie_id}")
    
     # Check if the rating is within the acceptable range
    if rating.rating < 0 or rating.rating > 5:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"{rating} is invalid, Rating range should be from 0 to 5")
       
    new_rating = Rating(movie_id=movie_id, user_id=user_id, rating=rating.rating)
    db.add(new_rating)
    db.commit()
    db.refresh(new_rating)
    
    update_movie_average_rating(db, movie_id)
    
    return new_rating

def update_movie_average_rating(db: Session, movie_id: int):
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    ratings = db.query(models.Rating).filter(models.Rating.movie_id == movie_id).all()
    if ratings:
        average_rating = sum(r.rating for r in ratings) / len(ratings)
        movie.average_rating = round(average_rating, 2)
    else:
        movie.average_rating = None
    
    db.commit()
    db.refresh(movie)


def get_ratings_for_movie(db: Session, movie_id: int):
   return db.query(models.Rating).filter(models.Rating.movie_id == movie_id).all()

def get_rating_by_id(db: Session, rating_id: int):
    return db.query(models.Rating).filter(models.Rating.id == rating_id).first()

def delete_rating(db: Session, rating_id: int):
    db_rating = db.query(models.Rating).filter(models.Rating.id == rating_id).first()
    if db_rating:
        
        movie_id = db_rating.movie_id
        
        db.delete(db_rating)
        db.commit()
        
        update_movie_average_rating(db, movie_id)
        
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rating_id {rating_id} does not exist")   

   



 