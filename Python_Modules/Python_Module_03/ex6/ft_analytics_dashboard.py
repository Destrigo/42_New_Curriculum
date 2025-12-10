if __name__ == "__main__":
    """first try"""
    print("=== Game Analytics Dashboard ===")
    print("")

    players = ["alice", "bob", "charlie", "diana"]
    scores = [2300, 1800, 2150, 2050]
    achievements = {
        "alice": ["first_kill", "level_10", "boss_slayer",
                  "quest_complete", "treasure_hunter"],
        "bob": ["first_kill", "level_5", "quest_complete"],
        "charlie": ["first_kill", "level_10", "boss_slayer",
                    "quest_complete", "treasure_hunter",
                    "arena_champion", "speed_run"],
        "diana": ["first_kill", "level_8", "quest_complete"]
    }
    active = {
        "alice": True,
        "bob": True,
        "charlie": True,
        "diana": False
    }
    regions = ["north", "east", "central", "north"]

    print("=== List Comprehension Examples ===")
    high_scorers = [players[i]
                    for i in range(len(players)) if scores[i] > 2000]
    print("High scorers (>2000):", high_scorers)

    scores_doubled = [scores[i] * 2 for i in range(len(scores))]
    print("Scores doubled:", scores_doubled)

    active_players = [p for p in players if active.get(p, []) is True]
    print("Active players:", active_players)

    print("")
    print("=== Dict Comprehension Examples ===")
    player_scores = {players[i]: scores[i] for i in range(len(players))}
    print("Player scores:", player_scores)

    score_categories = {
        "high": len([s for s in scores if s > 2000]),
        "medium": len([s for s in scores if 2000 >= s >= 1900]),
        "low": len([s for s in scores if s < 1900])
    }
    print("Score categories:", score_categories)

    achievement_counts = {p: len(achievements.get(p, [])) for p in players}
    print("Achievement counts:", achievement_counts)

    print("")
    print("=== Set Comprehension Examples ===")
    unique_players = {p for p in players}
    print("Unique players:", unique_players)

    unique_achievements = set({ach for p in players
                               for ach in achievements.get(p, [])})
    print(f"Unique achievements: {unique_achievements}")

    unique_regions = set(regions)
    print(f"Active regions: {unique_regions}")

    print("")
    print("=== Combined Analysis ===")
    total_players = len(players)
    total_unique_achievements = len(unique_achievements)
    average_score = sum(scores) / len(scores)

    max_score = scores[0]
    top_index = 0
    i = 1
    while i < len(scores):
        if scores[i] > max_score:
            max_score = scores[i]
            top_index = i
        i += 1
    top_performer = players[top_index]
    top_achievements = len(achievements.get(top_performer, []))

    print(f"Total players: {total_players}")
    print(f"Total unique achievements: {total_unique_achievements}")
    print(f"Average score: {average_score}")
    print(f"Top performer: {top_performer} "
          f"({max_score} points, {top_achievements} achievements)")
