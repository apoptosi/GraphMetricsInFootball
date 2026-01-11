from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from Models.NodeData import NodeData
from Models.Player import Player
from Models.Base import Base


def init_db(database_url):
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)


def add_graph_statistic(
    database_url,
    player_id,
    score_betweenness,
    score_pagerank,
    score_degree
):
    init_db(database_url=database_url)

    engine = create_engine(database_url, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        player_already_present = session.query(
            exists().where(NodeData.player_id == int(player_id))
        ).scalar()

        if player_already_present:
            existing_node = (
                session.query(NodeData)
                .filter_by(player_id=int(player_id))
                .first()
            )

            existing_node.games += 1
            existing_node.score_betweenness += score_betweenness
            existing_node.score_pagerank += score_pagerank
            existing_node.score_degree += score_degree

        else:
            new_node = NodeData(
                player_id=int(player_id),
                games=1,
                score_betweenness=score_betweenness,
                score_pagerank=score_pagerank,
                score_degree=score_degree
            )
            session.add(new_node)

        session.commit()
        
    except Exception as e:
        # Catch any  unexpected error
        print(f"Unexpected error: {e}")
        session.rollback()

    finally:
        session.close()