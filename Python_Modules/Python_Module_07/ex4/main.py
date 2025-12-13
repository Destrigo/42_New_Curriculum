from .TournamentCard import TournamentCard
from .TournamentPlatform import TournamentPlatform


def main():
    print("=== DataDeck Tournament Platform ===")
    platform = TournamentPlatform()

    print("Registering Tournament Cards...")
    fire_dragon = TournamentCard("Fire Dragon", cost=5, rarity="Legendary",
                                 attack=7, health=5)
    ice_wizard = TournamentCard("Ice Wizard", cost=4, rarity="Epic",
                                attack=6, health=4)

    id1 = platform.register_card(fire_dragon)
    id2 = platform.register_card(ice_wizard)

    for cid in [id1, id2]:
        card = platform.cards[cid]
        print(f"{card.name} (ID: {cid}):")
        print("- Interfaces: [Card, Combatable, Rankable]")
        print(f"- Rating: {card.calculate_rating()}")
        print(f"- Record: {card.wins}-{card.losses}")

    print("Creating tournament match...")
    match_result = platform.create_match(id1, id2)
    print("Match result:", match_result)

    print("Tournament Leaderboard:")
    leaderboard = platform.get_leaderboard()
    for idx, entry in enumerate(leaderboard, 1):
        card = platform.cards[entry["id"]]
        print(f"{idx}. {card.name} - Rating: "
              f"{entry['rating']} ({card.wins}-{card.losses})")

    report = platform.generate_tournament_report()
    print("Platform Report:")
    print(report)
    print("=== Tournament Platform Successfully Deployed! ===")
    print("All abstract patterns working together harmoniously!")


if __name__ == "__main__":
    main()
