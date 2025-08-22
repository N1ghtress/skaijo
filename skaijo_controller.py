import numpy as np
from collections.abc import Sequence
from collections import OrderedDict
from skaijo_model import SkaijoGame
from error import UnimplementedError


class SkaijoTerminalController:
    """
    Allow management of game state via terminal.
    """

    def __init__(self, model: SkaijoGame):
        self.model: SkaijoGame = model
        self.players: OrderedDict = OrderedDict()
        self.listeners: Sequence = []

    def ask(self, prompt: str, valids: Sequence, type: type):
        """
        Ask players for input.
        """
        wrong_answer = True
        full_prompt = (
            '%s (%s): ' % (prompt, valids) if valids is not None else '%s: ' % (prompt)
        )
        error_prompt = 'Please enter valid answer (%s)' % (valids)
        while wrong_answer:
            try:
                print(full_prompt, end='')
                x = type(input())
                wrong_answer = x not in valids if valids is not None else False
                if wrong_answer:
                    raise ValueError(x)
            except ValueError:
                print(error_prompt)
        return x

    def __ask_players(self):
        prompt = 'Enter player count'
        valids = np.arange(2, 9)
        players = []
        for i in range(self.ask(prompt, valids, int)):
            prompt = 'Enter name for player %d' % (i + 1)
            players.append(self.ask(prompt, None, str))

        return players

    def play(self):
        players = self.__ask_players()
        self.model.set_players(players)

        for player in players:
            self.players[player] = SkaijoTerminalPlayerController(
                self.model, self, player
            )

        self.model.init_deck()
        self.model.deal_hands()

        for player in self.model.hands.keys():
            player_con = self.players[player]
            player_con.reveal()
            player_con.reveal()

        self.model.sort_by_value_revealed()
        while not self.model.is_a_hand_revealed():
            for player in self.model.hands.keys():
                player_con = self.players[player]
                if player_con.draw_or_recover() == 'd':
                    card = player_con.draw()
                    if player_con.discard_or_swap() == 'd':
                        player_con.discard(card)
                        player_con.reveal()
                    else:
                        player_con.swap(card)
                else:
                    card = player_con.recover()
                    player_con.swap(card)

        self.model.reveal_hands()
        self.model.leaderboard()


class SkaijoTerminalPlayerController:
    """
    Manages player actions via terminal.
    """

    def __init__(self, model: SkaijoGame, controller, name: str):
        self.model: SkaijoGame = model
        self.controller = controller
        self.name: str = name

    def reveal(self):
        prompt = '%s, select which card to reveal ' % self.name
        # + 1 and - 1 to prevent confusing humans
        valids = (
            np.array(
                np.logical_not(self.model.hands[self.name]['revealed']).nonzero()
            ).flatten()
            + 1
        )
        index = self.controller.ask(prompt, valids, int) - 1
        self.model.reveal(self.name, index)

    def draw(self):
        return self.model.draw()

    def recover(self):
        return self.model.recover()

    def discard(self, card):
        self.model.discard(card)

    def swap(self, card):
        prompt = '%s, select which card to swap with %d' % (self.name, card)
        # + 1 and - 1 to prevent confusing humans
        valids = np.arange(self.model.hands[self.name].size) + 1
        index = self.controller.ask(prompt, valids, int) - 1
        self.model.swap(card, self.name, index)

    def draw_or_recover(self):
        prompt = '%s, choose between draw and recover' % self.name
        valids = ['d', 'r']
        return self.controller.ask(prompt, valids, str)

    def discard_or_swap(self):
        prompt = '%s, choose between discard and swap' % self.name
        valids = ['d', 's']
        return self.controller.ask(prompt, valids, str)
