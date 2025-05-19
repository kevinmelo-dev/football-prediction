from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    season = Column(String)
    utcDate = Column(DateTime)
    status = Column(String)
    matchday = Column(Integer)
    league_id = Column(Integer, ForeignKey("leagues.id"))  

    home_team_id = Column(Integer, ForeignKey("teams.id"))
    away_team_id = Column(Integer, ForeignKey("teams.id"))
    home_score = Column(Integer)
    away_score = Column(Integer)

    home_team = relationship("Team", foreign_keys=[home_team_id])
    away_team = relationship("Team", foreign_keys=[away_team_id])
    league = relationship("League", foreign_keys=[league_id]) 
