from sqlalchemy import Column, Integer, String
from models.base import Base

class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    shortName = Column(String)
    tla = Column(String)
    crest = Column(String)
