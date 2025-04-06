class Card:
    def __init__(self, rank: int, suit: int):
        self.rank = rank # int [2; 14]
        self.suit = suit # int [1; 4]

    def get_card(self):
        rank_char =  {
            2: '2',
            3: '3',
            4: '4',
            5: '5',
            6: '6',
            7: '7',
            8: '8',
            9: '9',
            10: '10',
            11: 'J',
            12: 'Q',
            13: 'K',
            14: 'A',
        }[self.rank]

        suit_char = {
            1: '♧',
            2: '♤',
            3: '♥',
            4: '♦',
        }[self.suit]

        return rank_char + suit_char