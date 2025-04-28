from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.database.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, Token, User as UserSchema

router = APIRouter()

@router.post("/register", response_model=UserSchema)
def register(*, db: Session = Depends(get_db), user_in: UserCreate) -> Any:
    """
    Handles user registration by creating a new user in the database if the provided
    email and username are not already associated with an existing account. Performs
    validations to ensure the uniqueness of email and username, hashes the user's
    password, and stores the new user details.

    Args:
        db (Session): A database session dependency that provides access to the
            database operations.
        user_in (UserCreate): Pydantic model that holds the user input data for
            creating a new user. Expects attributes like username, email, password,
            first_name, last_name, age, gender, country, and continent.

    Raises:
        HTTPException: If a user with the provided email already exists. Responds with
            HTTP 400 status and an appropriate error message.
        HTTPException: If a user with the provided username already exists. Responds
            with HTTP 400 status and an appropriate error message.

    Returns:
        Any: A Pydantic schema representation of the newly created user, including all
            user details (except sensitive ones like the unencrypted password).
    """
    # Check if user with this email already exists
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists",
        )

    # Check if user with this username already exists
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this username already exists",
        )

    # Create new user
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        password=get_password_hash(user_in.password),
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        age=user_in.age,
        gender=user_in.gender,
        country=user_in.country,
        continent=user_in.continent,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Convert UUID to string to match Pydantic model expectations
    db_user.id = str(db_user.id)
    return db_user

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    Handles the user login process by authenticating via email or username and password.
    If the authentication is successful, it generates and returns a new access token.

    Parameters:
    db: Session
        The database session dependency required to query the database.
    form_data: OAuth2PasswordRequestForm
        The form data containing the login credentials, specifically the username
        (used interchangeably for email or username) and password.

    Returns:
    Any
        Returns a dictionary containing the JSON Web Token (JWT) as 'access_token'
        and the token type as 'bearer'.

    Raises:
    HTTPException
        Raises HTTP 401 Unauthorized if the email/username does not exist in the
        database or the provided password is incorrect.
    """
    # Try to find user by email
    user = db.query(User).filter(User.email == form_data.username).first()

    # If not found by email, try by username
    if not user:
        user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email/username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}
