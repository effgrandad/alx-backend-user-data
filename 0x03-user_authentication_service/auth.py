#!/usr/bin/env python3
"""
Auth module
"""
from db import DB
from user import User
from sqlalchemy.orm.exc import NoResultFound
import bcrypt
import uuid


def _hash_password(password: str) -> bytes:
    """
    Hashes a password string using bcrypt
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


def _generate_uuid() -> str:
    """
    Generate a new UUID
    """
    return str(uuid.uuid4())


class Auth:
    """
    Auth class to interact with the authentication database.
    """

    def __init__(self):
        self._db = DB()

    def register_user(self, email: str, password: str) -> User:
        """
        Register a new user
        """

        try:
            self._db.find_user_by(email=email)
            # return f"User {email} already exists"
            raise ValueError(f"User {email} already exists")
        except NoResultFound:
            pass

        hashed_password = _hash_password(password)

        user = self._db.add_user(email, hashed_password)
        return user

    def valid_login(self, email: str, password: str) -> bool:
        """
        Validate login credentials
        """

        try:
            user = self._db.find_user_by(email=email)
            return bcrypt.checkpw(password.encode('utf-8'),
                                  user.hashed_password)
        except NoResultFound:
            return False

    def create_session(self, email: str) -> str:
        """
        Create a session for the user
        """
        try:
            found_user = self._db.find_user_by(email=email)
        except NoResultFound:
            return None

        session_id = _generate_uuid()
        self._db.update_user(found_user.id, session_id=session_id)
        return session_id

    def get_user_from_session_id(self, session_id: str) -> User:
        """
        Retrieve user corresponding to a session ID
        """
        if session_id is None:
            return None

        try:
            return self._db.find_user_by(session_id=session_id)
        except NoResultFound:
            return None

    def destroy_session(self, user_id: int) -> None:
        """
        Destroy the session for the user
        """

        self._db.update_user(user_id, session_id=None)

    def get_reset_password_token(self, email: str) -> str:
        """
        Auth.get_reset_password_token method. Generate reset password token
        """
        user = self._db.find_user_by(email=email)
        if user is None:
            raise ValueError

        token = str(uuid.uuid4())
        user.reset_token = token
        self._db.commit()

        return token

    def update_password(self, reset_token: str, password: str) -> None:
        """
        Update user's password using reset_token
        """
        user = self._db.find_user_by(reset_token=reset_token)

        if not user:
            raise ValueError("Invalid reset token")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'),
                                        bcrypt.gensalt())

        user.hashed_password = hashed_password

        user.reset_token = None

        self._db.commit()
