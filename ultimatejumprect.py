#!/bin/python

# Tested and implemented on Python 2.5.4 and Pygame 1.9.1
from __future__ import with_statement # might want to detect <2.6
import sys
import os
import pygame
import random
#import threading
from pygame.locals import *

import tilemap
if not pygame.font: print('warning, fonts disabled')
if not pygame.mixer: print('warning, sound disabled')

#! /usr/bin/env python

def ableToJump():
     if (playerRect.left < 3  # wall jumps
            or playerRect.right > SCRWIDTH - 3
            or playerRect.bottom > SCRHEIGHT - 2):
         # might need px perfect collision first, depends on implementation
         return True
     else:
         return False

SCRWIDTH, SCRHEIGHT = 640, 480

clock = pygame.time.Clock()
fpslimit = 60 # fps limit

class Player:
    def __init__(self, size = 5, startcoords = 460, prevCoord = 5, speed = 0):
        self.RECTLEFT = self.RECTTOP = startcoords
        self.RECTWIDTH = self.RECTHEIGHT = 5
        self.playerRect = pygame.Rect(self.RECTLEFT, self.RECTTOP,
                                        self.RECTWIDTH, self.RECTHEIGHT) 
        self.prevLeft = self.prevTop = 5  # prev coords. used for collisions
        self.movementspeed = speed
        self.playerXspeed = self.playerYspeed = 0
        self.jumping = False # True while rising from jump

        # airborne is better than jumped because its state depends solely on
        # player position rather than an abstract game concept
        self.airborne = (False if self.bottom > SCRHEIGHT else True)

        # how long i've been rising from the jump. gotta stop rising from jump
        # eventually
        self.jumpframes = 0

    def update(self):
        #__________________________________________________________
        #
        # Wall/ground/ceiling collision
        #__________________________________________________________
        #
        # check wall collision, move back inside if needed
        if self.playerRect.top < 0:
            self.playerRect.top = 1
        elif self.playerRect.bottom > SCRHEIGHT:
            self.playerRect.top = SCRHEIGHT - RECTHEIGHT
            self.airborne = False  # reset jumped since i've hit the ground


# player Rect coords, dimensions
#===================================

RECTLEFT = RECTTOP = RECTWIDTH = RECTHEIGHT = 32
playerRect = pygame.Rect(RECTLEFT, RECTTOP, RECTWIDTH, RECTHEIGHT) 
blockcolor = (255, 0, 0) # red
playercolor = (255, 255, 255) # white
goalcolor = (0, 0, 255) # blue

prevLeft = prevTop = 5  # hold prev coords. used for collisions
playerXspeed = playerYspeed = 0
jumping = False # True while rising from jump
jumped = False  # indicate already jumped, prevent infinite jumps
jumpframes = 0  # how long i've jumped. gotta stop rising from jump eventually

# controls
#====================
JUMP = K_k
LEFT = K_s
RIGHT = K_f
DOWN = K_d

tilemap = tilemap.Tilemap()
solidtiles = []

for i, row in enumerate(tilemap.maplines):
    for j, col in enumerate(tilemap.maplines[i]):
        if col == '1':
            block = pygame.Rect(j * tilemap.tilewidth, i * tilemap.tileheight, 
                                tilemap.tilewidth,       tilemap.tileheight)
            solidtiles.append(block)

# array of numbers to test with goal rect moving.
goalRectPositions = []

random.seed(1)

for i in range(5):
    maxX = SCRWIDTH / RECTWIDTH - 2
    maxY = SCRHEIGHT / RECTHEIGHT - 2

    newGoalX, newGoalY = random.randint(1, maxX), random.randint(1, maxY)

    # always check if legal
    while tilemap.at(newGoalX * RECTWIDTH,
                     newGoalY * RECTHEIGHT) == "1":
        print("rejected: " + str(newGoalX) + ", " + str(newGoalY))
        newGoalX = random.randint(1, maxX)
        newGoalY = random.randint(1, maxY)

    goalRectPositions.append((newGoalX, newGoalY))

goalRect = pygame.Rect( RECTWIDTH*newGoalX, RECTHEIGHT*newGoalY,
                        RECTWIDTH, RECTHEIGHT) 
goalRectPosTried = 0;
goalRectPosIndexToTry = goalRectPosTried;

#print(str(playerRect.top))
#print(str(playerRect.left))

screen = pygame.display.set_mode((SCRWIDTH, SCRHEIGHT))

# game state constants
STATE_PAUSE = 0
STATE_GAME_IN_PROGRESS = 1

