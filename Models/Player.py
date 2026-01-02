from sqlalchemy import Column, String, Integer
from db.base import Base

class Player(Base):
    __tablename__ = "players"

    playerId = Column(String, primary_key=True)
    firstName = Column(String)
    lastName = Column(String)
    role = Column(String)
    birthDate = Column(String)
    currentTeamId = Column(String)

    total_matches = Column(Integer)
    wins = Column(Integer)
    draws = Column(Integer)
    losses = Column(Integer)

    total_passes = Column(Integer)
    completed_passes = Column(Integer)
    goals = Column(Integer)
    assists = Column(Integer)
    fouls_committed = Column(Integer)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
