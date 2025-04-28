from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

# Shared properties
class CommentBase(BaseModel):
    """
    Represents a comment within the system.

    This class is used for defining the basic structure of a comment. It stores
    the text content of the comment and can serve as a base class for more
    specialized comment-related classes.
    """
    text: str

# Properties to receive via API on creation
class CommentCreate(CommentBase):
    """
    Represents the data structure required to create a new comment.

    This class defines attributes necessary for creating a comment associated
    with a movie. It extends the base class `CommentBase` to include an additional
    attribute `movie_id` which specifies the movie for which the comment is being
    added.

    Attributes:
        movie_id (str): The unique identifier of the movie associated with the comment.
    """
    movie_id: str

# Properties to receive via API on update
class CommentUpdate(CommentBase):
    """
    Represents an updated comment in the system.

    This class inherits from CommentBase and is used to handle updated comments.
    It does not add any new functionality or attributes beyond what is provided
    by the parent class. Use this class to represent or work with comments that
    require updates or modifications.
    """
    pass

# Properties to return via API
class Comment(CommentBase):
    """
    Represents a comment in the system.

    This class defines the structure and attributes for a comment, including
    information about the associated movie, the user who made the comment, and
    timestamps for creation and updates. It serves as a model to encapsulate comment
    data and its associated metadata.

    Attributes:
        id: Unique identifier for the comment.
        movie_id: Identifier of the movie associated with the comment.
        user_id: Identifier of the user who made the comment.
        created_at: Timestamp indicating when the comment was created.
        updated_at: Timestamp indicating the last update to the comment.
    """
    id: str
    movie_id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Properties to return via API with user information
class CommentWithUser(Comment):
    """
    Represents a comment with additional user information.

    This class extends the base Comment class by adding a user attribute. It
    can be used in scenarios where comment-related data is supplemented with
    specific user details, allowing for richer data handling and processing in
    comment-based models or functionality.

    Attributes:
        user: A dictionary containing user-related information. The content or
        structure of this dictionary can be customized based on specific use
        cases or data processing requirements.
    """
    user: dict

    model_config = ConfigDict(from_attributes=True)
