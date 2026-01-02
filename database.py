from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

from db.base import Base
from Models.NodeData import NodeData
from Models.Player import Player

DATABASE_URL = "sqlite:///data/graph_results.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(engine)

def add_statistic(playerId,scoreBetweenness,scorePageRank,scoreDegree)
    playerAlreadyPresent = session.query(
        exists().where(NodeData.playerId == playerId,)
    ).scalar()

    if playerAlreadyPresent:
        existingNode = session.query(NodeData).filter_by(playerId = playerId,).first()
        existingNode.games += 1
        existingNode.scoreBetweenness += scoreBetweenness
        existingNode.scorePageRank += scorePageRank
        existingNode.scoreDegree += scoreDegree
        session.commit()
    else
        newNode = NodeData
        (
            playerId = playerId,
            games = 1,
            scoreBetweenness = scoreBetweenness,
            scorePageRank = scorePageRank,
            scoreDegree = scoreDegree
        )
        session.add(newNode)
        session.commit()
