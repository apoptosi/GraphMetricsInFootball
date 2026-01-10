import json
import pandas as pd
import networkx as nx

from database import add_graph_statistic


def match_to_graphStats(
    json_path,
    match_id,
    team_id,
    database_url
):
    # load json from file
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)

    # Filter data we only need passes to compute the statistics
    df = df[df["matchId"] == int(match_id)]
    df = df[df["teamId"] == int(team_id)]
    passes = df[df["eventName"] == "Pass"]

    # Build graph
    G = nx.DiGraph()
    for i in range(len(passes) - 1):
        passer = passes.iloc[i]["playerId"]
        receiver = passes.iloc[i + 1]["playerId"]

        if G.has_edge(passer, receiver):
            G[passer][receiver]["weight"] += 1
        else:
            G.add_edge(passer, receiver, weight=1)

    # Extract metrics
    betweenness = nx.betweenness_centrality(G, weight="weight")
    pagerank = nx.pagerank(G, weight="weight")
    degree = dict(G.degree(weight="weight"))

    # Store Mach metrics in DB for future use
    for player_id in G.nodes():
        add_graph_statistic(
            database_url=database_url,
            player_id=player_id,
            score_betweenness=betweenness.get(player_id, 0.0),
            score_pagerank=pagerank.get(player_id, 0.0),
            score_degree=degree.get(player_id, 0.0)
        )