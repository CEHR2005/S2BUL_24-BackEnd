from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

# Shared properties
class UserBase(BaseModel):
    """
    Represents a foundational data model for user information.

    This class serves as a base for defining core user attributes to facilitate
    user-related operations or validation. It utilizes Pydantic BaseModel to
    leverage data validation and type enforcement. The class can be extended
    for more specific user-related use cases or additional fields.

    Attributes:
        username: str
            The unique username of the user.
        email: EmailStr
            The email address of the user, validated to be a proper email format.
        first_name: Optional[str]
            The first name of the user. Defaults to None if not provided.
        last_name: Optional[str]
            The last name of the user. Defaults to None if not provided.
        age: Optional[int]
            The age of the user in years. Defaults to None if not provided.
        gender: Optional[str]
            The gender of the user. Defaults to None if not provided.
        country: Optional[str]
            The country of residence of the user. Defaults to None if not provided.
        continent: Optional[str]
            The continent of residence of the user. Defaults to None if not provided.
    """
    username: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    continent: Optional[str] = None

# Properties to receive via API on creation
class UserCreate(UserBase):
    """
    User creation data model with password validation.

    Represents a user creation data model that extends the base user model
    with an additional password field. Provides validation to ensure the
    password meets specific criteria.

    Attributes:
        password (str): The user's password. Must be at least 8 characters
        long.

    Methods:
        password_min_length: Validates that the provided password meets the
        minimum length requirement.
    """
    password: str

    @field_validator('password', mode='before')
    def password_min_length(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

# Properties to receive via API on update
class UserUpdate(BaseModel):
    """
    Represents a model for updating user information.

    This class serves as a data structure for updating user details in an
    application. It inherits from `BaseModel` and allows flexible updates to
    specific user information while keeping other fields unchanged. All attributes
    are optional, enabling partial updates.

    Attributes:
        username: User's username.
        first_name: User's first name.
        last_name: User's last name.
        age: User's age.
        gender: User's gender.
        country: User's country.
        continent: User's continent.
    """
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    continent: Optional[str] = None

# Properties to return via API
class User(UserBase):
    """
    Represents a user entity with attributes for identification, permissions,
    and timestamps.

    This class encapsulates the properties of a user, including a unique
    identifier, administrative privileges, and timestamps for creation and
    updates. It extends functionality from the UserBase and is designed for use
    in applications requiring user management.

    Attributes:
        id: A unique identifier for the user.
        is_admin: Indicates whether the user has administrative privileges.
        created_at: The timestamp when the user was created.
        updated_at: The timestamp when the user was last updated.
    """
    id: str
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# Properties to return via API for login
class UserLogin(BaseModel):
    """
    Represents the login credentials for a user.

    This class is used to validate and store the necessary credentials for a user
    to log in. It ensures the email is in a valid format and provides a container
    for the password.
    """
    email: EmailStr
    password: str

# Token schema
class Token(BaseModel):
    """
    Represents a token typically used for authentication or authorization.

    The Token class is designed to model authentication or authorization tokens,
    including the access token and token type. It can be used to manage, validate, or
    transfer token-related information within an application.
    """
    access_token: str
    token_type: str

# Token payload
class TokenPayload(BaseModel):
    """
    Represents the payload of a token.

    This class serves as a data model for token payloads used in authentication or
    authorization contexts. It inherits from BaseModel to ensure compatibility with
    data validation and serialization mechanisms. The primary attribute `sub`
    indicates the subject or identifier associated with the token payload.

    Attributes:
        sub: An optional string indicating the subject or identifier associated
             with the token payload. It may be None if no subject is specified.
             Typically used to identify the token's ownership or purpose.
    """
    sub: Optional[str] = None
