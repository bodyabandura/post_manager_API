from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import User, Post, Base
from schemas import Post, PostCreate, PostBase
import crud
from database import SessionLocal, engine
import cachetools.func
from auth.auth_handler import signJWT, decodeJWT
from auth.auth_bearer import JWTBearer
from auth.schemas import UserCreate, UserLogin
from auth.utils import verify_password, hash_password

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/user/signup", tags=["user"])
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    A function to create a new user in the database.
    Parameters:
    - user: A UserCreate object containing user information.
    - db: A database session.
    Returns:
    - A message indicating the success of user creation.
    """

    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created successfully"}


@app.post("/user/login", tags=["user"])
def user_login(user: UserLogin, db: Session = Depends(get_db)):
    """
    A POST endpoint to login a user.
    Parameters:
    - user: UserLogin object containing username and password
    - db: Session object for the database
    Returns:
    - JWT token for authentication
    """

    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user and verify_password(user.password, db_user.hashed_password):
        return signJWT(db_user.email)
    else:
        raise HTTPException(status_code=400, detail="Invalid credentials")


@app.post("/posts", tags=["posts"])
def add_post(post: PostCreate, db: Session = Depends(get_db), token: str = Depends(JWTBearer())):
    """
    Creates a new post in the database.

    Args:
        post (PostCreate): The post data to be created.
        db (Session, optional): The database session. Defaults to Depends(get_db).
        token (str, optional): The JWT token. Defaults to Depends(JWTBearer()).

    Returns:
        dict: A dictionary containing the detail message and the id of the created post.

    Raises:
        HTTPException: If the post size exceeds 1 MB.
    """
    # Decode the JWT token to get the user email
    user_email = decodeJWT(token)['user_id']

    # Get the user id from the database
    user_id = db.query(User).filter(User.email == user_email).first().id

    # Check if the post size exceeds 1 MB
    if len(post.text.encode('utf-8')) > 1_048_576:
        raise HTTPException(status_code=400, detail="Post size exceeds 1 MB")

    # Create the post in the database
    created_post = crud.create_post(db=db, post=post, user_id=user_id)

    # Return the detail message and the id of the created post
    return {
        "detail": "Post created successfully",
        "post_id": created_post.id
    }


@cachetools.func.ttl_cache(maxsize=1024, ttl=300)
@app.get("/posts", response_model=list[Post], tags=["posts"])
def get_posts(db: Session = Depends(get_db), token: str = Depends(JWTBearer())):
    """
    Get the posts for a specific user based on the provided token.

    Args:
        db (Session): The database session.
        token (str): The JWT token.

    Returns:
        list: A list of posts for the specified user.
    """

    user_email = decodeJWT(token)['user_id']

    user_id = db.query(User).filter(User.email == user_email).first().id

    # Retrieve the posts for the user
    return crud.get_posts(db=db, user_id=user_id)


@app.delete("/posts/{post_id}", tags=["posts"])
def delete_post(post_id: int, db: Session = Depends(get_db), token: str = Depends(JWTBearer())):
    """
        Deletes a post from the database.

        Args:
            post_id (int): The ID of the post to be deleted.
            db (Session, optional): The database session. Defaults to Depends(get_db).
            token (str, optional): The JWT token. Defaults to Depends(JWTBearer()).

        Raises:
            HTTPException: If the post is not found.

        Returns:
            Dict[str, str]: A dictionary indicating the success of the deletion.
        """
    user_email = decodeJWT(token)['user_id']

    user_id = db.query(User).filter(User.email == user_email).first().id

    # Delete the post from the database
    success = crud.delete_post(db=db, post_id=post_id, user_id=user_id)

    # Raise an exception if the post is not found
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")

    # Return a success message
    return {"detail": "Post deleted successfully"}
