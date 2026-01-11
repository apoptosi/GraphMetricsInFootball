import json

# sql lite
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Models.Base import Base
from Models.Player import Player


# SELECT COMPETITION TO LOAD PLAYERS FOR
def choose_competition():
    competitions = [
        "Italy",
        "England",
        "Spain",
        "France",
        "Germany",
        "World_Cup",
        "European_Championship"
    ]

    print("\nSelect competition to load players from:")
    for i, comp in enumerate(competitions):
        print(f"{i}) {comp}")

    while True:
        choice = input("> ")
        if choice.isdigit() and 0 <= int(choice) < len(competitions):
            return competitions[int(choice)]
        else:
            print("Invalid choice, try again.")

COMPETITION = choose_competition()

DATABASE_URL = f"sqlite:///Databases/Data_{COMPETITION}.db"


# DB session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

Base.metadata.create_all(engine)


# players metadata

print("Loading players.json...")

BASE_PATH = "Data"

with open(f"{BASE_PATH}/players.json") as f:
    players = json.load(f)

# dictionary for statistics
player_stats = {}

print("Initialized empty player table for competition:", COMPETITION)


# match files

print("Processing matches files...")

# helper to log winner
def match_result(team_score, opponent_score):
    if team_score > opponent_score:
        return "win"
    elif team_score < opponent_score:
        return "loss"
    else:
        return "draw"

# Lookup dictionary
PLAYERS_BY_ID = {p["wyId"]: p for p in players}


match_files = [f"Data/matches/matches_{COMPETITION}.json"]

# add new players to the table and record wins/losses
for file_path in match_files:
    print(f"  Reading {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:

        matches = json.load(f)

    for match in matches:
        teams_data = match["teamsData"]

        # read the two teams playing this match
        team_ids = list(teams_data.keys())
        team_a = team_ids[0]
        team_b = team_ids[1]

        score_a = teams_data[team_a]["score"]
        score_b = teams_data[team_b]["score"]

        # twice to update both teams results
        result_a = match_result(score_a, score_b)
        result_b = match_result(score_b, score_a)

        for team_id, result in [(team_a, result_a), (team_b, result_b)]:
            formation = teams_data[team_id]["formation"]

            # loop through formation and bench
            players_in_match = formation["lineup"] + formation["bench"]

            for player in players_in_match:
                pid = player["playerId"]

                if pid not in player_stats:
                    # first time we see this player in this competition
                    p = PLAYERS_BY_ID.get(pid)
                    if p is None:
                        continue

                    team_id = p["currentTeamId"]

                    player_stats[pid] = {
                        "playerId": pid,
                        "firstName": p["firstName"],
                        "lastName": p["lastName"],
                        "role": p["role"]["code2"],
                        "birthDate": p["birthDate"],
                        "currentTeamId": team_id,

                        "total_matches": 0,
                        "wins": 0,
                        "draws": 0,
                        "losses": 0,

                        "total_passes": 0,
                        "completed_passes": 0,
                        "goals": 0,
                        "assists": 0,
                        "fouls_committed": 0,
                        "yellow_cards": 0,
                        "red_cards": 0
                    }

                player_stats[pid]["total_matches"] += 1

                if result == "win":
                    player_stats[pid]["wins"] += 1
                elif result == "loss":
                    player_stats[pid]["losses"] += 1
                else:
                    player_stats[pid]["draws"] += 1



# WYSCOUT TAG-ID LIST:  https://dataglossary.wyscout.com/
# used for sub event types (shot->goal? pass->completed?)
# event files
print("Processing events files...")

event_files = [f"Data/events/events_{COMPETITION}.json"]

for file_path in event_files:
    print(f"  Reading {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        events = json.load(f)

    # no need to consider match id, we only care for global player stats
    for event in events:
        # event = single action in some match
        player_id = event.get("playerId")

        if player_id not in player_stats:
            # bad id
            continue
        
        # read if it was pass shot foul etc
        event_name = event.get("eventName", "")
        # faster event type check
        # same event can have multiple tag properties
        tags = {tag["id"] for tag in event.get("tags", [])}

        # passes (any kind)
        if event_name == "Pass":
            player_stats[player_id]["total_passes"] += 1

            if 1801 in tags:   
                # accurate pass
                player_stats[player_id]["completed_passes"] += 1

            if 301 in tags:
                # pass is also an assist
                player_stats[player_id]["assists"] += 1

        # goals
        elif event_name == "Shot":
            if 101 in tags:    
                # shot was also a goal
                player_stats[player_id]["goals"] += 1

        # fouls
        elif event_name == "Foul":
            player_stats[player_id]["fouls_committed"] += 1

        # cards
        if 1702 in tags:      
            # yellow card
            player_stats[player_id]["yellow_cards"] += 1

        if 1701 in tags or 1703 in tags:      
            # red card
            player_stats[player_id]["red_cards"] += 1

# DB EXPORT
for pid, stats in player_stats.items():
    player = Player(
        playerId=stats["playerId"],
        firstName=stats["firstName"],
        lastName=stats["lastName"],
        role=stats["role"],
        birthDate=stats["birthDate"],
        currentTeamId=stats["currentTeamId"],

        total_matches=stats["total_matches"],
        wins=stats["wins"],
        draws=stats["draws"],
        losses=stats["losses"],

        total_passes=stats["total_passes"],
        completed_passes=stats["completed_passes"],
        goals=stats["goals"],
        assists=stats["assists"],
        fouls_committed=stats["fouls_committed"],
        yellow_cards=stats["yellow_cards"],
        red_cards=stats["red_cards"],
    )

    # avoids duplicate keys
    session.merge(player)

session.commit()