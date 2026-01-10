import json
import os

# import the graph statistics function
from match_to_graphStats import match_to_graphStats

# The path to the json is the one specify in the 
# estractRawData.cmd file

MATCHES_DIRECTORY_PATH = "Data/matches/"
EVENTS_DIRECTORY_PATH = "Data/Events/"
TEAMS_PATH = "Data/Teams/teams.json"
PLAYERS_PATH = "Data/Players/players.json"

# ================================== LOAD TEAMS METADATA =============================================

with open(TEAMS_PATH, "r", encoding="utf-8") as f:
    teams_metadata = json.load(f)

# Map: teamId (string) -> team name
TEAM_ID_TO_NAME = {
    str(team["wyId"]): team["name"]
    for team in teams_metadata
}



# ================================== SINGLE MATCH STATISTICS ==============================================

# Load matches for a given competition (Italy, England, etc.)
def load_matches_for_competition(competition: str):
    file_path = os.path.join(MATCHES_DIRECTORY_PATH, f"matches_{competition}.json")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"No matches file found for {competition}")

    with open(file_path, "r", encoding="utf-8") as f:
        matches = json.load(f)

    return matches

# Ask user which competition he wants to see matches from
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
    
    print("\nSelect competition:")
    for i, comp in enumerate(competitions):
        print(f"{i}) {comp}")

    while True:
        choice = input("> ")

        if choice.isdigit() and 0 <= int(choice) < len(competitions):
            return competitions[int(choice)]
        else:
            print("Invalid choice, try again.")


# Choose a match inside the chosen competition
def choose_match(matches):
    print("\nAvailable matches:")

    for i, match in enumerate(matches):
        teams = match["teamsData"]
        team_ids = list(teams.keys())

        team_a_id = team_ids[0]
        team_b_id = team_ids[1]

        team_a = TEAM_ID_TO_NAME.get(team_a_id, f"Team {team_a_id}")
        team_b = TEAM_ID_TO_NAME.get(team_b_id, f"Team {team_b_id}")

        score_a = teams[team_a_id]["score"]
        score_b = teams[team_b_id]["score"]

        print(f"[{i}] {team_a} vs {team_b} ({score_a}-{score_b})")

    while True:
        choice = input("\nSelect match index: ")

        if choice.isdigit() and 0 <= int(choice) < len(matches):
            return matches[int(choice)]
        else:
            print("Invalid index, try again.")


def main():
    print("\nSelect analysis mode:")
    print("1) Match statistics")
    print("2) Season statistics (not implemented yet)")

    mode = input("> ")

    if mode == "1":
        competition = choose_competition()
        matches = load_matches_for_competition(competition)
        match = choose_match(matches)

        match_id = match["wyId"]

        print(f"\nRunning match statistics for matchId={match_id} ({competition})")

        # Covert each team stats to graphs compute and save the stats
        file_path = os.path.join(EVENTS_DIRECTORY_PATH, f"events_{competition}.json")
        database_url = f"sqlite:///Databases/Data_{competition}_{match_id}.db"
        teams = match["teamsData"]
        team_ids = list(teams.keys())
        team_a_id = team_ids[0]
        team_b_id = team_ids[1]

        match_to_graphStats(json_path=file_path, match_id=match_id , team_id = team_a_id ,database_url = database_url)
        match_to_graphStats(json_path=file_path, match_id=match_id , team_id = team_b_id ,database_url = database_url)

        

    elif mode == "2":
        print("Season statistics not implemented yet.")

    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()