import json
import os
import random
import networkx as nx
import pandas as pd


DATA_PATH = "Data"
RESULTS_PATH = "Results"

N_MATCHES = 15   # small sample of matches

COMPETITIONS = [
    "Italy",
    "England",
    "Spain",
    "France",
    "Germany",
    "World_Cup",
    "European_Championship"
]


def build_team_graph(events, match_id, team_id):
    # Build directed weighted passing graph for one team in one match
    df = pd.DataFrame(events)

    df = df[
        (df["matchId"] == match_id) &
        (df["teamId"] == team_id) &
        (df["eventName"] == "Pass")
    ]

    G = nx.DiGraph()

    for i in range(len(df) - 1):
        passer = df.iloc[i]["playerId"]
        receiver = df.iloc[i + 1]["playerId"]

        if G.has_edge(passer, receiver):
            G[passer][receiver]["weight"] += 1
        else:
            G.add_edge(passer, receiver, weight=1)

    return G


def graph_metrics(G):
    # Compute graph-level metrics
    if G.number_of_nodes() < 2:
        return None, None

    density = nx.density(G)

    # clustering works on undirected graphs
    clustering = nx.average_clustering(
        G.to_undirected(),
        weight="weight"
    )

    return density, clustering


def main():
    os.makedirs(RESULTS_PATH, exist_ok=True)

    output_path = f"{RESULTS_PATH}/graph_level_summary.txt"

    with open(output_path, "w", encoding="utf-8") as out:

        for competition in COMPETITIONS:
            print(f"Processing {competition}...")

            # Load data
            with open(f"{DATA_PATH}/events/events_{competition}.json", encoding="utf-8") as f:
                events = json.load(f)

            with open(f"{DATA_PATH}/matches/matches_{competition}.json", encoding="utf-8") as f:
                matches = json.load(f)

            sampled_matches = random.sample(
                matches,
                min(N_MATCHES, len(matches))
            )

            densities = []
            clusterings = []

            for match in sampled_matches:
                match_id = match["wyId"]
                teams = list(match["teamsData"].keys())

                for team_id in teams:
                    G = build_team_graph(events, match_id, int(team_id))
                    density, clustering = graph_metrics(G)

                    if density is not None:
                        densities.append(density)
                        clusterings.append(clustering)

            avg_density = sum(densities) / len(densities)
            avg_clustering = sum(clusterings) / len(clusterings)

            out.write(f"Competition: {competition}\n")
            out.write(f"Matches sampled: {len(sampled_matches)}\n")
            out.write(f"Average network density: {avg_density:.4f}\n")
            out.write(f"Average clustering coefficient: {avg_clustering:.4f}\n\n")

    print(f"Graph-level summary written to {output_path}")



if __name__ == "__main__":
    main()
