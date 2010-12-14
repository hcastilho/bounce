import sys
import pygame
import world
from world import Box2D
import pgview
import cwiid

class Game(object):

    def __init__(self):
        pygame.init()
        self.clock=pygame.time.Clock()
        self.world=world.World()

        self.players=[Player('Mouse')]


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
                if event.type == pygame.QUIT:
                    if self.controller=='Wiimote': self.wm.close()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                       self.world.makeBall()
                    elif event.key == pygame.K_ESCAPE:
                        if self.controller=='Wiimote': self.wm.close()
                        sys.exit()

                for player in self.players:
                    if player.control=='Mouse':
                        player.mouseInputs(event,self.world)


            for player in self.players:
                if player.control=='Wiimote': player.wmInputs(self.world)

            self.world.step()
            self.world.destroyViolations(self.players)
            self.world.draw()


class Player(object):

    playerNum=1
    ball=None
    active=False
    points=0

    def __init__(self,control='Mouse',color=(0,0,255)):
        Player.playerNum+=1
        self.control=control
        self.color=color

        if self.control=="Wiimote":
            # Setup Wiimotes
            print 'Press 1+2 on your Wiimote now'
            # TODO try catch
            self.wm=cwiid.Wiimote()
            self.wm.rpt_mode=cwiid.RPT_BTN | cwiid.RPT_ACC
            self.wmstate=self.wm.state

    def select(self):
        if self.ball!=None: self.ball.select(self.color)

    def unselect(self):
        if self.ball!=None:
            self.ball.unselect()
            self.ball=None

    def selectNext(self,group):

        if len(group)==0 : return

        if self.ball!=None:
            self.ball.unselect()
            ind=group.sprites().index(self.ball)+1
            if ind>=len(group): ind=0
            self.ball=group.sprites()[ind]
        else:
            self.ball=group.sprites()[0]

        self.select()

    def activate(self,world):
        if self.ball==None:
            self.selectNext(world.balls)

        if self.ball!=None:
            if self.control=='Mouse':
                self.joint=world.createJoint(self.ball)
            # TODO
            #elif self.control='Wiimote':
            #    self.force=world.createForce()

            self.ball.activate()
            self.active=True

    def deactivate(self,world):
        if self.ball!=None:

            if self.control=='Mouse':
                world.destroyJoint(self.joint)
            # TODO force needs to be updated on every step?
            # where is ClearForces?
            #elif self.control='Wiimote':
            #    world.destroyForce(self.force)

            self.ball.deactivate(self.color)
            self.active=False

    def mouseInputs(self,event,world):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Activate ball
            if event.button == 1:
                self.activate(world)
            # Next ball
            if event.button == 3: self.selectNext(world.balls)
        # Deactivate ball
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: self.deactivate(world)
        # Update
        elif event.type == pygame.MOUSEMOTION and self.active:
            self.updateTarget(event.pos)

    def wmInputs(self,world):
        wmstate=self.wm.state
        # Next ball
        if (wmstate['buttons'] & cwiid.BTN_A) and \
        not (self.wmstate['buttons'] & cwiid.BTN_A):
            self.selectNext(world.balls)
        # Activate ball
        if (wmstate['buttons'] & cwiid.BTN_B) and \
        not (self.wmstate['buttons'] & cwiid.BTN_B) :
            self.world.activateObject()
        # Deactivate ball
        if not (wmstate['buttons'] & cwiid.BTN_B) and \
        (self.wmstate['buttons'] & cwiid.BTN_B):
            self.deactivate(world)
        # Push ball
        if (wmstate['buttons'] & cwiid.BTN_B) and self.active:
            self.updateForce(wmstate['acc'][0],wmstate['acc'][2])

        self.wmstate=wmstate


    def updateTarget(self,pos):
        self.ball.body.isSpleeping=False
        pos=pgview.s2wPos(pos)
        self.joint.target=Box2D.b2Vec2(pos[0], pos[1])


    def updateForce(self,ax,ay):
        point=ball.body.getMassData.center
        fx=ax*ball.body.GetMass()
        fy=ay*ball.body.GetMass()
        ball.body.ApplyForce(Box2D.b2Vec2(fx,fy), point)
        return


class HUD(object):
    def __init__(self):
        return



class Menu(object):
    def __init__(self):
        return

