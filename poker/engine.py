import random
from typing import List

from poker.player import Player
from poker.table import Table
from poker.utils import find_matches


class GameEngine:
    def __init__(self, players: List[Player], table: Table, big_blind: int):
        self.players = players
        self.table = table
        self.big_blind = big_blind
        self.big_blind_num: int = 0

    def assign_random_blinds(self):
        self.big_blind_num = random.randint(0, len(self.players) - 1)
        self.players[self.big_blind_num].is_big_blind = True
        self.players[self.big_blind_num - 1].is_small_blind = True

    def move_blinds(self):
        self.players[self.big_blind_num].is_big_blind = False
        self.players[self.big_blind_num].is_small_blind = True

        self.players[self.big_blind_num - 1].is_small_blind = False

        self.big_blind_num += 1
        if self.big_blind_num >= len(self.players):
            self.big_blind_num = 0
        self.players[self.big_blind_num].is_big_blind = True

    def assign_blinds(self):
        if self.table.rounds == 1:
            self.assign_random_blinds()
        else:
            self.move_blinds()

    def players_move_orders(self, is_preflop: bool) -> List[int]:
        players_move_orders = []

        for i in range(len(self.players)):
            num = self.big_blind_num

            if is_preflop:
                num += i + 1
            else:
                if len(self.players) > 2:
                    num += i - 1
                else:
                    num += i

            if num >= len(self.players):
                num -= len(self.players)

            if self.players[num].chips > 0:
                players_move_orders.append(num)

        return players_move_orders

    def deal_private_cards(self):
        for i in range(len(self.players)):
            self.players[i].cards = self.table.private_cards[i]

    def deal_flop_cards(self):
        for i in range(3):
            self.table.dealt_community_cards.append(self.table.community_cards[i])

    def deal_turn_cards(self):
        self.table.dealt_community_cards.append(self.table.community_cards[3])

    def deal_river_cards(self):
        self.table.dealt_community_cards.append(self.table.community_cards[4])

    def place_forced_bet(self):
        for player in self.players:
            if player.is_big_blind: player.place_bet(self.big_blind)
            if player.is_small_blind: player.place_bet(self.big_blind // 2)
        self.table.max_bet = self.big_blind

    def perform_player_action(self, player_num: int):
        player = self.players[player_num]

        if player.action == 'Fold':
            player.is_active = False
            player.is_fold = True
        elif player.action == 'Call':
            if self.table.max_bet >= player.chips:
                player.place_bet(player.chips)
            else:
                player.place_bet(self.table.max_bet - player.bet)
        elif player.action == 'Raise':
            self.table.max_bet = player.raise_chips
            player.place_bet(player.raise_chips - player.bet)
            self.table.raise_player_num = player_num

    def betting_round(self, interface):
        players_with_chips = [player for player in self.players if player.chips != 0]
        if len(players_with_chips) > 1:
            while True:
                for player_num in self.players_move_orders(is_preflop=True):
                    if player_num == self.table.raise_player_num:
                        self.table.raise_player_num = None
                        break
                    interface.get_betting_round_info(player_num)
                    interface.get_action(player_num)
                    self.perform_player_action(player_num)

                if self.table.raise_player_num is None:
                    break

            for player in self.players:
                self.table.pot += player.bet
                player.bet = 0
                player.action = ''
                player.raise_chips = 0

            self.table.raise_player_num = None
            self.table.max_bet = 0

    def find_best_hand(self, player: Player):
        cards = self.table.community_cards + player.cards
        all_hands = {1: [player.kicker]}
        ranks = [card.rank for card in cards]

        # Поиск комбинаций повторения достоинства (пара, две пары, сет, каре)
        ranks_matches = find_matches(ranks)

        best_pair = 0
        best_second_pair = 0
        best_trip = 0

        for i in range(7):
            if ranks_matches[i] == 4:
                all_hands.update({8: ranks[i]})
            if ranks_matches[i] == 3:
                if ranks[i] > best_trip:
                    best_trip = ranks[i]
            if ranks_matches[i] == 2:
                if ranks[i] > best_pair:
                    best_second_pair = best_pair
                    best_pair = ranks[i]

            if best_pair != 0:
                all_hands.update({2: [best_pair]})
            if best_second_pair != 0:
                all_hands.update({3: [best_pair, best_second_pair]})
            if best_trip != 0:
                all_hands.update({4: [best_trip]})

        # Поиск стрита
        straight = []
        for i in ranks:
            if i == 14:
                i = 1
            for j in ranks:
                if i + 1 == j:
                    for k in ranks:
                        if j + 1 == k:
                            for l in ranks:
                                if k + 1 == l:
                                    for m in ranks:
                                        if l + 1 == m:
                                            straight.append(i)
        if straight:
            all_hands.update({5: [max(straight)]})

        # Поиск флэша
        suits = [card.suit for card in cards]
        suits_matches = find_matches(suits)
        flush_ranks = set()

        for i in range(7):
            if suits_matches[i] >= 5:
                flush_ranks.add(ranks[i])

        if flush_ranks:
            all_hands.update({6: list(reversed(list(flush_ranks)))})

        # Поиск комбинаций, которые являются сочетанием других комбинаций (стрит-флеш, фулл хаус)
        if 2 in all_hands.keys() and 4 in all_hands.keys():
            all_hands.update({7: [all_hands[4][0], all_hands[2][0]]})

        if 5 in all_hands.keys() and 6 in all_hands.keys():
            all_hands.update({9: [all_hands[5][0]]})

        max_hand = max(all_hands.keys())

        return max_hand, all_hands[max_hand]

    def compute_winners(self) -> List[int]:
        """Вычисление победителя"""
        players = [player for player in self.players if not player.is_fold]
        winners = []
        best_hand_in_game = 0
        max_score_hand = []
        max_kicker = 0

        for player in players:
            player.best_hand, player.best_hand_score = self.find_best_hand(player)
            if player.best_hand > best_hand_in_game:
                best_hand_in_game = player.best_hand
                max_score_hand = player.best_hand_score
                max_kicker = player.kicker
                winners.clear()
                winners.append(player.uid)
            elif player.best_hand == best_hand_in_game:
                for i in range(len(max_score_hand)):
                    if player.best_hand_score[i] > max_score_hand[i]:
                        max_score_hand = player.best_hand_score
                        max_kicker = player.kicker
                        winners.clear()
                        winners.append(player.uid)
                    elif player.best_hand_score[i] == max_score_hand[i]:
                        if player.best_hand == 2 or player.best_hand == 3 or player.best_hand == 4 or player.best_hand == 8:
                            if player.kicker > max_kicker:
                                max_kicker = player.kicker
                                winners.clear()
                                winners.append(player.uid)
                            elif player.kicker == max_kicker:
                                winners.append(player.uid)
                        else:
                            winners.append(player.uid)

        # Передача фишек из банка победителю / победителям
        for player in players:
            if player.uid in winners:
                player.chips += self.table.pot // len(winners)

        return winners

    def reset(self):
        for player in self.players:
            player.cards = []
            player.best_hand = 0
            player.best_hand_score = []
            player.is_fold = False

        self.table.cards_pool = []
        self.table.dealt_community_cards = []