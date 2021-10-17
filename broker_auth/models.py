from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32))
    password = Column(String(32))
    super = Column(Integer(), default=0)

    acl_users = relationship("ACL", back_populates="users")

class ACL(Base):
    __tablename__ = "acls"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String(64))
    username = Column(String(64))
    user_id = Column(Integer, ForeignKey("users.id"))
    rw = Column(Integer)


    users = relationship("User", back_populates="acl_users")