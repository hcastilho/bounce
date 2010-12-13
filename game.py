import sys
import pygame
import world
import pgview
import cwiid

class Game(object):

    controller="Mouse"
    #controller="Wiimote"

    def __init__(self):
        self.clock=pygame.time.Clock()
        self.world=world.World()

        if self.controller="Wiimote":
            # Setup Wiimotes
            a=1

    def menu(self):
        return

    def setup_controllers(self):
        return

    def run(self):


        while True:

            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: sys.exit()

                if self.controller="Mouse":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE:
                            self.world.selectNextObject()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1: self.world.activateObject(event.pos)
                        if event.button == 3: self.world.makeBall()
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if event.button == 1: self.world.deactivateObject()
                    elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                        self.world.updateTarget(event.pos)

                elif self.controller=="Wiimote":
                    a=1

            self.world.step()
            self.world.draw()


