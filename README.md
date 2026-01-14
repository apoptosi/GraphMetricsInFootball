# GraphMetricsInFootball

## Project Motivation
When watching football, it often appears that certain players dominate the game, acting as central points for passes in most of the actions. Therefore, they should be valued as more important than others.
To properly assess this, we need a reliable and quantifiable measure: we aim to examine whether a player’s centrality in a team’s passing network - along with, if necessary, other measures - correlates with match outcome and individual performance.


## Project structure
```
GraphMetricsInFootball/
│
├── Data/                      # Extracted raw data (events, matches, players, teams)
├── Databases/                 # SQLite databases (one per competition)
│   ├── Data_Italy.db
│   ├── Data_England.db
│   ├── ...
│
├── Models/                    # SQLAlchemy models
│   ├── Base.py
│   ├── Player.py
│   └── NodeData.py
│
├── Results/                   # Analysis outputs
│   ├── results_Italy.txt
│   ├── results_France.txt
│   └── ...
│
├── Graphs/                    # Saved plots
│
├── extractRawData.cmd         # Script to extract raw JSON data
├── database.py                # Database utilities
├── match_to_graphStats.py     # Per-match graph construction and centrality computation
├── player_table_loader.py     # Player statistics loader
├── main.py                    # Interactive computation of graph metrics
├── analysis_main.py           # Player-level analysis
├── analysis_graph_level.py    # Graph-level (team) analysis
└── README.md
```
