import json
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from main import app, get_db
from database import SessionLocal, engine
from models import Base, User, Movie, Rating, Comment
import crud, pytest, schemas, models
from main import get_db, get_current_user

# Create a test client using TestClient
client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override database dependency for testing
def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
def override_get_current_user():
    return models.User(id=1, username="testuser")

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


# Set up and tear down for tests
def setup_module(module):
    Base.metadata.create_all(bind=engine)

def teardown_module(module):
    Base.metadata.drop_all(bind=engine)
    
def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message":"WELCOME TO MY APP OF MOVIES"}


def test_read_movies():
    response = client.get("/movies/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    

@pytest.fixture(scope="module")
def test_ratings(test_movie, test_db: Session):
    ratings = [
        schemas.RatingCreate(
            rating=4,
            comment="Great movie!"
        ),
        schemas.RatingCreate(
            rating=5,
            comment="Good movie!"
        )
    ]
    for rating_data in ratings:
        crud.create_rating(db=test_db, rating=rating_data, movie_id=test_movie.id)
    return ratings

def test_get_ratings_for_nonexistent_movie(test_db: Session):
    nonexistent_movie_id = 9999
    response = client.get(f"/movies/{nonexistent_movie_id}/ratings/")
    assert response.status_code == 404
    assert response.json()["detail"] == f"Movie_id {nonexistent_movie_id} does not exist, Please try again"


