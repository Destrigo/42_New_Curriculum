from ex4.TournamentCard import TournamentCard
from typing import Dict, List
import uuid


class TournamentPlatform:
    def __init__(self):
        self.cards: Dict[str, TournamentCard] = {}
        self.matches_played = 0

    def register_card(self, card: TournamentCard) -> str:
        card_id = f"{card.name.lower().replace(' ', '_')
                     }_{str(uuid.uuid4())[:8]}"
        self.cards[card_id] = card
        return card_id

    def create_match(self, card1_id: str, card2_id: str) -> Dict:
        card1 = self.cards[card1_id]
        card2 = self.cards[card2_id]

        if card1.attack >= card2.attack:
            winner, loser = (card1, card2)
        else:
            winner, loser = (card2, card1)
        winner.update_wins(1)
        loser.update_losses(1)
        self.matches_played += 1
        return {
            "winner": card1_id if winner == card1 else card2_id,
            "loser": card2_id if loser == card2 else card1_id,
            "winner_rating": winner.calculate_rating(),
            "loser_rating": loser.calculate_rating()
        }

    def get_leaderboard(self) -> List:
        return sorted(
            [{"id": cid,
              **card.get_rank_info()} for cid, card in self.cards.items()],
            key=lambda x: x["rating"],
            reverse=True
        )

    def generate_tournament_report(self) -> Dict:
        avg_rating = 0
        for card in self.cards.values():
            avg_rating += card.calculate_rating()
        avg_rating //= len(self.cards) if self.cards else 0
        return {
            "total_cards": len(self.cards),
            "matches_played": self.matches_played,
            "avg_rating": avg_rating,
            "platform_status": "active"
        }
