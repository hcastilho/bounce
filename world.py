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

    def __init__(self,world,radiusS=30,pos=(0,0)):

        pygame.sprite.Sprite.__init__(self)

        self.world=world

        self.radiusS=radiusS
        self.radiusW=world.s2wScale((0,radiusS))[1]
        #print radiusS
        #print self.radiusW
        #print world.w2sScale((0,self.radiusW))[1]

        self.thickness=3

        self._initDisplay()

        self._initPhysics(world,pos)

        self.player=None
        self.state='Unselected'


    def _initDisplay(self):
        if Ball.image is None:
            img=pygame.image.load("basic-ball.png").convert()
            img=pygame.transform.scale(img,(int(round(2*self.radiusS)),
                int(round(2*self.radiusS))))
            img.set_colorkey((0,248,0),pygame.RLEACCEL)
            Ball.image=img

        self.image=Ball.image.convert()
        self.rect = self.image.get_rect()


    def _initPhysics(self,world,pos):
        bodyDef=Box2D.b2BodyDef()
        pos=world.s2wPos(pos)
        bodyDef.position=Box2D.b2Vec2(pos[0],pos[1])
        #bodyDef.fixedRotation=True

        body=world.world.CreateBody(bodyDef)

        shapeDef=Box2D.b2CircleDef()
        shapeDef.radius=self.radiusW
        shapeDef.density=1
        shapeDef.friction=0.1
        shapeDef.restitution=0.5

        body.CreateShape(shapeDef)
        body.SetMassFromShapes()

        self.body=body


    def update(self):
        pos=self.body.GetPosition()
        pos=(pos.x,pos.y)
        pos=self.world.w2sPos(pos)
        self.rect.center=pos

    def select(self,player):

        self.image=player.sprite.convert()
        self.image=pygame.transform.scale(self.image,(int(round(2*self.radiusS)),
                int(round(2*self.radiusS))))
        color=player.color
        pygame.draw.circle(self.image,color,
                (int(round(self.rect.w/2)),int(round(self.rect.h/2))),
                int(round(self.radiusS))+1,self.thickness)

        self.state='Selected'
        self.player=player

    def activate(self):

        if self.state!='Selected':
            print 'Assert fail: activate'
            print self.state

        pygame.draw.circle(self.image,(0,255,0),
                (int(round(self.rect.w/2)),int(round(self.rect.h/2))),
                int(round(self.radiusS))+1,self.thickness)

        self.state='Active'

    def unselect(self):

        if self.state!='Active' and self.state!='Selected':
            print 'Assert fail: unselect'
            print self.state

        if self.player!=None:
            self.image=self.player.sprite.convert()
            self.image=pygame.transform.scale(self.image,
                    (int(round(2*self.radiusS)),
                    int(round(2*self.radiusS))))
        else:
            self.image=Ball.image.convert()

        self.state='Unselected'

    def deactivate(self,player):
        self.select(player)

    def updatePlayer(self,player):
        self.image=player.sprite.convert()
        self.image=pygame.transform.scale(self.image,
                (int(round(2*self.radiusS)),
                int(round(2*self.radiusS))))
        self.player=player


class Wall(object):
    def __init__(self,world,top,size):


        scenter=(top[0]+(size[0]/2),
                top[1]+(size[1]/2))
        wcenter=world.s2wPos(scenter)

        extends=world.s2wScale(size)

        #print 'top: '+str(top)
        #print 'scenter: '+str(scenter)
        #print 'wcenter: '+str(wcenter)
        #print world.w2sPos(wcenter)
        #print 'size: '+str(size)
        #print 'extends: '+str(extends)
        #print world.w2sScale(extends)


        # Physics
        walldef=Box2D.b2BodyDef()
        walldef.position=Box2D.b2Vec2(wcenter[0],wcenter[1])
        walldef.userData={}
        wallbody=world.world.CreateBody(walldef)
        wallbody.iswall=True
        wallshape=Box2D.b2PolygonDef()
        width, height = extends
        wallshape.SetAsBox(width/2, height/2)
        wallbody.CreateShape(wallshape)

        # Display
        self.image=pygame.Surface(size)
        self.image.fill((56,71,216))
        self.rect = self.image.get_rect()
        self.rect.topleft=top
        #print top
        #print size


    def draw(self,screen):
        screen.blit(self.image,self.rect)


