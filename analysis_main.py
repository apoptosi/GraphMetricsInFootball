import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# Load competition DB
def load_db(competition):
    db_path = f"Databases/Data_{competition}.db"
    conn = sqlite3.connect(db_path)

    players = pd.read_sql("SELECT * FROM players", conn)
    node_data = pd.read_sql("SELECT * FROM node_data", conn)

    conn.close()
    return players, node_data

# FILTER PLAYERS < 10 GAMES PLAYED
def filter_reliable_players(df, min_games=10):
    return df[df["games"] >= min_games].copy()


# MERGE AND NORMALIZE CENTRALITIES
def build_analysis_dataframe(players, node_data):
    df = node_data.merge(
        players,
        left_on="player_id",
        right_on="playerId",
        how="inner"
    )

    # normalize centralities per game
    df["avg_degree"] = df["score_degree"] / df["games"]
    df["avg_betweenness"] = df["score_betweenness"] / df["games"]
    df["avg_pagerank"] = df["score_pagerank"] / df["games"]

    return df


# PLAYER RANKINGS OVER A METRIC
def rank_players(df, metric, top_k=10):
    ranked = (
        df.sort_values(metric, ascending=False)
        [["firstName", "lastName", "role", metric, "games"]]
        .head(top_k)
    )

    print(f"\nTop {top_k} players by {metric}:")
    print(ranked.to_string(index=False))


# DEGREE CENTRALITY CONSISTENCY
def centrality_consistency(df, metric="avg_degree", min_games=20):
    filtered = df[df["games"] >= min_games]

    ranked = filtered.sort_values(
        by=metric,
        ascending=False
    )

    print("\nMost consistent players:")
    print(ranked[[
        "firstName", "lastName", "games", "avg_degree"
    ]].head(10).to_string(index=False))


# INDIVIDUAL RECOGNITION vs CENTRALITY
def recognition_vs_centrality(df, metric):
    df = df.copy()
    df["recognition"] = df["goals"] + df["assists"]

    corr = df[[metric, "recognition"]].corr(
        method="spearman"
    ).iloc[0, 1]

    print(
        f"Spearman correlation ({metric} vs recognition): {corr:.3f}"
    )


# TEAM SUCCESS vs CENTRALITY
def success_vs_centrality(df, metric):
    df = df.copy()
    df["win_rate"] = df["wins"] / df["total_matches"]

    corr = df[[metric, "win_rate"]].corr(
        method="spearman"
    ).iloc[0, 1]

    print(
        f"Spearman correlation ({metric} vs win rate): {corr:.3f}"
    )



# MAIN
def main():
    competition = "Italy"
    players, node_data = load_db(competition)

    df = build_analysis_dataframe(players, node_data)
    df = filter_reliable_players(df, min_games=10)
    
    rank_players(df, "avg_degree")
    rank_players(df, "avg_betweenness")
    rank_players(df, "avg_pagerank")

    # avg degree consistency 
    centrality_consistency(df, metric="avg_degree")  # higher games threshold (20)

    # correlations
    metrics = ["avg_degree", "avg_betweenness", "avg_pagerank"]
    print("\n--- Individual recognition vs centrality ---")
    for m in metrics:
        recognition_vs_centrality(df, m)

    print("\n--- Team success vs centrality ---")
    for m in metrics:
        success_vs_centrality(df, m)


if __name__ == "__main__":
    main()