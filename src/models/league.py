from sqlalchemy import Column, Integer, String
from models.base import Base

class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    country = Column(String)
    emblem = Column(String)
