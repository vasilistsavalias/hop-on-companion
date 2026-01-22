from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(String, default='user')
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    watchlist_items = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    saved_searches = relationship("SavedSearch", back_populates="user", cascade="all, delete-orphan")

class Watchlist(Base):
    __tablename__ = 'watchlist'

    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    project_id = Column(String, primary_key=True)
    added_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watchlist_items")

class SavedSearch(Base):
    __tablename__ = 'saved_searches'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False)
    filters = Column(Text, nullable=False) # JSON string of filters
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="saved_searches")