class World(object):

    world_size=(40.,40.)  # 40 meters

    def __init__(self,surface):

        # Drawing surface
        self.surface=surface
        self.surface.fill(pgview.BG_COLOR)

        # Find largest square on surface
        self.area_top=area_top=(0,0)
        area_size=self.surface.get_size()
        self.area_size=area_size
        if area_size[0]>=area_size[1]:
            arena_size=(area_size[1],area_size[1])
        else:
            arena_size=(area_size[0],area_size[0])
        self.arena_size=arena_size

        arena_top=pgview.centerRectangles(area_top,area_size,arena_size)
        self.arena_top=arena_top
        #print area_top
        #print arena_top

        # Variables for coordinate transformations
        self.scale=(float(arena_size[0])/self.world_size[0],
                    float(arena_size[1])/self.world_size[1])
        self.mirror=(1,-1)
        self.trans=(arena_top[0]+float(arena_size[0])/2,
                arena_top[1]+float(arena_size[1])/2)
        #print 'scale: '+str(self.scale)
        #print 'trans: '+str(self.trans)

        # Ball group
        self.balls=Balls()

        # Physics Engine options
        gravity=(0,-10)
        doSleep=True
        self.timeStep=1.0/60.0
        self.velIterations=10
        self.posIterations=8

        # World bouding box
        aabb=Box2D.b2AABB()
        aabb.upperBound=Box2D.b2Vec2(self.world_size[0]/2,self.world_size[1]/2)
        aabb.lowerBound=Box2D.b2Vec2(-self.world_size[0]/2,-self.world_size[1]/2)
        #print arena_top
        #print arena_size
        #print aabb.upperBound
        #print aabb.lowerBound
        #print self.s2wPos(arena_top)
        #print self.s2wScale(arena_size)
        #print self.s2wPos((arena_top[0]+arena_size[0],arena_top[1]+arena_size[1]))

        # World
        self.world=Box2D.b2World(aabb,gravity,doSleep)
        # World listeners
        self.boundaryListener=BoundListener()
        self.world.SetBoundaryListener(self.boundaryListener)
        self.contactListener=ContactListener(self.balls)
        self.world.SetContactListener(self.contactListener)

        # Walls
        self.staticObjs=[]
        self.makeBounds(arena_top,arena_size)
        # Draw Walls
        for obj in self.staticObjs:
            obj.draw(self.surface)
        self.background=self.surface.copy()

    def w2sPos(self,wpos):
        spos=( int(round(wpos[0]*self.scale[0]*self.mirror[0]+self.trans[0])),
               int(round(wpos[1]*self.scale[1]*self.mirror[1]+self.trans[1])))
        return spos

    def s2wPos(self,spos):
        wpos=( (spos[0]-self.trans[0])/(self.scale[0]*self.mirror[0]),
               (spos[1]-self.trans[1])/(self.scale[1]*self.mirror[1]))
        return wpos


    def s2wScale(self,vect):
        vectW=(vect[0]/self.scale[0],
              vect[1]/self.scale[1])
        return vectW

    def w2sScale(self,vect):
        vectS=(int(round(vect[0]*self.scale[0])),
              int(round(vect[1]*self.scale[1])))
        return vectS


    def makeBounds(self,arena_top,arena_size,thickness=10):

        # Wall(world,top,width)

        # Left
        self.staticObjs.append(
                Wall(self,
                    arena_top,
                    (thickness,arena_size[1])))
        # Right
        self.staticObjs.append(
                Wall(self,
                    (arena_top[0]+arena_size[0]-thickness,arena_top[1]),
                    (thickness,arena_size[1])))
        # Bottom
        self.staticObjs.append(
                Wall(self,
                    (arena_top[0],arena_top[1]+arena_size[1]-thickness),
                    (arena_size[0],thickness)))
        # Top
        self.staticObjs.append(
                Wall(self,
                    arena_top,
                    (int(round(arena_size[0]/4)),thickness)))
        self.staticObjs.append(
                Wall(self,
                    (arena_top[0]+int(round((3*arena_size[0])/4)),arena_top[1]),
                    (int(round(arena_size[0]/4)),thickness)))


    def makeBall(self):

        radius=30
        pos=(
        random.randrange(self.arena_top[0]+radius,
            self.arena_top[0]+self.arena_size[0]-radius),
        random.randrange(self.arena_top[1]+radius,
            self.arena_top[1]+self.arena_size[1]-radius)
        )

        self.balls.add(Ball(self,30,pos))

    def getBallsFromBodies(self,bodies):
        ballList=[]
        for body in bodies:
            ballList.append(self.balls.ballFromBody(body))

        return ballList

    def destroyViolations(self,players,hud):
        balls=self.getBallsFromBodies(self.boundaryListener.violations)
        for ball in balls:
            self.world.DestroyBody(ball.body)

            if ball.player!=None:
                ball.player.incrementPoints(ball)
            self.balls.remove(ball)

        self.boundaryListener.violations=[]

    def update(self,players,hud):
        self.world.Step(self.timeStep,self.velIterations,self.posIterations)
        for ball in self.balls:
            ball.update()
        self.destroyViolations(players,hud)


    def draw(self):

        self.balls.clear(self.surface,self.background)
        rectlist=self.balls.draw(self.surface)
        return self.surface.get_rect(topleft=self.surface.get_offset())

    def createJoint(self,ball,pos):

        mouseDef=Box2D.b2MouseJointDef()
        pos=self.s2wPos(pos)
        mouseDef.target=Box2D.b2Vec2(pos[0], pos[1])
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


