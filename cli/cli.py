from typing import List
from colorama import Fore

from poker.player import Player
from poker.table import Table


class CLI:
    def __init__(self, players: List[Player], table: Table, big_blind: int):
        self.players = players
        self.table = table
        self.big_blind = big_blind

    def get_rounds_number(self):
        print(f'Round: {self.table.rounds}')

    def get_role(self, player_num):
        if self.players[player_num].is_big_blind:
            return ' (BB)'
        if self.players[player_num].is_small_blind:
            return ' (SB)'
        return ''

    def get_action(self, player_num):
        player = self.players[player_num]

        while True:
            answer = input('Fold | Call | Raise ? \n-> ').lower()

            if answer == 'f' or answer == 'fold':
                player.action = 'Fold'
                break
            elif answer == 'c' or answer == 'call':
                player.action = 'Call'
                break
            elif answer == 'r' or answer == 'raise':
                if player.chips <= self.table.max_bet:
                    print('You can`t raise')
                else:
                    while True:
                        bet_chips = int(input('Bet: '))
                        if (self.table.max_bet <= bet_chips <= player.chips and bet_chips >= self.big_blind) or player.chips <= self.big_blind:
                            player.action = 'Raise'
                            player.raise_chips = bet_chips
                            break
                        else:
                            print('Incorrect value')
                    break
            else:
                print('Incorrect value')


    def get_betting_round_info(self, player_num):
        table_cards = [card.get_card() for card in self.table.dealt_community_cards]

        print('-' * 30)
        print(f'Table cards: {' '.join(table_cards)}')
        print(f'Pot: {self.table.pot}')
        print('-' * 30)

        for i in range(len(self.players)):
            if i != player_num:
                opponent = self.players[i]
                print(f'Player{opponent.uid}{self.get_role(i)}: {opponent.chips} Bet: {opponent.bet} {Fore.BLUE + opponent.action + Fore.RESET}')

        player = self.players[player_num]

        print('-' * 30)
        print(f'You{self.get_role(player_num)}: {player.chips} Bet: {player.bet}')
        print(f'[{player.cards[0].get_card()} {player.cards[1].get_card()}]')
        print('-' * 30)

    def get_end_round_info(self, winners):
        if len(winners) == 1:
            print(f'Round winner: Player{winners[0]}')
        else:
            winners_str = [f'Player{winner} ' for winner in winners]
            print('Round winners:', winners_str)

