import json
import glob
import pandas as pd


# players metadata

print("Loading players.json...")

with open("/Dataset/players.json", "r", encoding="utf-8") as f:
    players = json.load(f)

# dictionary for statistics
player_stats = {}

for p in players:
    player_id = p["wyId"]

    player_stats[player_id] = {
        "playerId": player_id,
        "firstName": p["firstName"],
        "lastName": p["lastName"],
        "role": p["role"]["code2"],
        "birthDate": p["birthDate"],
        "currentTeamId": p["currentTeamId"],

        # init match stats
        "total_matches": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,

        # init event statistics
        "total_passes": 0,
        "completed_passes": 0,
        "goals": 0,
        "assists": 0,
        "fouls_committed": 0,
        "yellow_cards": 0,
        "red_cards": 0
    }

print(f"Loaded {len(player_stats)} players.")


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


match_files = glob.glob("/Dataset/matches/*.json")

# one competition at a time
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
                    # skip bad ids
                    continue

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

event_files = glob.glob("/Dataset/events/*.json")

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


# CSV EXPORT

print("Saving player_global_stats.csv...")

# table from our dictionary, rows = keys
df = pd.DataFrame.from_dict(player_stats, orient="index")
# most frequent players at the top
df.sort_values(by="total_matches", ascending=False, inplace=True)

df.to_csv("player_global_stats.csv", index=False)

print("File saved as player_global_stats.csv")
