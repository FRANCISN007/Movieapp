# main.py
from fastapi import FastAPI, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth import pwd_context, authenticate_user, create_access_token, get_current_user
from typing import List, Optional
from database import engine, Base, get_db
import crud, models, schemas, auth
#from loguru import logger
from logger import get_logger




logger = get_logger(__name__)


#logger.add("app.log", rotation="500 MB", level="DEBUG")

Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI() 

@app.get("/")
def read_root():
        return {"message":"WELCOME TO MY APP OF MOVIES"}


@app.post("/Registration", response_model=schemas.User, status_code =status.HTTP_201_CREATED, tags= ["User"])

def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    This Session is for user Registration, fill your details below to signup
    """
    logger.info("creating user.....")
    db_user = crud.get_user_by_username(db, username=user.username)
    db_user_by_email = crud.get_user_by_email(db, email=user.email)
    hashed_password = pwd_context.hash(user.password)
    if db_user:
        logger.warning(f"user trying to register but username entered already exist: {user.username}")
        raise HTTPException(status_code=400, detail="Username already registered")
    
    if db_user_by_email:
        logger.error(f"User trying to register but email entered already exists: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")
    logger.info("user successfully created")
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)
    

@app.post("/login", status_code =status.HTTP_201_CREATED, tags=["User"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    This Session is for user to login and generate a token that expires in 30mins time
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.error(f"Failed login attempt for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Credential ",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    logger.info(f"user authorisation successfull for {form_data.username}")
    return {"access_token": access_token, "token_type": "bearer"}


# Movie endpoints
@app.post("/movies/", response_model=schemas.Movie, status_code =status.HTTP_201_CREATED, tags= ["Movie"])
def create_new_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    """
    This is the Movie creation plaform, enter the movie information below
    """
    logger.info(f"User {current_user.username} creating a movie: {movie.title}")
    return crud.create_movie(db=db, movie=movie, user_id=current_user.id)


@app.get("/movies/", response_model=List[schemas.Movie], tags= ["Movie"])
def list_all_movies(db: Session = Depends(get_db), skip: int = 0, limit: int = 10):
    
    """
    This endpoint lists all available Movies created by all user
    """
    
    logger.info("Fetching list of movies")
    return crud.get_movies(db=db, skip=skip, limit=limit)

# Read User Movies
@app.get("/movies/List", response_model=list[schemas.Movie], tags= ["Movie"])
def my_movies(skip: int = 0, limit: int = 10, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    """
    This endpoint lists all Movies created by the current user
    """
    movies = crud.get_user_movies(db, user_id=current_user.id)
    logger.info(f"Fetching only the list of movie(s) created by the user_id:{current_user.id}")
    return movies

@app.get("/movies/Search", response_model=List[schemas.Movie], tags= ["Movie"])
def movie_by_title(search: Optional[str] = "", skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    You can use this endpoint to search for any movie title even if the title name provided doesn't match correctly.
    The Searching entry is case sensitive 
    """
    return db.query(models.Movie).filter( models.Movie.title.contains(search)).offset(skip).limit(limit).all()
    

@app.get("/movies/{movie_id}", response_model=schemas.Movie, tags= ["Movie"])
def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    
    """
    This endpoint views one Movie at a time using the movie_id
    """
    movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        logger.warning(f"Movie not found with id: {movie_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Movie_id {movie_id} does not exist, Please try another movie_id")
    logger.info(f"Fetching details for movie id: {movie_id}, {movie.title}")   
    return movie


