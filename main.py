import json
import os

# import the graph statistics function
# from match_to_graphStats import compute_match_graph_stats

DATASET_PATH = "RawData/matches"

# ================================== SINGLE MATCH STATISTICS ==============================================

# Load matches for a given competition (Italy, England, etc.)
def load_matches_for_competition(competition: str):
    file_path = os.path.join(DATASET_PATH, f"matches_{competition}.json")

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
    
    print("Select competition:")
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

        team_a = teams[team_ids[0]]["teamName"]
        team_b = teams[team_ids[1]]["teamName"]

        score_a = teams[team_ids[0]]["score"]
        score_b = teams[team_ids[1]]["score"]

        print(f"[{i}] {team_a} vs {team_b} ({score_a}-{score_b})")

        while True:
            choice = input("\nSelect match index: ")

            if choice.isdigit() and 0 <= int(choice) < len(matches):
                return matches[int(choice)]
            else:
                print("Invalid index, try again.")


def main():
    print("Select analysis mode:")
    print("1) Match statistics")
    print("2) Season statistics (not implemented yet)")

    mode = input("> ")

    if mode == "1":
        competition = choose_competition()
        matches = load_matches_for_competition(competition)
        match = choose_match(matches)

        match_id = match["wyId"]

        print(f"\nRunning match statistics for matchId={match_id} ({competition})")

        # Call graph/statistics computation
        # compute_match_graph_stats(match_id=match_id, competition=competition)

    elif mode == "2":
        print("Season statistics not implemented yet.")

    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()