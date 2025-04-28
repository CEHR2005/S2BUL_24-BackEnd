from typing import Any, List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.user import User as UserSchema, UserUpdate

router = APIRouter()

@router.get("/me", response_model=UserSchema)
def get_current_user(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Provides an endpoint to retrieve the currently authenticated user's
    information in a format compatible with the defined Pydantic schema.
    The `id` attribute of the user object is converted to a string prior to
    return to meet schema expectations.

    Args:
        current_user: The currently authenticated user object, resolved
                      using the dependency injection of `get_current_active_user`.

    Returns:
        The authenticated user's information matching the `UserSchema`
        response model.
    """
    # Convert UUID to string to match Pydantic model expectations
    current_user.id = str(current_user.id)
    return current_user

@router.put("/me", response_model=UserSchema)
def update_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Update the details of the currently authenticated user.

    Checks if the username is being updated and confirms it is not already taken
    by another user. Updates the attributes of the current user with the provided
    data and commits the changes to the database. Returns the updated user details.

    Parameters:
    db: Session
        The SQLAlchemy database session used to interact with the database.
    user_in: UserUpdate
        The Pydantic model representing the fields to be updated for the user.
    current_user: User
        The currently authenticated active user retrieved from the request context.

    Returns:
    Any
        The updated user details as a response model.

    Raises:
    HTTPException
        If the provided username is already taken by another user.
    """
    # Check if username is being updated and if it's already taken
    if user_in.username and user_in.username != current_user.username:
        user = db.query(User).filter(User.username == user_in.username).first()
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken",
            )

    # Update user attributes
    for field, value in user_in.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    # Convert UUID to string to match Pydantic model expectations
    current_user.id = str(current_user.id)
    return current_user

@router.get("/{user_id}", response_model=UserSchema)
def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    Fetch a user by their unique ID.

    This function retrieves a user from the database using their unique user ID.
    The user ID is expected to be in UUID format. If the ID is not found,
    an HTTP 404 error is raised. If the ID format is invalid, an HTTP 400
    error is raised.

    Args:
        user_id (str): The unique identifier of the user in UUID format.
        db (Session): A SQLAlchemy database session dependency.

    Returns:
        Any: The user record matching the provided user ID.
    """
    try:
        # Convert string to UUID object before querying
        uuid_obj = uuid.UUID(user_id)
        user = db.query(User).filter(User.id == uuid_obj).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        # Convert UUID to string to match Pydantic model expectations
        user.id = str(user.id)
        return user
    except ValueError:
        # Handle invalid UUID format
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )
