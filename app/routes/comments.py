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
    Get all comments for a movie.
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
    Create a new comment.
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
    Update a comment.
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
    Delete a comment.
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