class ContactListener(Box2D.b2ContactListener):
    def __init__(self,balls):
        Box2D.b2ContactListener.__init__(self)
        self.balls=balls

    def Add(self,contactPoint):
        #self.contacts.append(contactPoint)
        body1=contactPoint.shape1.GetBody()
        body2=contactPoint.shape2.GetBody()
        ball1=self.balls.ballFromBody(body1)
        ball2=self.balls.ballFromBody(body2)

        if ball1==None or ball2==None: return

        if ball1.state=='Active' or ball1.state=='Selected':
            if ball2.state=='Unselected':
                ball2.updatePlayer(ball1.player)
        else:
            if ball2.state=='Active' or ball2.state=='Selected':
                if ball1.state=='Unselected':
                    ball1.updatePlayer(ball2.player)


class Balls(pygame.sprite.RenderUpdates):
    def __init__(self):
        pygame.sprite.RenderUpdates.__init__(self)

    def ballFromBody(self,body):
        for ball in self.sprites():
            if body == ball.body:
                return ball
        return None


    def selectNext(self,player):
        ball=player.ball

        if len(self)==0: return

        if ball==None:
            #ball=group.sprites()[0]
            ind=0
        else:
            ball.unselect()
            ind=self.sprites().index(ball)+1
            if ind>=len(self): ind=0
            #ball=group.sprites()[ind]

        for i in range(len(self)):
            if self.sprites()[ind].state=='Unselected':
                ball=self.sprites()[ind]
                ball.select(player)
                player.ball=ball
                break
            ind+=1
            if ind>=len(self): ind=0




    def select(self,player):
        if ball.player==None: self.selectNext(player)

        if ball.player!=None: player.ball.select(player)

    def unselect(self,player):
        player.ball.unselect()

    def activate(self,player):
        if player.ball==None: self.selectNext(player)
        if player.ball!=None: player.ball.activate()

    def deactivate(self,player):
        if player.ball!=None: player.ball.deactivate(player)

    def updateLastPlayer(self,player,ball):
        ball.player=player





