import sys
import pygame
import world
import pgview
import cwiid

class Game(object):

    controller="Mouse"
    #controller="Wiimote"

    def __init__(self):
        pygame.init()
        self.clock=pygame.time.Clock()
        self.world=world.World()

        if self.controller=="Wiimote":
            # Setup Wiimotes
            print 'Press 1+2 on your Wiimote now'
            # TODO try catch
            self.wm=cwiid.Wiimote()
            self.wm.rpt_mode=cwiid.RPT_BTN | cwiid.RPT_ACC
            self.wmstate=self.wm.state

    def menu(self):
        self.font=pygame.font.SysFont('arial',50)
        surface=self.font.render('blah blah',True,(125,125,0),(0,0,0))
        rect=pygame.Rect((50,50),(surface.get_width(),surface.get_height()))
        self.world.screen.blit(surface,rect)

        return

    def setup_controllers(self):
        return

    def run(self):

        self.menu()

        while True:

            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.controller=='Wiimote': self.wm.close()
                        sys.exit()

                if self.controller=="Mouse":
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

            if self.controller=="Wiimote":
                wmstate=self.wm.state
                # Add ball
                if (wmstate['buttons'] & cwiid.BTN_A) and \
                not (self.wmstate['buttons'] & cwiid.BTN_A):
                    self.world.makeBall()
                # Activate ball
                if (wmstate['buttons'] & cwiid.BTN_B) and \
                not (self.wmstate['buttons'] & cwiid.BTN_B) :
                    self.world.activateObject()
                # Deactivate ball
                if not (wmstate['buttons'] & cwiid.BTN_B) and \
                (self.wmstate['buttons'] & cwiid.BTN_B):
                    self.world.deactivateObject()
                # Push ball
                if wmstate['buttons'] & cwiid.BTN_B:
                    self.world.pushObject(wmstate['acc'][0],wmstate['acc'][2])
                # Next ball
                if not (wmstate['buttons'] & cwiid.BTN_RIGHT) and \
                (self.wmstate['buttons'] & cwiid.BTN_RIGHT):
                        self.world.selectNextObject()

                self.wmstate=wmstate

            self.world.step()
            self.world.draw()


