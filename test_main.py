import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from main import app
from database import Base, get_db
import schemas, crud

# Create a temporary test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the get_db dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "WELCOME TO MY APP OF MOVIES"}

def test_user_registration(setup_db):
    response = client.post("/Registration", json={
        "username": "testuser",
        "full_name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "testuser"

def test_user_login(setup_db):
    response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 201
    assert "access_token" in response.json()

def test_create_movie(setup_db):
    login_response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    token = login_response.json()["access_token"]
    
    response = client.post("/movies/", json={
        "title": "Test Movie",
        "description": "A test movie description",
        "year": 2024
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["title"] == "Test Movie"
    
def test_read_movies():
    response = client.get("/movies/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
        

def test_list_movies(setup_db):
    response = client.get("/movies/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_get_movie_by_id(setup_db):
    response = client.get("/movies/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_update_movie(setup_db):
    login_response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    token = login_response.json()["access_token"]

    response = client.put("/movies/1", json={
        "title": "Updated Test Movie",
        "description": "An updated test movie description",
        "year": 2025
    }, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["title"] == "Updated Test Movie"

def test_delete_movie(setup_db):
    login_response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    token = login_response.json()["access_token"]

    response = client.delete("/movies/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Movie deleted successfully"}

def test_create_comment(setup_db):
    login_response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    token = login_response.json()["access_token"]

    response = client.post("/movies/2/comments/", json={"content": "Test comment"}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["content"] == "Test comment"

def test_get_comments_for_movie(setup_db):
    response = client.get("/movies/2/comments/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_create_rating(setup_db):
    login_response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    token = login_response.json()["access_token"]

    response = client.post("/movies/2/rate/", json={"rating": 5}, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["rating"] == 5

def test_delete_rating(setup_db):
    login_response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    token = login_response.json()["access_token"]

    response = client.delete("/ratings/1", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Rating deleted successfully"}
    
    

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


    
    
    
   