# gameloop
#============
frames = 0
running = True
while running:
    # event = pygame.event.poll()
    for event in pygame.event.get():
        # pygame.event.clear()
        if event.type == pygame.QUIT:
            running = False
        # elif event.type == pygame.MOUSEMOTION:
            # print "mouse at (%d, %d)" % event.pos
        # elif event.type == pygame.MOUSEBUTTONDOWN:
            # print "mouse at (%d, %d)" % event.pos # DEBUG
        #______________________________________________________________________
        #
        # Key events and control
        #______________________________________________________________________
        #
        elif event.type == KEYDOWN:
            # print "key pressed: " + str(event.key) # ??? # DEBUG
            if event.key == K_ESCAPE:
                running = False

            if event.key == LEFT:
                # print "a pressed, leftspeed +" # DEBUG
                playerXspeed += -5 # playerRect.move_ip(-5, 0)
            if event.key == RIGHT:
                # print "d pressed, rightspeed +" # DEBUG
                playerXspeed += 5
                # playerRect.move_ip(5, 0)

            # jump. the Gravity section prevents jump craziness. collision
            # section resets the jumped variable to allow jumping again
            if event.key == JUMP and ((not jumped) or ableToJump()):
                # print "w pressed, upspeed +" # DEBUG
                jumping = True
                jumpframes = 0
                playerYspeed = -10
            if event.key == DOWN:
                # print "s pressed, downspeed +" # DEBUG
                playerYspeed += 5

        if event.type == KEYUP:
            # print "key released: " + str(event.key) # ??? # DEBUG
            if event.key == LEFT:
                # print "a released, leftspeed -" # DEBUG
                playerXspeed += 5 # playerRect.move_ip(-5, 0)
            if event.key == RIGHT:
                # print "d released, rightspeed -" # DEBUG
                playerXspeed += -5
            if event.key == JUMP:
                # print "w released, upspeed -" # DEBUG
                jumping = False
                jumpframes = 0
            if event.key == DOWN:
                # print "s released, downspeed -" # DEBUG
                playerYspeed += -5

    # regardless of whether or not i jumped. it should become false again
    # within this loop if i'm in contact with something.
    jumped = True

    if jumping:
        jumpframes += 1

    #__________________________________________________________
    #
    # Gravity
    #__________________________________________________________
    # gravity if i've jumped too long
    # no gravity during jump or if too fast
    if (playerYspeed < 3 and not jumping) or jumpframes > 10:
        playerYspeed += 1 # gravity
        jumpframes = 0
        jumping = False
        # print('gravity!') # DEBUG

    #__________________________________________________________
    #
    # Tile collision
    #__________________________________________________________
    #
    playerRect.move_ip(0, playerYspeed) # move based on speed
    if tilemap.in_collision(playerRect): # Y axis collision
        if playerYspeed > 0: # came from top
            playerRect.top = int((playerRect.top)
                                / tilemap.tileheight) * tilemap.tileheight
            jumped = False
        elif playerYspeed < 0: # came from bottom
            playerRect.top = int((playerRect.top + tilemap.tileheight)
                                / tilemap.tileheight) * tilemap.tileheight
            # jumped = False    # this would be interesting ceiling jumping

    playerRect.move_ip(playerXspeed, 0) # move based on speed
    if tilemap.in_collision(playerRect): # X axis collision
        if playerXspeed > 0: # came from left
            playerRect.left = int((playerRect.left)
                                / tilemap.tilewidth) * tilemap.tilewidth
            jumped = False
        elif playerXspeed < 0: # came from right
            playerRect.left = int((playerRect.left + tilemap.tilewidth)
                                / tilemap.tilewidth) * tilemap.tilewidth
            jumped = False

    #__________________________________________________________
    #
    # Wall/ground/ceiling collision
    #__________________________________________________________
    #
    # check wall collision, move back inside if needed
    if playerRect.top < 0:
        playerRect.top = 0
    elif playerRect.bottom > SCRHEIGHT:
        playerRect.top = SCRHEIGHT - RECTHEIGHT
        jumped = False  # reset jumped since i've hit the ground

    # left/right boundaries
    if playerRect.left < 0:
        playerRect.left = -1
    if playerRect.right > SCRWIDTH:
        playerRect.left = SCRWIDTH - playerRect.width - 1
    prevTop = playerRect.top
    prevLeft = playerRect.left

    # hit goal, create new goal
    if playerRect.colliderect(goalRect):
        maxX = SCRWIDTH / RECTWIDTH - 2
        maxY = SCRHEIGHT / RECTHEIGHT - 2

        newGoalX, newGoalY = (goalRectPositions[goalRectPosIndexToTry][0],
                                goalRectPositions[goalRectPosIndexToTry][1])
        goalRectPosTried = goalRectPosTried + 1
        goalRectPosIndexToTry = goalRectPosTried % len(goalRectPositions)
        print("Goals hit: " + str(goalRectPosTried) +
                ". Goal array index: " + str(goalRectPosIndexToTry))

        goalRect.topleft = (RECTWIDTH * newGoalX,
                            RECTHEIGHT * newGoalY)
        # print("newgoalx, newgoaly: " + str(newGoalX) + " " + str(newGoalY))
        # print("maxX, maxY: " + str(maxX) + " " + str(maxY))
        # print("new goalRect.topleft: " + str(goalRect.topleft))

    # redraw whole screen
    screen.fill((0, 0, 0))
    for eachtile in solidtiles:
        screen.fill(blockcolor, eachtile)
    #pygame.draw.rect(screen, (255, 0, 0), collisionbox)
    pygame.draw.rect(screen, playercolor, playerRect)
    pygame.draw.rect(screen, goalcolor, goalRect)
    pygame.display.flip()

    clock.tick(fpslimit)

    frames += 1
    if frames > 60:
        pygame.display.set_caption(str(clock.get_fps()) + ' fps')
        frames = 0

# be idle friendly
pygame.quit()

    # K_a           a
    # K_b           b
    # K_c           c
    # K_d           d
    # K_e           e
    # K_f           f
    # K_g           g
    # K_h           h
    # K_i           i
    # K_j           j
# http://eli.thegreenplace.net/2008/12/13/writing-a-game-in-python-with-pygame-part-i/
# http://lorenzod8n.wordpress.com/2007/05/25/pygame-tutorial-1-getting-started/
# http://en.wordpress.com/tag/pygame-tutorial/
# locals has commonly used constants / functions
# import for convenience, so that the func / constants are in global

