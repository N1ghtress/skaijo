import numpy as np
from collections.abc import Sequence
from collections import OrderedDict
from error import UnimplementedError


# TODO: fix bug causing players not to have a final turn when they are before the player who reveal their hand in the turns
# TODO: Implement way to start with a game state (i.e.: specified deck, hands, revealed)
# TODO: Implement replay (in model, reset function)
# TODO: Parametrize hand shape/size
class SkaijoGame:
    """
    The skaijo model that manages the game state.
    """

    def __init__(self, seed: int = None):
        """
        A new game model.
        An optional seed offers replayability.
        """

        self.players = 0
        self.seed = (
            seed if seed is not None else np.random.randint(np.iinfo(np.int32).max)
        )
        self.hands = OrderedDict()
        self.deck = np.array([])
        self.listeners = []

    def __str__(self):
        s = 'Discard: %d\n' % self.deck[-1]

        for player in self.hands.keys():
            s += '{:<24}'.format(player)
        s += '\n'

        hands = [np.where(h['revealed'], h['card'], 'X') for h in self.hands.values()]
        for line in range(3):
            for hand in hands:
                s += '{:<24}'.format(str(hand.reshape((3, len(hand) // 3))[line]))
            s += '\n'

        return s

    def register_listener(self, listener: callable):
        self.listeners.append(listener)

    def remove_listener(self, listener: callable):
        self.listeners.remove(listener)

    def __notify(self, event_name: str, data):
        for listener in self.listeners:
            listener(event_name, data)

    def set_players(self, players: Sequence[str]):
        """
        Initialize hands with players names.
        """

        for player in players:
            self.hands[player] = np.array([])
        self.__notify('players', players)

    def init_deck(self):
        """
        Mutates deck into shuffled skaijo deck.
        """

        np.random.seed(self.seed)
        self.deck = np.array([i // 10 - 2 for i in range(150)], dtype=np.int8)
        self.deck[0:5] = np.zeros(5)
        np.random.shuffle(self.deck)
        self.__notify('init_deck', self.deck)

    def __deal(self, indeces):
        """
        Return cards at indeces from deck.
        Delete cards at indeces from deck.
        """

        cards = np.take(self.deck, indeces)
        self.deck = np.delete(self.deck, indeces)
        return cards

    def deal_hands(self):
        """
        Populate hands with cards
        """

        for player, hand in self.hands.items():
            self.hands[player] = np.full(
                12,
                self.__deal(np.arange(12)),
                dtype=[('card', int), ('revealed', bool)],
            )
            self.hands[player]['revealed'] = False

        self.__notify('deal_hands', self.hands)

    def __get_player_by(self, order_func: callable):
        """
        Returns player that has maximum value for order_func(player hand)
        """
        keys = list(self.hands.keys())
        index = np.argmax([order_func(c) for c in self.hands.values()])
        return keys[index]

    def sort_by_value_revealed(self):
        """
        Sorts players by most value revealed.
        """

        highest = self.__get_player_by(
            lambda x: np.sum(np.where(x['revealed'], x['card'], 0))
        )
        first = next(iter(self.hands))
        while first != highest:
            self.hands.move_to_end(first)
            first = next(iter(self.hands))

        self.__notify('player_order', (highest, self.hand_value(highest)))

    def draw(self):
        card = self.__deal(0)
        self.__notify('draw', card)
        return card

    def recover(self):
        card = self.__deal(-1)
        self.__notify('recover', card)
        return card

    def discard(self, card, notify=True):
        self.deck = np.append(self.deck, card)
        self.__notify('discard', card) if notify else None

    def swap(self, card, player, index):
        """
        Swap card card with given card in players hands.
        """

        discard = self.hands[player][index]['card']
        self.hands[player][index] = (card, True)
        self.discard(discard, notify=False)
        self.__notify('swap', (player, discard, card))
        self.column_check(player, index)

    def reveal(self, player, index):
        """
        Turn a player's card face up.
        """

        self.hands[player][index]['revealed'] = True
        self.__notify('reveal', (player, self.hands[player][index]['card'], index + 1))
        self.column_check(player, index)

    # TODO: Remove hard coded column size
    # TODO: BUGGED
    def column_check(self, player, index):
        """
        Checks for all same-value revealed cards in given player's card's column.
        If it is the case, set this column to 0 value cards.
        """
        hand = self.hands[player]
        col = np.arange(hand.size) % (hand.size // 3) == index % (hand.size // 3)
        if (
            hand[col]['revealed'].all()
            and (hand[col]['card'][0] == hand[col]['card']).all()
        ):
            self.hands[player] = np.delete(self.hands[player], col)
            self.__notify('column', (player, hand[col][0]['card']))
            self.discard(hand[col]['card'])

    def is_a_hand_revealed(self):
        """
        Whether a hand has all cards face up or not.
        """
        hands_revealed = [hand['revealed'].all() for _, hand in self.hands.items()]
        return np.array(hands_revealed).any()

    def reveal_hands(self):
        """
        Reveals every player's whole hand.
        """
        for hand in self.hands.values():
            hand[:]['revealed'] = True

        self.__notify('reveal_hands', self.hands)

    def leaderboard(self):
        hands = {p: int(np.sum(h['card'])) for p, h in self.hands.items()}
        leaderboard = sorted(hands.items(), key=lambda item: item[1])
        self.__notify('leaderboard', leaderboard)
        return leaderboard

    def hand_value(self, player: str, revealed=True):
        cards = np.where(self.hands[player]['revealed'], self.hands[player]['card'], 0)
        return cards.sum()


def main():
    a = SkaijoGame()
    a.set_players(['Victor', 'Juliette'])
    a.init_deck()
    a.deal_hands()
    print(a.leaderboard())


if __name__ == '__main__':
    main()
