# This file is part of Mindscape. <>
# Mindscape is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. Mindscape is distributed in the hope that it
# will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details. You should have received a
# copy of the GNU General Public License along with Mindscape. If not, see
# <https://www.gnu.org/licenses/>.

from checkers import Checkers


# The main loop for the game. When there is a winner, we break out
def main():
    game = Checkers()
    while True:
        if game.print_winner():
            break
        # Realize one game step at a time
        game.game_step()


main()
