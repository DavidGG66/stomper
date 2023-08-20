import argparse
import pygame
from random import choice, randrange, random
from typing import Dict, Tuple
import sys

from common import (
    CYAN,
    MAX_WIDTH,
    MAX_HEIGHT,
    TILE_SIZE,
    ARC_LENGTH,
    ARC_WIDTH,
)
from node import Node



def screen_size(size):
    """
    the size of the screen given the number of columns and rows
    """
    pix_size = (TILE_SIZE * (size + 2)) + (ARC_LENGTH * (size - 1))
    return pix_size, pix_size


class GameState:
    """
    Keeps track of the state of the game

    screen: the pygame screen
    nodes: a map from (col, row) pairs to node objects
    player_loc:  a col, row pair indicating the node the player is on
    """

    def __init__(self, screen, nodes, player_loc):
        self.screen = screen
        self.nodes = nodes
        self.player_loc = player_loc
        

def init_nodes(size) -> Dict[Tuple[int, int], Node]:
    """
    Create the nodes and draw them on the screen
    """
    left_margin = TILE_SIZE
    top_margin = TILE_SIZE

    nodes = {}
    for x in range(size):
        left = left_margin + ((TILE_SIZE + ARC_LENGTH) * x)
        for y in range(size):
            top = top_margin + ((TILE_SIZE + ARC_LENGTH) * y)
            new_node = Node(left, top)
            nodes[(x, y)] = new_node
    return nodes


def init_pips(nodes, size, avg_pips):
    """
    Add initial pips to the nodes in the grid
    """
    pips_left = int(size * size * avg_pips)
    while pips_left > 0:
        pips_left -= 1
        available_nodes = [n for n in nodes.values() if n.pip_count < 13]
        node = choice(available_nodes)
        available_positions = [n for n in range(13) if not node.pips[n]]
        new_position = choice(available_positions)
        node.add_pip_at(new_position)


def init_net(screen, nodes, size, ctd_chance):
    """
    Set neighbors and make connections between the nodes
    """
    for x in range(size):
        for y in range(size):
            node = nodes[(x, y)]
            if x == 0:
                node.nbr["west"] = None
            if x < size - 1:
                node.nbr["east"] = nodes[(x + 1, y)]
                node.nbr["east"].nbr["west"] = node
                if random() <= ctd_chance:
                    node.connect_east(screen)
                else:
                    node.disconnect_east(screen)
            else:
                node.nbr["east"] = None
            if y == 0:
                node.nbr["north"] = None
            if y < size - 1:
                node.nbr["south"] = nodes[(x, y + 1)]
                node.nbr["south"].nbr["north"] = node
                if random() <= ctd_chance:
                    node.connect_south(screen)
                else:
                    node.disconnect_south(screen)
            else:
                node.nbr["south"] = None


def init_choices(nodes, size, bounce):
    """
    Set the spill choices list for each node:
    Four instances of each of this node's adjacent neighbors
    One instance each of this node's diagonal neighbors
    These neighbors will be selected from when scattering pips
    If the bounce option is off, the return list may contain False,
    which, if selected, means the pip falls off the board
    """
    for x in range(size):
        for y in range(size):
            node = nodes[(x, y)]
            if x < size - 1:
                node.spill_choices += [node.nbr["east"]] * 4
            elif not bounce:
                node.spill_choices += [False] * 4
            if x > 0:
                node.spill_choices += [node.nbr["west"]] * 4
            elif not bounce:
                node.spill_choices += [False] * 4
            if y < size - 1:
                node.spill_choices += [node.nbr["south"]] * 4
            elif not bounce:
                node.spill_choices += [False] * 4
            if y > 0:
                node.spill_choices += [node.nbr["north"]] * 4
            if x < size - 1 and y < size - 1:
                node.spill_choices += [node.nbr["east"].nbr["south"]]
            elif not bounce:
                node.spill_choices += [False]
            if x < size - 1 and y > 0:
                node.spill_choices += [node.nbr["east"].nbr["north"]]
            elif not bounce:
                node.spill_choices += [False]
            if x > 0 and y < size - 1:
                node.spill_choices += [node.nbr["west"].nbr["south"]]
            elif not bounce:
                node.spill_choices += [False]
            if x > 0 and y > 0:
                node.spill_choices += [node.nbr["west"].nbr["north"]]
            elif not bounce:
                node.spill_choices += [False]


