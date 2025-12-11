from .SpellCard import SpellCard
from .ArtifactCard import ArtifactCard
from .Deck import Deck
from ..ex0.CreatureCard import CreatureCard


def main():
    print("=== DataDeck Deck Builder ===")
    print("Building deck with different card types...")

    deck = Deck()
    fire_dragon = CreatureCard("Fire Dragon", 5, "Legendary", 7, 5)
    lightning_bolt = SpellCard("Lightning Bolt", 3, "Rare", "damage")
    mana_crystal = ArtifactCard("Mana Crystal", 2, "Common", 3, "Permanent: +1 mana per turn")

    deck.add_card(fire_dragon)
    deck.add_card(lightning_bolt)
    deck.add_card(mana_crystal)

    stats = deck.get_deck_stats()
    print("Deck stats:", stats)

    print("Drawing and playing cards:")
    deck.shuffle()

    for i in range(3):
        card = deck.draw_card()
        print(f"Drew: {card.name} ({card.__class__.__name__.replace('Card', '')})")
        result = card.play({})
        print("Play result:", result)

    print("Polymorphism in action: Same interface, different card behaviors!")


if __name__ == "__main__":
    main()
