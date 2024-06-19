## Project Documentation: FastAPI PostManager
### Overview

This project implements an API for creating and managing posts, allowing users to sign up, log in, create, view, and delete posts. The project uses FastAPI to create a web server and MySQL to store data.

### Functionality

    Signup: Users can sign up with an email and password.
    Login: Users can log in with their email and password to receive a JWT token.
    Add Post: Authenticated users can create new posts.
    View Posts: Authenticated users can view their posts.
    Delete Post: Authenticated users can delete their posts.
    Token-based Authentication: Ensures secure access to protected endpoints.
    Caching: Uses in-memory caching to improve performance.

### Technologies

    FastAPI: A framework for creating REST APIs.
    SQLAlchemy: ORM for interacting with the database.
    MySQL: A database for storing information about posts.
    Uvicorn: ASGI server for deploying FastAPI applications.
    Alembic: Database migrations tool.

### Installation and configuration

Make sure you have Python 3.10+ and pip installed. Then follow the steps below to set up your project.
Clone the repository

```bash
git clone https://your-repository-link
cd your-project-folder
```

### Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

### Setting dependencies

```bash
pip install -r requirements.txt
```


### Database configuration

    Install and configure MySQL.
    Create a database and user in MySQL.
    Update the alembic.ini file with your MySQL connection details.
    Update the .env configuration file (use the example data from .env.sample). 

### Alembic configuration
    Configure alembic.ini with your MySQL database URL:
    sqlalchemy.url = mysql://username:password@localhost/dbname (line 63)

    Generate and apply the initial migration:
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

```

### Starting the server

```bash
uvicorn main:app --reload
```

### Usage
    Signup: Send a POST request to /signup with email and password.
    Login: Send a POST request to /token with email and password to receive a JWT token.
    Add Post: Send a POST request to /posts with text and the JWT token in the Authorization header.
    View Posts: Send a GET request to /posts with the JWT token in the Authorization header.
    Delete Post: Send a DELETE request to /posts/{post_id} with the JWT token in the Authorization header.
