import pygame
from random import choice, shuffle

from common import (
    BLACK,
    CYAN,
    RED,
    WHITE,
    TILE_SIZE,
    TILE_BORDER_WIDTH,
    TILE_MARGIN,
    PIP_RADIUS,
)


def pip_rect(pos):
    """
    Given a pip position, return the rect where it should
    be drawn
    """
    offset = TILE_BORDER_WIDTH + TILE_MARGIN
    space = (TILE_SIZE - offset * 2) / 5
    
    if pos < 3:
        left = pos * space * 2 + offset
        top = offset
    elif pos < 5:
        left = (pos - 3) * space * 2 + offset + space
        top = offset + space
    elif pos < 8:
        left = (pos - 5) * space * 2 + offset
        top = offset + space * 2
    elif pos < 10:
        left = (pos - 8) * space * 2 + offset + space
        top = offset + space * 3
    else:
        left = (pos - 10) * space * 2 + offset
        top = offset + space * 4
    return pygame.Rect(left, top, space, space)


# A node is a square on the playing area. Nodes are adjacent
# to other nodes, and are connected to some of their adjacent
# nodes
#
# They include:
#
# surface:     A Surface object showing what the node looks like
# rect:        The node's location on the screen
# pip_count:   The number of pips on this node
# pips:        pips[n] == True if the nth position holds a pip
#
# nbr:         nbr["north"] == the node to the north of this one, etc
# ctd:         ctd["north"] == True if this node is connected to its north neighbor, etc

class Node:

    def __init__(self, left, top):
        self.rect = pygame.Rect(left, top, TILE_SIZE, TILE_SIZE)
        self.surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.pip_count = 0
        self.pips = [False] * 13
        self.occupied = False
        self.nbr = {}
        self.ctd = {}
        for dir in ["north", "south", "west", "east"]:
            self.nbr[dir] = None
            self.ctd[dir] = False
        self.spill_choices = []

    def add_pip_at(self, pos):
        """
        Add a pip to the node at a given position
        Assumes there is not already a pip there
        """
        self.pip_count += 1
        self.pips[pos] = True

    def remove_pip_at(self, pos):
        """
        Remove a pip from the node at a given position if it exists
        """
        if self.pips[pos]:
            self.pip_count -= 1
        self.pips[pos] = False

    def add_pips(self, qty):
        """
        Add a quantity of pips to a node
        """
        to_add = qty
        while self.pip_count < 13 and to_add > 0:
            to_add -= 1
            available = [n for n in range(13) if not self.pips[n]]
            new_pos = choice(available)
            self.add_pip_at(new_pos)

    def remove_pips(self, qty):
        """
        Remove a quantity of pips from a node
        """
        order = list(range(13))
        shuffle(order)
        left = qty
        while self.pip_count > 0 and left > 0 and order:
            pos = order.pop()
            if self.pips[pos]:
                self.remove_pip_at(pos)
                left -= 1

    def remove_all_pips(self):
        """
        Remove all the pips from a node
        """
        for pos in range(13):
            self.remove_pip_at(pos)

    def connect_east(self, screen):
        """
        Connect this node and its east adjacent node
        """
        self.ctd["east"] = True
        self.nbr["east"].ctd["west"] = True
        source = self.rect.midright
        dest = self.nbr["east"].rect.midleft
        pygame.draw.line(screen, BLACK, source, dest, width = TILE_BORDER_WIDTH)

    def disconnect_east(self, screen):
        """
        Disconnect this node and its east adjacent node
        """
        self.ctd["east"] = False
        self.nbr["east"].ctd["west"] = False
        source = self.rect.midright
        dest = self.nbr["east"].rect.midleft
        pygame.draw.line(screen, CYAN, source, dest, width = TILE_BORDER_WIDTH)

    def connect_south(self, screen):
        """
        Connect this node and its south adjacent node
        """
        self.ctd["south"] = True
        self.nbr["south"].ctd["north"] = True
        source = self.rect.midbottom
        dest = self.nbr["south"].rect.midtop
        pygame.draw.line(screen, BLACK, source, dest, width = TILE_BORDER_WIDTH)

    def disconnect_south(self, screen):
        """
        Disconnect this node and its south adjacent node
        """
        self.ctd["south"] = False
        self.nbr["south"].ctd["north"] = False
        source = self.rect.midbottom
        dest = self.nbr["south"].rect.midtop
        pygame.draw.line(screen, CYAN, source, dest, width = TILE_BORDER_WIDTH)

    def render(self, screen):
        """
        Draw the node, its outline and its pips
        """
        node_rect = pygame.Rect(0, 0, TILE_SIZE, TILE_SIZE)
        pygame.draw.rect(self.surface, WHITE, node_rect)
        pygame.draw.rect(self.surface, BLACK, node_rect, width = TILE_BORDER_WIDTH)
        for pos in range(13):
            if self.pips[pos]:
                prect = pip_rect(pos)
                pygame.draw.circle(self.surface, BLACK, prect.center, PIP_RADIUS)
        if self.occupied:
            pygame.draw.circle(self.surface, RED, node_rect.center, PIP_RADIUS * 5)
        screen.blit(self.surface, self.rect)        
