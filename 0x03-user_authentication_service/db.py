#!/usr/bin/env python3

"""
DB module
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound

from user import (User, Base)


class DB:
    """
    DB class
    """

    def __init__(self) -> None:
        """
        commence a new DB instance
        """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self) -> Session:
        """
        Memoized session object
        """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """"
        Add a user to the session for persistene
        Args:
            email (str): user email
            hashed_pwd (str): Hashed password
        Returns:
            returns the user object
        """
        # session = Session(bind=self._engine)
        user_creds = {
            "email": email,
            "hashed_password": hashed_password
        }
        user = User(**user_creds)
        # user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user

    def find_user_by(self, **filters) -> User:
        """
        Query for a user, filter the response and return
        The first object
        Args:
            filters (dict): filters to use when filtering
        Returns:
            returns an object of the User class
        Raises:
            Raises NoResultFound if no result is found
            InvalidRequestError otherwise
        """
        if filters:
            user = self._session.query(User).filter_by(**filters).first()
            if user:
                return user
            raise NoResultFound
        raise InvalidRequestError

    def update_user(self, user_id: int, **kwargs) -> None:
        """
        Update a user
        Args:
            user_id (int): The user to update
            kwargs (dict): New user properties
        Returns:
            Returns None (expclicity)
        """
        search_params = {
            "id": user_id
        }
        user = self.find_user_by(id=user_id)
        if user is None:
            return
        update_source = {}
        for key, value in kwargs.items():
            if hasattr(User, key):
                update_source[getattr(User, key)] = value
            else:
                raise ValueError()
        self._session.query(User).filter(User.id == user_id).update(
            update_source,
            synchronize_session=False,
        )
        self._session.commit()