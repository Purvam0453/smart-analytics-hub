from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime

from database import Base




class User(Base):

    __tablename__ = "users"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    username = Column(
        String,
        unique=True,
        index=True
    )


    email = Column(
        String,
        unique=True,
        index=True
    )


    password = Column(
        String
    )






class LoginLog(Base):

    __tablename__ = "login_logs"


    id = Column(

        Integer,

        primary_key=True,

        index=True

    )


    user_id = Column(

        Integer,

        ForeignKey("users.id")

    )


    username = Column(

        String

    )


    login_time = Column(

        DateTime,

        default=datetime.utcnow

    )