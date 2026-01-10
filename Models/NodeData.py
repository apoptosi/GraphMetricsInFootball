from sqlalchemy import Column, String, Float , Integer
from Models.Base import Base

class NodeData(Base):
    __tablename__ = "node_data"

    player_id            = Column(Integer, primary_key=True)
    games                = Column(Integer)
    score_betweenness    = Column(Float)
    score_pagerank       = Column(Float)
    score_degree         = Column(Float)
