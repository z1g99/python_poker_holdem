from typing import List
from random import randint

from poker.card import Card

class Table:
    def __init__(self, num_players):
        self.cards_pool: List[Card] = []
        self.__private_cards = []
        self.__community_cards = []
        self.dealt_community_cards: List[Card] = []
        self.num_players = num_players
        self.pot: int = 0
        self.rounds: int = 0
        self.max_bet: int = 0
        self.raise_player_num = None

    def generate_cards(self) -> None:
        """Генерирует карты"""
        cards = []
        num_cards = 5 + self.num_players * 2
        for _ in range(num_cards):
            while True:
                new_card = [randint(2, 14), randint(1, 4)]
                if not new_card in cards:
                    break
            cards.append(new_card)

        # Добавление карт в пул
        for i in range(num_cards):
            self.cards_pool.append(Card(cards[i][0], cards[i][1]))

    @property
    def private_cards(self) -> List[List[Card]]:
        cards = []
        count = 5
        for _ in range(self.num_players):
            player_cards = [self.cards_pool[count], self.cards_pool[count+1]]
            cards.append(player_cards)
            count += 2
        return cards

    @property
    def community_cards(self) -> List[Card]:
        cards = []
        for i in range(5):
            cards.append(self.cards_pool[i])
        return cards

    def reset(self) -> None:
        """Очищает переменные"""
        self.cards_pool = []
        self.dealt_community_cards = []