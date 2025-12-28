# -------------------------------------
#
# The program uses panda and networkx if you don't have them preinstalled run
# python -m pip install networkx
# python -m pip install pandas
# python -m pip install c
#
#--------------------------------------

import json
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


MATCH_ID = 2575959

#load data from a match using panda

with open("events_Italy.json", "r", encoding="utf-8") as f:
    data = json.load(f)
df = pd.DataFrame(data)
# Keep only this match
df = df[df["matchId"] == MATCH_ID]
# filter only one team 
df = df[df["teamId"] == 3158]
# Keep only pass events
passes = df[df["eventName"] == "Pass"]




# build a network using networkx
G = nx.DiGraph()
print(len(passes))
for i in range(len(passes) - 2):
    passer = passes.iloc[i]["playerId"]
    receiver = passes.iloc[i + 1]["playerId"]

    if G.has_edge(passer, receiver):
        G[passer][receiver]["weight"] += 1
    else:
        G.add_edge(passer, receiver, weight=1)


plt.figure(figsize=(8, 8))
pos = nx.spring_layout(G, seed=42)

nx.draw(
    G, pos,
    with_labels=True,
    node_size=1500,
    node_color="lightblue",
    arrows=True
)

nx.draw_networkx_edge_labels(
    G, pos,
    edge_labels=nx.get_edge_attributes(G, "weight")
)

plt.title("Simple Passing Network (Test)")
plt.show()