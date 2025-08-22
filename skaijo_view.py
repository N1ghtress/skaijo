import os

class SkaijoTerminalView:
    """
    Displays skaijo game states to the terminal.
    """

    def __init__(self, model):
        self.model = model
        model.register_listener(self.__model_event)

    def __model_event(self, event_name, data):
        if event_name == 'players':
            print('Players are : %s' % data)
        elif event_name == 'init_deck':
            print('Deck has been shuffled, let the columns roar !')
        elif event_name == 'deal_hands':
            print('Hands have been dealt, fortune favors the bold...')
            self.display_game()
        elif event_name == 'player_order':
            print('%s starts as they have the highest score of %d !' % data)
            self.display_game()
        elif event_name == 'draw':
            print('%d is drawn.' % data)
        elif event_name == 'recover':
            print('%d is recovered.' % data)
        elif event_name == 'discard':
            print(f'{data} is discarded.')
            self.display_game()
        elif event_name == 'swap':
            print('%s swaps their %d with a %d.' % data)
            self.display_game()
        elif event_name == 'reveal':
            print('%s reveals their %d in position %d.' % data)
            self.display_game()
        elif event_name == 'column':
            print('%s has a column of %d !' % data)
            self.display_game()
        elif event_name == 'reveal_hands':
            print('Game is over, let the hands be revealed !')
            self.display_game()
        elif event_name == 'leaderboard':
            print('Leaderboard:\n%s' % data)

    def display_game(self):
        print(self.model)


class SkaijoFileView:
    """
    Displays skaijo game states to the terminal.
    """

    def __init__(self, model, filepath):
        self.model = model
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.file = open(filepath, 'w')
        model.register_listener(self.__model_event)

    def __model_event(self, event_name, data):
        if event_name == 'players':
            self.file.write('Players are : %s\n' % data)
        elif event_name == 'init_deck':
            self.file.write('Deck has been shuffled.\n')
        elif event_name == 'deal_hands':
            self.file.write('Hands have been dealt.\n')
        elif event_name == 'player_order':
            self.file.write('%s starts as they have the highest score of %d !\n' % data)
        elif event_name == 'draw':
            self.file.write('%d is drawn.\n' % data)
        elif event_name == 'recover':
            self.file.write('%d is recovered.\n' % data)
        elif event_name == 'discard':
            self.file.write(f'{data} is discarded.\n')
        elif event_name == 'swap':
            self.file.write('%s swaps their %d with a %d.\n' % data)
        elif event_name == 'reveal':
            self.file.write('%s reveals their %d in position %d.\n' % data)
        elif event_name == 'column':
            self.file.write('%s has a column of %d!\n' % data)
        elif event_name == 'reveal_hands':
            self.file.write('Game is over, hands are revealed.\n')
        elif event_name == 'leaderboard':
            self.file.write('Leaderboard:\n%s\n' % data)
