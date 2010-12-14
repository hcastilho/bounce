#!/usr/bin/python
# -*- coding: utf-8 -*-

#import world
#from world import Box2D # TODO necessário??
import Box2D,pygame
import random
import pgview

class Ball(object):
    """Bola ;)"""
    def __init__(self,world):

        #self.originalSurface=pygame.image.load("beach-ball.png").convert()

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
        self.surface=pygame.image.load("beach-ball.png").convert()
        self.surface=pygame.transform.scale(self.surface,(2*self.radiusS,2*self.radiusS))
        self.surface.set_colorkey((255,0,0),pygame.RLEACCEL)
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


    def step(self):
        pos=self.body.GetPosition()
        pos=(pos.x,pos.y)
        pos=pgview.w2sPos(pos)
        self.rect.center=pos

    def draw(self,screen):
        screen.blit(self.surface,self.rect)

    def select(self):
        pygame.draw.circle(self.surface,(0,0,255),(self.rect.w/2,self.rect.h/2),self.radiusS+1,self.thickness)

    def activate(self):
        pygame.draw.circle(self.surface,(0,255,0),(self.rect.w/2,self.rect.h/2),self.radiusS+1,self.thickness)

    def unselect(self):
        self._initDisplay()


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
        self.objects=[]
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

        self.selectedObject=-1



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

        self.objects.append(Ball(self.world))

    def destroyBall(self,index):
        obj=self.objects[index]
        self.world.DestroyBody(obj.body)
        del(self.objects[index])

    def destroyBallHash(self,hash):
        # Get index
        i=-1
        for index in range(len(self.objects)):
            if self.objects[index].body.__hash__==hash: i=index

        if i==-1: return
        else:
            self.destroyBall(i)
            # Destroyed ball is currently selected/active
            if self.selectedObject==i:
                # No more balls to select
                if len(self.objects)==0:
                    self.selectedObject=-1
                    return
                else:
                    self.selectObject()

    def step(self):
        self.world.Step(self.timeStep,self.velIterations,self.posIterations)
        self.destroyViolations()
        for obj in self.objects:
            obj.step()

    def draw(self):
            self.screen.fill(pgview.BG_COLOR)
            for obj in self.staticObjs:
                obj.draw(self.screen)
            for obj in self.objects:
               obj.draw(self.screen)
            pygame.display.flip()

    def selectNextObject(self):

        if len(self.objects)==0: return

        if self.selectedObject!=-1: self.objects[self.selectedObject].unselect()

        self.selectedObject+=1
        if self.selectedObject>=len(self.objects): self.selectedObject=0

        self.objects[self.selectedObject].select()

    def selectObject(self):
        if len(self.objects)==0 or self.selectedObject==-1: return

        self.objects[self.selectedObject].select()

    def activateObject(self,pos):
        if len(self.objects)==0: return

        if self.selectedObject==-1: self.selectNextObject()

        self.objects[self.selectedObject].activate()
        self._createJoint(pos)

    def deactivateObject(self):
        if len(self.objects)==0 or self.selectedObject==-1: return

        self._destroyJoint()
        self.objects[self.selectedObject].select()

    def _createJoint(self,pos):

        obj=self.objects[self.selectedObject]

        mouseDef=Box2D.b2MouseJointDef()
        pos=pgview.s2wPos(pos)
        mouseDef.target=Box2D.b2Vec2(pos[0], pos[1])
        #mouseDef.target=obj.body.position
        mouseDef.maxForce=20000*obj.body.GetMass()
        #mouseDef.frequencyHz=1
        #mouseDef.dampening=0.3
        mouseDef.body1=self.world.groundBody
        mouseDef.body2=obj.body
        mouseDef.collideConnected=True
        self.joint=self.world.CreateJoint(mouseDef).asMouseJoint()

    def _destroyJoint(self):
        self.world.DestroyJoint(self.joint)

    def updateTarget(self,pos):
        if len(self.objects)==0 or self.selectedObject==-1: return

        obj=self.objects[self.selectedObject]
        obj.body.isSpleeping=False

        pos=pgview.s2wPos(pos)
        self.joint.target=Box2D.b2Vec2(pos[0], pos[1])

    def pushObject(self,acc):
        obj=self.objects[selectedObject]
        point=obj.body.getMassData.center
        force=acc*obj.body.GetMass()
        obj.body.ApplyForce(b2Vec2 force, b2Vec2 point)

    def destroyViolations(self):
        for hash in self.boundaryListener.violations:
            self.destroyBallHash(hash)
        self.boundaryListener.violations=[]

class BoundListener(Box2D.b2BoundaryListener):
    violations=[]
    def Violation(self,body):
        self.violations.append(body.__hash__)