def init_grid(screen, size, ctd_chance, avg_pips, bounce):
    """
    Initialize the playing grid
    """
    nodes = init_nodes(size)
    init_pips(nodes, size, avg_pips)
    init_net(screen, nodes, size, ctd_chance)
    init_choices(nodes, size, bounce)
    pygame.display.flip()
    return nodes


def set_player(node, args):
    """
    highlight this node and scatter its pips to its neighbors
    """
    if args.eat:
        node.remove_pips(1)
    choices = node.spill_choices
    for i in range(node.pip_count):
        neighbor = choice(choices)
        if neighbor:
            neighbor.add_pips(1)
    node.remove_all_pips()
    node.occupied = True


def render_nodes(nodes, screen):
    """
    """
    for node in nodes.values():
        node.render(screen)


def render_zone(nodes, pos, screen):
    """
    Render a node and its immediate neighbors
    """
    col, row = pos
    for c in range(col-1, col+2):
        for r in range(row-1, row+2):
            if (c, r) in nodes:
                nodes[(c, r)].render(screen)


def random_position(size):
    """
    choose a random position based on the size of the grid
    """
    col = choice(range(size))
    row = choice(range(size))
    return col, row


def init_game(args) -> GameState:
    """
    Set up the game using the arguments passed in
    """
    pygame.init()
    if args.size:
        size = args.size
    else:
        size = randrange(5) + 5
    screen = pygame.display.set_mode(screen_size(size))
    screen.fill(CYAN)

    nodes = init_grid(screen, size, args.ctd_chance, args.avg_pips, args.bounce)
    render_nodes(nodes, screen)
    player_loc = random_position(size)
    player_node = nodes[player_loc]
    set_player(player_node, args)
    render_nodes(nodes, screen)
    pygame.display.flip()
    return GameState(screen, nodes, player_loc)


def handle_keydown(key, game, args):
    """
    Handle a KEYDOWN event
    """
    options = {
        pygame.K_UP: ("north", 0, -1),
        pygame.K_DOWN: ("south", 0, 1),
        pygame.K_LEFT: ("west", -1, 0),
        pygame.K_RIGHT: ("east", 1, 0),
    }
    if key in options:
        dir, col_mod, row_mod = options[key]
        col, row = game.player_loc
        cur_node = game.nodes[game.player_loc]
        if cur_node.ctd[dir]:
            new_node = cur_node.nbr[dir]
            if new_node.pip_count > 0 or not args.needy:
                cur_node.occupied = False
                game.player_loc = (col + col_mod, row + row_mod)
                set_player(new_node, args)
                render_zone(game.nodes, game.player_loc, game.screen)
                pygame.display.flip()


def main(args) -> None:
    game = init_game(args)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                handle_keydown(event.key, game, args)
            if event.type == pygame.QUIT:
                running = False

parser = argparse.ArgumentParser()
parser.add_argument(
    "-s", "--size",
    type=int,
    help="the number of rows and columns",
)
parser.add_argument(
    "-b", "--bounce",
    action="store_true",
    help="pips won't spill over the edge",
)
parser.add_argument(
    "-e", "--eat",
    action="store_true",
    help="a pip is removed from the node the player lands on",
)
parser.add_argument(
    "-n", "--needy",
    action="store_true",
    help="player cannot move to an empty square"
)
parser.add_argument(
    "-sh", "--shifty",
    action="store_true",
    help="one connection is moved every turn"
)
parser.add_argument(
    "-p", "--avg_pips",
    type=int,
    default=5,
    help="the average number of pips per tile",
)
parser.add_argument(
    "-c", "--ctd_chance",
    type=float,
    default=0.5,
    help="the probability any two adjacent tiles will be connected",
)

args = parser.parse_args()


if __name__ == '__main__':
    sys.exit(main(args))
