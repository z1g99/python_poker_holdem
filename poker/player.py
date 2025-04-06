from typing import List
from poker.card import Card

class Player:
    def __init__(self, uid: int, initial_chips: int):
        self.uid = uid
        self.cards: List[Card] = []
        self.__kicker = 0
        self.best_hand: int = 0
        self.best_hand_score: List[int] = []
        self.chips: int = initial_chips
        self.bet: int = 0
        self.action: str = ''
        self.raise_chips: int = 0
        self.is_small_blind: bool = False
        self.is_big_blind: bool = False
        self.is_fold: bool = False

    def place_bet(self, bet_chips: int):
        self.chips -= bet_chips
        self.bet += bet_chips

    @property
    def kicker(self):
        return max([card.rank for card in self.cards])