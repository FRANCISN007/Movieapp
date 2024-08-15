Project Structure

movie-api/

├── main.py               # FastAPI application setup

├── database.py           # Database connection and setup

├── crud.py               # CRUD operations for movies

├── models.py             # SQLAlchemy models for movies, users, etc.

├── auth.py               # Authentication and JWT handling

├── schemas.py            # Pydantic schemas for request/response validation

├── tests/

│   ├── test_api.py       # Unit tests for API endpoints

├── requirements.txt      # Dependencies

├── README.md

├── deployment/           # Deployment related files (using xxxxxx)


# README.md

Movie Listing API
This project implements a movie listing API using FastAPI, PostgreSQL for database storage, 
and JWT for authentication. It allows users to list movies, rate them, add comments, 
and perform various CRUD operations securely.

Features

User registration: All users are expected to register or sign up before carrying out any vital operations, 
sign up and enter the necessary information displayed.

User Authentication: After registration, all users are authenticated first before they can Create, Edit or Delete Movie. 
In the Authentication platform, enter your registered username and password.

User login with JWT token generation: login with your username and password, a token is generated and the token takes 30 minutes 
befor the current user time expires.

Movie Creation:
Creating a movie (authenticated users only): This endpoint allows only an authenticated user to create movie.
This is an example of details for movie creation:

  "title": "Mission Impossible",

  "description": "A movie full of suspense and romance",

  "genres": "Action and comedy movie",

  "writer": "Randy Don",

  "director": "Willy Coke",

  "cast": "James Bond",

  "language": "English",

  "Runtime": "2hr.30mins",

  "year_released": 2010,

Schemas Explanation
Movie ID: (Auto creation) A unique identifier for each movie in the database.

Title: The title of the movie.

Description: A brief summary or description of the movie's plot.

Genres: Categories that classify the movie (e.g., Action, Comedy, Drama).

Writer(s): The name(s) of the writer(s) of the movie.

Director(s): The name(s) of the director(s) of the movie.

Cast: The main actors/actresses in the movie.

Runtime: The duration of the movie in hour and minutes.

Language: The primary language(s) spoken in the movie.

Year Released: The year the movie was released in theaters.

View all movies (public access): 
This endpoint allows the public to view all movies created without Authentication.

View my movies (authenticated users only): 
This is a feature that allows user to see only the movies he/she created.

Edit a movie (only by the user who listed it): 
you can only edit movie that you created 

Delete a movie (only by the user who listed it): 
you can only delete movie that you created 

List Movie
This is a public access endpoint and it is use to list all available movies created by all users

LIst My Movie
This endpoint is use to list only the movie created by the current user

List Movie by ID (public)
This endpoint lists one movie at a time with the specified movie id  

Update Movie by ID 
This endpoint enables the user to update or alter only movies created by him or her by specifting the movie id

Delete Movie
This endpoint enables the user to permanently delete the movie created by himself or herself.
Note: you can not delete any movie that has already been rated or commented on.

Movie Rating:
Rate a movie (authenticated access): Only authenticated user has the right to rate any movie by providing the movid_id to rate
Get ratings for a movie (plubic access): Anybody can view any rated movie by providing the movie_id you want to view its ratings
To delete a Rating, the Rating id is required for authenticated user only to carry this operation

Comments:
Add a comment to a movie (authenticated access): only authenticated user has the right to comment to any movie by providing the movie_id
View comments for a movie (public access): Anybody can view comment made on any movie by provding the movid_id to its comments
To delete a comment, the comment id is required for authenticated user to carry out this operation.

Reply:
Replying a comment (authenticated access): Only authenticated user has the right to reply a comment by providing the comment_id
To delete a Reply (authenticated access): the Reply id is required for authenticated user to carry out this operation




Note: PLease, ensure you click the "Try it Out" button at every endpoint to enter any information, 
then click the Execute botton to process your information.
# Movieapp
