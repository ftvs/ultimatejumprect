#!/usr/bin/env python
from __future__ import with_statement # might want to detect <2.6
import pygame

class Tilemap():
    def readmap(self, mapfilename):
        with open(mapfilename) as mapfile:
            return mapfile.readlines(1000)

    def __init__(self, mapwidth = 50, mapheight = 50,
                        tilewidth = 32, tileheight = 32, mapfile = 'map1.txt'):
        self.tilearray = [[None] * mapwidth] * mapheight
        self.tilewidth, self.tileheight = tilewidth, tileheight
        self.maplines = self.readmap(mapfile)
        # self.tiles = gentiles(self)

    # returns object in map at x, y screen coords
    def at(self, x, y):
        tileX = x / 32
        tileY = y / 32
        if tileX > len(self.maplines) or tileY > len(self.maplines[0]):
            return None
        else:
            # print("tilemap at: " +
                    # str(self.maplines[tileY][tileX]))
            return self.maplines[tileY][tileX]

    # return true if in collision with a tile, false otherwise
    # px_allowed_overlap is how many pixels the edge is allowed to overlap
    # with the tile
    def in_collision(self, rect, px_allowed_overlap = 1):
        # + 1 and - 1 to allow player to be "thinner" to squeeze between tiles
        fromcol = int((rect.left + px_allowed_overlap) / self.tilewidth)
        tocol = int((rect.right - px_allowed_overlap) / self.tilewidth)
        fromrow = int((rect.top + px_allowed_overlap) / self.tileheight)
        torow = int((rect.bottom - px_allowed_overlap) / self.tileheight)

        for row in range(fromrow, torow + px_allowed_overlap):
            for col in range(fromcol, tocol + px_allowed_overlap):
                if (row < len(self.maplines)
                        and col < len(self.maplines[0])
                        and self.maplines[row][col] == '1'):
                    return True

        return False

#    def gentiles(self):
#        tiles = []
#        for row in range(len(self.maplines)):
#            for col in self.maplines[row]:
#                if col == '1':
#                    tiles.append(pygame.Rect(
#                                row * self.tilewidth,   col * self.tileheight,
#                                self.tilewidth,         self.tileheight))
#        return tiles

    #def push(self, rect):


