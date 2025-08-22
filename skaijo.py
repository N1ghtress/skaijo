#!/usr/bin/python3

# TODO: Add some other type of players...
# TODO: Implement way to start with a game state (i.e.: specified deck, hands, revealed)
# TODO: Add unit tests
# TODO: Display seed at game begin
# TODO: Implement SkaijoFileView

import skaijo_model
import skaijo_view
import skaijo_controller
from time import strftime, localtime


def main():
    model = skaijo_model.SkaijoGame()
    termview = skaijo_view.SkaijoTerminalView(model)
    fileview = skaijo_view.SkaijoFileView(
        model, f'replay/skaijo_{strftime("%Y_%m_%d_%H:%M:%S", localtime())}.replay'
    )
    controller = skaijo_controller.SkaijoTerminalController(model)
    controller.play()


if __name__ == '__main__':
    main()
