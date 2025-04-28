import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime

from app.database.database import Base
from app.database.custom_types import GUID

class User(Base):
    """
    Represents a user entity within the system, storing personal, authentication,
    and administrative information for account management.

    This class serves as the database model for users, managing essential personal
    attributes such as name, age, and contact information, as well as system-specific
    details like administrative privileges, account creation, and update timestamps.
    It supports integration with authentication mechanisms and permission control
    by storing encrypted passwords and admin status.

    Attributes:
        __tablename__ (str): The name of the database table used to store user data.
        id (GUID): The unique identifier for the user, automatically generated.
        username (str): A unique username for identifying the user.
        email (str): The email address of the user, unique for each account.
        password (str): The encrypted password for the user's account.
        first_name (str): The first name of the user, optional.
        last_name (str): The last name of the user, optional.
        age (int): The age of the user, optional.
        gender (str): The gender of the user, optional.
        country (str): The country of residence of the user, optional.
        continent (str): The continent of residence of the user, optional.
        is_admin (bool): Boolean indicating if the user holds administrative privileges.
        created_at (datetime): The timestamp when the user account was created.
        updated_at (datetime): The timestamp of the last update to the user account.
    """
    __tablename__ = "users"

    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String, nullable=True)
    country = Column(String, nullable=True)
    continent = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
