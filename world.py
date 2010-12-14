#!/usr/bin/python
# -*- coding: utf-8 -*-

#import world
#from world import Box2D # TODO necessário??
import Box2D,pygame
import random
import pgview

class Ball(pygame.sprite.Sprite):
    """Bola ;)"""

    image=None

    def __init__(self,world):

        pygame.sprite.Sprite.__init__(self)


        self.radiusW=3
        self.radiusS=pgview.w2sScale((0,self.radiusW))[1]

        self.thickness=3

        self._initDisplay()

        rx=random.randrange(-pgview.size[0]/2+self.radiusW,
                pgview.size[0]/2-self.radiusW)
        ry=random.randrange(-pgview.size[1]/2+self.radiusW
                ,pgview.size[1]/2-self.radiusW)
        pos=Box2D.b2Vec2(rx,ry)


        self._initPhysics(world,pos)


    def _initDisplay(self):
        if Ball.image is None:
            img=pygame.image.load("beach-ball.png").convert()
            img=pygame.transform.scale(img,(2*self.radiusS,2*self.radiusS))
            img.set_colorkey((255,0,0),pygame.RLEACCEL)
            Ball.image=img

        self.surface=Ball.image.convert()
        self.rect = self.surface.get_rect()


    def _initPhysics(self,world,pos):
        bodyDef=Box2D.b2BodyDef()
        bodyDef.position=pos
        #bodyDef.fixedRotation=True

        body=world.CreateBody(bodyDef)

        shapeDef=Box2D.b2CircleDef()
        shapeDef.radius=self.radiusW
        shapeDef.density=1
        shapeDef.friction=0.1
        shapeDef.restitution=0.5

        body.CreateShape(shapeDef)
        body.SetMassFromShapes()

        self.body=body

    def update(self):
        self.step()

    def step(self):
        pos=self.body.GetPosition()
        pos=(pos.x,pos.y)
        pos=pgview.w2sPos(pos)
        self.rect.center=pos

    def draw(self,screen):
        screen.blit(self.surface,self.rect)

    def select(self,color):
        pygame.draw.circle(self.surface,color,(self.rect.w/2,self.rect.h/2),self.radiusS+1,self.thickness)

    def activate(self):
        pygame.draw.circle(self.surface,(0,255,0),(self.rect.w/2,self.rect.h/2),self.radiusS+1,self.thickness)

    def unselect(self):
        self._initDisplay()

    def deactivate(self,color):
        self.select(color)


class Wall(object):
    def __init__(self,world,pos,size):

        # Physics
        walldef=Box2D.b2BodyDef()
        walldef.position=pos
        walldef.userData={}
        wallbody=world.CreateBody(walldef)
        wallbody.iswall=True
        wallshape=Box2D.b2PolygonDef()
        width, height = size
        wallshape.SetAsBox(width, height)
        wallbody.CreateShape(wallshape)

        # Display
        size=pgview.w2sScale((2*size[0],2*size[1]))
        self.surface=pygame.Surface(size)
        self.surface.fill((0,0,0))
        self.rect = self.surface.get_rect()
        self.rect.center=pgview.w2sPos(pos)

    def draw(self,screen):
        screen.blit(self.surface,self.rect)


class World(object):
    def __init__(self):
        self.balls=pygame.sprite.Group()
        self.selectedBall=None
        self.selectedActive=False

        self.staticObjs=[]

        gravity=(0,-10)
        doSleep=True
        self.timeStep=1.0/60.0
        self.velIterations=10
        self.posIterations=8

        aabb=Box2D.b2AABB()
        aabb.upperBound=Box2D.b2Vec2(pgview.size[0]/2,pgview.size[1]/2)
        aabb.lowerBound=Box2D.b2Vec2(-pgview.size[0]/2,-pgview.size[1]/2)

        self.world=Box2D.b2World(aabb,gravity,doSleep)

        self.boundaryListener=BoundListener()
        self.world.SetBoundaryListener(self.boundaryListener)

        self.screen=pygame.display.set_mode(pgview.sbot)

        self.makeBounds()


    def makeBounds(self):
        (AWIDTH,AHEIGHT)=pgview.size/2
        # Left
        self.staticObjs.append(Wall(self.world,(-AWIDTH,0),(1,AHEIGHT)))
        # Right
        self.staticObjs.append(Wall(self.world,(AWIDTH,0),(1,AHEIGHT)))
        # Top
        #self.staticObjs.append(Wall(self.world,(0,pgview.AHEIGHT),(pgview.AWIDTH,1)))
        self.staticObjs.append(Wall(self.world,(-AWIDTH,AHEIGHT),(AWIDTH/2,1)))
        self.staticObjs.append(Wall(self.world,(AWIDTH,AHEIGHT),(AWIDTH/2,1)))
        # Bottom
        self.staticObjs.append(Wall(self.world,(0,-AHEIGHT),(AWIDTH,1)))


    def makeBall(self):
        self.balls.add(Ball(self.world))

    def getBallsFromBodies(self,bodies):
        ballList=[]
        for body in bodies:
            for ball in self.balls:
                if body is ball.body: ballList.append(ball)

        return ballList

    def destroyViolations(self,players):
        balls=self.getBallsFromBodies(self.boundaryListener.violations)
        for ball in balls:
            self.world.DestroyBody(ball.body)
            if player.ball is ball:
                player.ball=None
                player.active=False
            self.balls.remove(ball)

    def step(self):
        self.world.Step(self.timeStep,self.velIterations,self.posIterations)
        for ball in self.balls:
            ball.step()

    def draw(self):
            self.screen.fill(pgview.BG_COLOR)
            for obj in self.staticObjs:
                obj.draw(self.screen)
            for ball in self.balls:
               ball.draw(self.screen)
            pygame.display.flip()

    def createJoint(self,ball):

        mouseDef=Box2D.b2MouseJointDef()
        #pos=pgview.s2wPos(pos)
        #mouseDef.target=Box2D.b2Vec2(pos[0], pos[1])
        mouseDef.maxForce=20000*ball.body.GetMass()
        mouseDef.body1=self.world.groundBody
        mouseDef.body2=ball.body
        mouseDef.collideConnected=True

        return self.world.CreateJoint(mouseDef).asMouseJoint()

    def destroyJoint(self,joint):
        self.world.DestroyJoint(joint)


class BoundListener(Box2D.b2BoundaryListener):
    violations=[]
    def Violation(self,body):
        self.violations.append(body)


