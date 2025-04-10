from cli.cli import CLI
from poker.engine import GameEngine
from poker.player import Player
from poker.table import Table

def run_poker(num_players, initial_chips, big_blind):
    players = [Player(i + 1, initial_chips) for i in range(num_players)]
    table = Table(len(players))
    engine = GameEngine(players, table, big_blind)
    cli = CLI(players, table, big_blind)

    while True:
        for i in range(len(players)):
            if players[i].chips == 0:
                del players[i]

        if len(players) == 1:
            print(f'Player{players[0].uid} won!')
            break

        table.rounds += 1
        table.generate_cards()
        cli.print_rounds_number()
        engine.assign_blinds()

        # Префлоп
        engine.deal_private_cards()
        engine.place_forced_bets()
        engine.betting_round(is_preflop=True, interface=cli)

        # Флоп
        engine.deal_flop_cards()
        engine.betting_round(is_preflop=False,interface=cli)

        # Терн
        engine.deal_turn_cards()
        engine.betting_round(is_preflop=False,interface=cli)

        # Ривер
        engine.deal_river_cards()
        engine.betting_round(is_preflop=False,interface=cli)

        # Конец игры
        winners = engine.compute_winners()
        cli.print_end_round(winners)
        engine.reset()

if __name__ == '__main__':
    run_poker(num_players=2, initial_chips=10_000, big_blind=100)