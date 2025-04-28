from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.security import get_current_active_user
from app.database.database import get_db
from app.models.comment import Comment
from app.models.movie import Movie
from app.models.user import User
from app.schemas.comment import Comment as CommentSchema, CommentCreate, CommentUpdate, CommentWithUser

router = APIRouter()

@router.get("/movie/{movie_id}", response_model=List[CommentWithUser])
def get_comments_by_movie(
    movie_id: str,
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get comments for a specific movie including user information.

    This function retrieves all comments associated with a given movie. It also includes
    the user information for each comment. The response is formatted as per the
    `CommentWithUser` schema. If the movie does not exist, an HTTP 404 error is raised.

    Arguments:
        movie_id (str): The ID of the movie whose comments are to be retrieved.
        db (Session): The database session dependency.
        skip (int): The number of comments to skip for pagination. Default is 0.
        limit (int): The maximum number of comments to retrieve. Default is 100.

    Returns:
        Any: A list of comments for the specified movie, structured as per the
        `CommentWithUser` schema.
    """
    # Check if movie exists
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    # Get comments with user information
    comments = (
        db.query(Comment)
        .filter(Comment.movie_id == movie_id)
        .options(joinedload(Comment.user))
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Format the response to match CommentWithUser schema
    result = []
    for comment in comments:
        comment_dict = {
            "id": str(comment.id),
            "movie_id": str(comment.movie_id),
            "user_id": str(comment.user_id),
            "text": comment.text,
            "created_at": comment.created_at,
            "updated_at": comment.updated_at,
            "user": {
                "id": str(comment.user.id),
                "username": comment.user.username,
            }
        }
        result.append(comment_dict)

    return result

@router.post("/", response_model=CommentSchema)
def create_comment(
    *,
    db: Session = Depends(get_db),
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Creates a new comment on a specific movie by the current authenticated user.

    This function allows a user to add a comment to a movie in the database. It
    requires the movie to exist and the user to be authenticated. If the movie
    does not exist, an exception will be raised. The function stores the comment
    in the database and returns the created comment with converted identifier
    fields to match expected response format.

    Parameters:
    db (Session): The database session dependency.
    comment_in (CommentCreate): The input data for creating the comment,
        including the movie ID and comment text.
    current_user (User): The currently authenticated user making the request.

    Returns:
    Any: The created comment object with identifiers converted to strings.
    """
    # Check if movie exists
    movie = db.query(Movie).filter(Movie.id == comment_in.movie_id).first()
    if not movie:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found",
        )

    comment = Comment(
        movie_id=comment_in.movie_id,
        user_id=current_user.id,
        text=comment_in.text,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Convert UUIDs to strings to match Pydantic model expectations
    comment.id = str(comment.id)
    comment.movie_id = str(comment.movie_id)
    comment.user_id = str(comment.user_id)
    return comment

@router.put("/{comment_id}", response_model=CommentSchema)
def update_comment(
    *,
    db: Session = Depends(get_db),
    comment_id: str,
    comment_in: CommentUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Updates an existing comment in the database.

    This function allows authorized users to update the text of an existing
    comment. Only the author of the comment or an admin user has permission to
    perform this update. If the comment does not exist, or if the user lacks the
    necessary permissions, an HTTP exception is raised. Upon successful update, the
    updated comment data, including UUIDs converted to strings, is returned.

    Parameters:
    db : Session
        The database session dependency used for querying and persisting data.

    comment_id : str
        The unique identifier of the comment to be updated.

    comment_in : CommentUpdate
        The data for updating the comment. This must adhere to the structure defined
        by the CommentUpdate model.

    current_user : User
        The currently authenticated user, retrieved via dependency injection.

    Returns:
    Any
        The updated comment data after successfully applying the changes.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Only the comment author or an admin can update the comment
    if str(comment.user_id) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # Update comment text
    comment.text = comment_in.text

    db.add(comment)
    db.commit()
    db.refresh(comment)

    # Convert UUIDs to strings to match Pydantic model expectations
    comment.id = str(comment.id)
    comment.movie_id = str(comment.movie_id)
    comment.user_id = str(comment.user_id)
    return comment

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    *,
    db: Session = Depends(get_db),
    comment_id: str,
    current_user: User = Depends(get_current_active_user),
) -> None:
    """
    Handles the deletion of a specific comment by its ID. Ensures that only the comment's
    author or an admin can perform the delete operation.

    Arguments:
        db (Session): Database session dependency for querying the database.
        comment_id (str): ID of the comment to be deleted.
        current_user (User): The currently active user authenticated through dependency.

    Raises:
        HTTPException: If the comment is not found in the database.
        HTTPException: If the current user does not have sufficient permissions to delete
        the comment.

    Returns:
        None: Successfully removes the comment from the database or raises an error if not allowed.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    # Only the comment author or an admin can delete the comment
    if str(comment.user_id) != str(current_user.id) and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    db.delete(comment)
    db.commit()