@app.put("/movies/{movie_id}", response_model=schemas.Movie, status_code =status.HTTP_201_CREATED, tags= ["Movie"])
def update_movie(movie_id: int, movie: schemas.MovieUpdate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    This platform updates Movies created by the user using the Movie_id
    """
    
    existing_movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if existing_movie is None:
        logger.warning(f"Movie not found with id: {movie_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Movie_id {movie_id} does not exist, Please try another movie_id")
    if existing_movie.owner_id != current_user.id:
        logger.warning(f"User {current_user.username} is not authorized to update movie: {movie.title}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="We are sorry, you are not authorized to update this movie")
    logger.info(f"Updating movie details: {movie.title}")
    return crud.update_movie(db=db, movie_id=movie_id, movie=movie)
    
@app.delete("/movies/{movie_id}", tags= ["Movie"])
def delete_movie(movie_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    This endpoint allows the user to Delete its own created movie
    """
    
    existing_movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if existing_movie is None:
        logger.warning(f"Movie not found with id: {movie_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Movie_id {movie_id} does not exist, Please try another movie_id")
    if existing_movie.owner_id != current_user.id:
        logger.warning(f"User {current_user.username} is not authorized to delete movie_id: {movie_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"You are not authorized to delete movie_id {movie_id}")
    
     # Check if there are related ratings or comments
    if crud.get_ratings_for_movie(db=db, movie_id=movie_id):
        logger.warning(f"trying to delete Movie {movie_id} with rating or comments, but operation aborted")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"You cannot delete movie_id {movie_id} with existing ratings or comments")
    if crud.get_comments_for_movie(db=db, movie_id=movie_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"You cannot delete movie_id {movie_id} with existing ratings or comments")
    
    crud.delete_movie(db=db, movie_id=movie_id)
    logger.info(f"Movie_id {movie_id} deleted successfully")
    return {"message": "Movie deleted successfully"}

    

# Rating endpoints
@app.post("/movies/{movie_id}/rate/", response_model=schemas.Rating, status_code=status.HTTP_201_CREATED, tags=["Rating"])
def create_rating(movie_id: int, rating: schemas.RatingCreate, db: Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):   
    """
    This endpoint allows authenticated users to rate any movie using the movie_id,
    but a user can only rate a movie once. Ratings is between (0-5)
    """
    movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        logger.warning(f"Movie not found with id: {movie_id}")
        raise HTTPException(status_code=404, detail=f"Movie_id {movie_id} does not exist, Please try again")
    
    db_rating = crud.create_rating(db=db, rating=rating, movie_id=movie_id, user_id=current_user.id)
    logger.info(f"User {current_user.username} rated movie: {movie.title}, rating: {rating.rating}")
    return db_rating


@app.get("/movies/{movie_id}/ratings/", response_model=List[schemas.Rating], tags= ["Rating"])
def get_ratings_for_movie(movie_id: int, db: Session = Depends(get_db)):
    
    """
    This endpoint allows the public to view the rated movie using the movie_id
    """
    movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        logger.warning(f"Movie not found with id: {movie_id}")
        raise HTTPException(status_code=404, detail=f"Movie_id {movie_id} does not exist, Please try again")
    logger.info(f"Fetching ratings for movie:{movie.id}, {movie.title}")
    return crud.get_ratings_for_movie(db=db, movie_id=movie_id, )

@app.delete("/ratings/{rating_id}", tags=["Rating"])
def delete_rating(rating_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    This endpoint allows a user to delete their own rating using the rating_id.
    """
    # Fetch the rating by its ID
    existing_rating = crud.get_rating_by_id(db=db, rating_id=rating_id)
    
    # Check if the rating exists
    if existing_rating is None:
        logger.warning(f"Rating not found with id: {rating_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Rating_id {rating_id} does not exist, Please try another rating_id")
    
    # Check if the current user is the owner of the rating
    if existing_rating.user_id != current_user.id:
        logger.warning(f"User {current_user.username} is not authorized to delete rating_id: {rating_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this rating")
    
    # Delete the rating
    crud.delete_rating(db=db, rating_id=rating_id)
    logger.info(f"Rating_id {rating_id} deleted successfully")
    return {"message": "Rating deleted successfully"}
   

# comments, response_model=schema.CommentResponse
@app.post("/movies/{movie_id}/comments/", response_model=schemas.CommentResponse, status_code =status.HTTP_201_CREATED, tags= ["Comment"])
def create_comment(comment: schemas.CommentCreate, 
                   movie_id: int, 
                   current_user: schemas.User = Depends(get_current_user), 
                   db: Session = Depends(get_db)):
    logger.info(f"creating comment on movie_id {movie_id} by {current_user.username}")
    """
    This endpoint allows the user to comment on any movie using the movie_id
    """
    movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        logger.warning(f"Movie not found with id: {movie_id}")
        raise HTTPException(status_code=404, detail=f"Movie_id {movie_id} does not exist, Please try again")
    
    db_comment = crud.create_comment(db, comment, current_user.id, movie_id)
    return db_comment

    
@app.get("/movies/{movie_id}/comments/", response_model=schemas.MovieCommentResponse, tags= ["Comment"])
def get_comments(movie_id: int, db: Session = Depends(get_db)):
    
    """
    This endpoint allows the public to view comments & replies attached to any movie using the movie_id
    """
    movie = crud.get_movie_by_id(db=db, movie_id=movie_id)
    if movie is None:
        logger.warning(f"Movie not found with id: {movie_id}")
        raise HTTPException(status_code=404, detail=f"Movie_id {movie_id} does not exist, Please try again")
    logger.info(f"Fetching comments for movie:{movie.id}, {movie.title}")
    return crud.get_comments(db=db, movie_id=movie_id)    


@app.delete("/comments/{comment_id}", tags=["Comment"])
def delete_comment(comment_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    This endpoint allows the user to delete their own comment using the comment_id.
    """
    # Fetch the comment by its ID
    existing_comment = crud.get_comment_by_id(db=db, comment_id=comment_id)
    
    # Check if the comment exists
    if existing_comment is None:
        logger.warning(f"Comment not found with id: {comment_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Comment_id {comment_id} does not exist, Please try another comment_id")
    
    # Check if the current user is the owner of the comment
    if existing_comment.user_id != current_user.id:
        logger.warning(f"User {current_user.username} is not authorized to delete comment_id: {comment_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this comment")
    
    # Delete the comment
    crud.delete_comment(db=db, comment_id=comment_id)
    logger.info(f"Comment_id {comment_id} deleted successfully")
    return {"message": "Comment deleted successfully"}

# create reply
@app.post('/{comment_id}/replies', response_model=schemas.CommentResponse, tags= ["Reply Comment"])
def create_reply(payload: schemas.ReplyCreate, comment_id:int, current_user: schemas.User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_comment = crud.get_comment_by_id(db, comment_id)
    
    """
    This endpoint allows the user to create a reply upon an existing comment to a movie 
    """
    
    if not db_comment:
        logger.warning(f"comment_id {comment_id} not found")
        raise HTTPException(status_code=404, detail=f"Comment_id {comment_id} does not exist")
    
    # Extract the original comment text
    original_comment = db_comment.comment
    movie_id = db_comment.movie_id
    
    reply = crud.create_reply(db, payload, comment_id, current_user.id, original_comment, movie_id )
    db_comment.replies.append(reply)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment




@app.delete("/Reply/{reply_id}", tags=["Reply Comment"])
def delete_reply(reply_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """
    This endpoint allows the user to delete their replies made on comment using the reply_id.
    """

    existing_reply = crud.get_reply_by_id(db=db, reply_id=reply_id)
    
    # Check if the reply_id exists
    if existing_reply is None:
        logger.warning(f"Reply_id {reply_id} not found")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reply_id {reply_id} does not exist, Please try another reply_id")
    
    # Check if the current user is the owner of the reply
    if existing_reply.user_id != current_user.id:
        logger.warning(f"User {current_user.username} is not authorized to delete reply_id: {reply_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to delete this reply")
    
    # Delete the reply
    crud.delete_reply(db=db, reply_id=reply_id)
    logger.info(f"Reply_id {reply_id} deleted successfully")
    return {"message": "Reply deleted successfully"}
