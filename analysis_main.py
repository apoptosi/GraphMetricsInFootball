import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
from contextlib import contextmanager



# Print output to file Results/results_{competition}.txt
@contextmanager
def redirect_stdout_to_file(filepath):
    original_stdout = sys.stdout
    with open(filepath, "w", encoding="utf-8") as f:
        sys.stdout = f
        try:
            yield
        finally:
            sys.stdout = original_stdout



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

# ====================================================== CENTRALITIES ===========================================================

# MERGE AND NORMALIZE CENTRALITIES
def build_analysis_dataframe(players, node_data):
    # put same key type for merge
    players["playerId"] = players["playerId"].astype(int)
    node_data["player_id"] = node_data["player_id"].astype(int)

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


# PLAYER RANKINGS OVER A METRIC -> print top k results
def rank_players(df, metric, top_k=10):
    ranked = (
        df.sort_values(metric, ascending=False)
        [["firstName", "lastName", "role", metric, "games"]]
        .head(top_k)
    )

    print(f"\nTop {top_k} players by {metric}:")
    print(ranked.to_string(index=False))


# DEG CENTRALITY CONSISTENCY -> which players remain central while playing many matches
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


# INDIVIDUAL RECOGNITION vs CENTRALITY -> do more central players perform better too?
def recognition_vs_centrality(df, metric):
    df = df.copy()
    df["recognition"] = df["goals"] + df["assists"]

    corr = df[[metric, "recognition"]].corr(
        method="spearman"
    ).iloc[0, 1]

    print(
        f"Spearman correlation ({metric} vs recognition): {corr:.3f}"
    )


# TEAM SUCCESS vs CENTRALITY -> do players that are more central also belong to winning teams?
def success_vs_centrality(df, metric):
    df = df.copy()
    df["win_rate"] = df["wins"] / df["total_matches"]

    corr = df[[metric, "win_rate"]].corr(
        method="spearman"
    ).iloc[0, 1]

    print(
        f"Spearman correlation ({metric} vs win rate): {corr:.3f}"
    )



# ====================================================== GRAPHS ===========================================================
def plot_scatter(
    df,
    x_col,
    y_col,
    title,
    xlabel,
    ylabel,
    out_path
):
    plt.figure(figsize=(7, 5))
    plt.scatter(df[x_col], df[y_col], alpha=0.6)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_path)
    plt.close()


# RECOG vs CENTR PLOT
def plot_recognition_vs_centrality(df, competition):
    out_dir = f"Graphs/Graph_{competition}"
    os.makedirs(out_dir, exist_ok=True)

    df = df.copy()
    df["recognition"] = df["goals"] + df["assists"]

    metrics = {
        "avg_degree": "Average Degree Centrality",
        "avg_betweenness": "Average Betweenness Centrality",
        "avg_pagerank": "Average PageRank Centrality"
    }

    for metric, label in metrics.items():
        plot_scatter(
            df=df,
            x_col=metric,
            y_col="recognition",
            title=f"{competition}: Recognition vs {label}",
            xlabel=label,
            ylabel="Goals + Assists",
            out_path=f"{out_dir}/recognition_vs_{metric}.png"
        )

# TEAM SUCCESS vs CENTR PLOT
def plot_success_vs_centrality(df, competition):
    out_dir = f"Graphs/Graph_{competition}"
    os.makedirs(out_dir, exist_ok=True)

    df = df.copy()
    df["win_rate"] = df["wins"] / df["total_matches"]

    metrics = {
        "avg_degree": "Average Degree Centrality",
        "avg_betweenness": "Average Betweenness Centrality",
        "avg_pagerank": "Average PageRank Centrality"
    }

    for metric, label in metrics.items():
        plot_scatter(
            df=df,
            x_col=metric,
            y_col="win_rate",
            title=f"{competition}: Win Rate vs {label}",
            xlabel=label,
            ylabel="Win Rate",
            out_path=f"{out_dir}/success_vs_{metric}.png"
        )




# ======================================================= MAIN ==============================================================
def main():
    competition = "European_Championship"

    # output file
    output_path = f"Results/results_{competition}.txt"

    # FOR EU CUP AND WORLD CUP SET MIN GAMES TO 5, OR ELSE OUTPUT IS EMPTY

    players, node_data = load_db(competition)
    df = build_analysis_dataframe(players, node_data)
    df = filter_reliable_players(df, min_games=10)

    with redirect_stdout_to_file(output_path):    
        rank_players(df, "avg_degree")
        rank_players(df, "avg_betweenness")
        rank_players(df, "avg_pagerank")

        # avg degree consistency 
        centrality_consistency(df, metric="avg_degree", min_games=20)  # higher games threshold (20)

        # correlations
        metrics = ["avg_degree", "avg_betweenness", "avg_pagerank"]
        print("\n--- Individual recognition vs centrality ---")
        for m in metrics:
            recognition_vs_centrality(df, m)

        print("\n--- Team success vs centrality ---")
        for m in metrics:
            success_vs_centrality(df, m)

    print(f"Results written to {output_path}")

    # plots
    plot_recognition_vs_centrality(df, competition)
    plot_success_vs_centrality(df, competition)


if __name__ == "__main__":
    main()