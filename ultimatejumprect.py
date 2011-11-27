#!/bin/python

# Tested and implemented on Python 2.5.4 and Pygame 1.9.1
from __future__ import with_statement # might want to detect <2.6
import sys
import os
import pygame
#import threading
from pygame.locals import *

import tilemap
if not pygame.font: print('warning, fonts disabled')
if not pygame.mixer: print('warning, sound disabled')

#! /usr/bin/env python

#def ableToJump():
#    if (playerRect.left < 1  # wall jumps
#        or playerRect.right > SCRWIDTH - 1):
        # might need px perfect collision first, depends on implementation

SCRWIDTH, SCRHEIGHT = 640, 480

##class PlayerRect(Rect):
##    def __init__(self):
##        Rect.__init__(self)
##        # self.rect = pygame.Rect(5, 5, 5, 5)
##        self.top, self.left, self.bottom, self.right = 5, 5, 5, 5
##        self.prevLeft = 5
##        self.prevTop = 5
##
##    def wallCollide(self):
##        if self.top < 0 or self.bottom > SCRWIDTH:
##            self.top = self.prevTop
##
##        if self.left < 0 or self.right > SCRHEIGHT:
##            self.left = self.prevLeft

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
blockcolor = (255, 0, 0)
playercolor = (255, 255, 255)

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

# test collision box
#====================
#collisionbox = pygame.Rect(400, 400, 100, 100)
tilemap = tilemap.Tilemap()
solidtiles = []

for i, row in enumerate(tilemap.maplines):
    for j, col in enumerate(tilemap.maplines[i]):
        if col == '1':
            block = pygame.Rect(j * tilemap.tilewidth, i * tilemap.tileheight, 
                                tilemap.tilewidth,       tilemap.tileheight)
            solidtiles.append(block)


print(str(playerRect.top))
print(str(playerRect.left))

screen = pygame.display.set_mode((SCRWIDTH, SCRHEIGHT))


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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print "mouse at (%d, %d)" % event.pos
        #______________________________________________________________________
        #
        # Key events and control
        #______________________________________________________________________
        #
        elif event.type == KEYDOWN:
            print "key pressed: " + str(event.key) # ???
            if event.key == K_ESCAPE:
                running = False

            if event.key == LEFT:
                print "a pressed, leftspeed +"
                playerXspeed += -5 # playerRect.move_ip(-5, 0)
            if event.key == RIGHT:
                print "d pressed, rightspeed +"
                playerXspeed += 5
                # playerRect.move_ip(5, 0)

            # jump. the Gravity section prevents jump craziness. collision
            # section resets the jumped variable to allow jumping again
            if event.key == JUMP and (jumped == False 
                                        or playerRect.left < 3  # wall jumps
                                        or playerRect.right > SCRWIDTH - 3):
                print "w pressed, upspeed +"
                jumping = True
                jumpframes = 0
                playerYspeed = -5
                jumped = True
            if event.key == DOWN:
                print "s pressed, downspeed +"
                playerYspeed += 5

        if event.type == KEYUP:
            print "key released: " + str(event.key) # ???
            if event.key == LEFT:
                print "a released, leftspeed -"
                playerXspeed += 5 # playerRect.move_ip(-5, 0)
            if event.key == RIGHT:
                print "d released, rightspeed -"
                playerXspeed += -5
            if event.key == JUMP:
                print "w released, upspeed -"
                jumping = False
                jumpframes = 0
            if event.key == DOWN:
                print "s released, downspeed -"
                playerYspeed += -5

    if jumping:
        jumpframes += 1

    #__________________________________________________________
    #
    # Gravity
    #__________________________________________________________
    # gravity if i've jumped too long
    # no gravity during jump or if too fast
    if (playerYspeed < 6 and not jumping) or jumpframes > 20:
        playerYspeed += 1 # gravity
        jumpframes = 0
        jumping = False
        print('gravity!')

    playerRect.move_ip(0, playerYspeed) # move based on speed
    if tilemap.in_collision(playerRect): # Y axis collision
        if playerYspeed > 0: # came from top
            playerRect.top = int((playerRect.top)
                                / tilemap.tileheight) * tilemap.tileheight
            jumped = False
        elif playerYspeed < 0: # came from bottom
            playerRect.top = int((playerRect.top + tilemap.tileheight)
                                / tilemap.tileheight) * tilemap.tileheight
            jumped = False

    # other object vertical collision
    #__________________________________________________________
#    if playerRect.colliderect(collisionbox):
#        if (collisionbox.top < playerRect.bottom
#                or collisionbox.bottom > playerRect.top):
#            playerRect.top = prevTop
#
#        jumped = False

    playerRect.move_ip(playerXspeed, 0) # move based on speed
    if tilemap.in_collision(playerRect): # X axis collision
        if playerXspeed > 0: # came from left
            playerRect.left = int((playerRect.left)
                                / tilemap.tilewidth) * tilemap.tilewidth
        elif playerXspeed < 0: # came from right
            playerRect.left = int((playerRect.left + tilemap.tilewidth)
                                / tilemap.tilewidth) * tilemap.tilewidth

    # Other object horizontal collision
    #__________________________________________________________
#    if playerRect.colliderect(collisionbox):
#        if (collisionbox.left < playerRect.right
#                or collisionbox.right > playerRect.left):
#            playerRect.left = prevLeft

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
        playerRect.left = 0
    if playerRect.right > SCRWIDTH:
        playerRect.left = SCRWIDTH - playerRect.width + 1
    prevTop = playerRect.top
    prevLeft = playerRect.left

    # redraw whole screen
    screen.fill((0, 0, 0))
    pygame.draw.rect(screen, playercolor, playerRect)
    for eachtile in solidtiles:
        screen.fill(blockcolor, eachtile)
    #pygame.draw.rect(screen, (255, 0, 0), collisionbox)
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

