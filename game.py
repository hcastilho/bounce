import sys
import pygame
import world
from world import Box2D
import pgview
import cwiid


class Game(object):

    def __init__(self):
        # Pygame and clock init
        pygame.init()
        self.clock=pygame.time.Clock()


        # Setup screen
        self.screen=pygame.display.set_mode((1024,500))
        self.screen.fill(pgview.BG_COLOR)

        # Setup screen areas
        screen_size=self.screen.get_size()

        hud_top=(0,0)
        hud_size=MinimumSize('arial',12,5)
        hud_size=(hud_size[0]+40,screen_size[1])

        arena_top=(hud_size[0],0)
        arena_size=(screen_size[0]-hud_size[0],screen_size[1])

        arena_rect=pygame.Rect(arena_top,arena_size)
        arena_surf=self.screen.subsurface(arena_rect)
        self.world=world.World(arena_surf)

        self.sprites=pygame.image.load('Devilish-MainBall.png')
        self.sprites.set_colorkey((0,248,0),pygame.RLEACCEL)
        p1_sprite=self.sprites.subsurface(pygame.Rect((2,29),(20,20))).copy()
        p2_sprite=self.sprites.subsurface(pygame.Rect((2,6),(20,20))).copy()

        self.players=[
                Player(self.world,self.world.balls,
                    p1_sprite,'Mouse',(0,0,255),arena_top),
                Player(self.world,self.world.balls,
                    p1_sprite,'Wiimote',(0,0,255),arena_top),
                #Player(self.world,self.world.balls,
                #    p2_sprite,'Mouse',(255,0,0),arena_top),
        ]


        hud_rect=pygame.Rect(hud_top,hud_size)
        hud_surf=self.screen.subsurface(hud_rect)
        self.hud=HUD(hud_surf,self.players,'arial',12,(255,255,255),(0,0,0))


    def run(self):

        #self.menu()

        pygame.display.update()

        while True:

            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                       self.world.makeBall()
                    elif event.key == pygame.K_ESCAPE:
                        sys.exit()

                for player in self.players:
                    if player.control=='Mouse':
                        player.mouseInputs(self.world,event)


            for player in self.players:
                if player.control=='Wiimote': player.wmInputs(self.world)

            self.world.update(self.players,self.hud)
            rectlist=[]
            rectlist.append(self.world.draw())
            if self.hud.hasChanged():
                rectlist.append(self.hud.draw())

            pygame.display.update(rectlist)

class Player(object):

    playerCount=0
    mouseOffset=(0,0)

    def __init__(self,world,balls,
            sprite,control='Mouse',color=(0,0,255),mouseOffset=(0,0)):

        Player.playerCount+=1
        self.playerNum=Player.playerCount
        self.control=control
        self.color=color
        self.sprite=sprite

        self.world=world
        self.balls=balls

        self.ball=None
        self.points=0

        self.active=False
        self.hud=None

        self.mouseOffset=mouseOffset

        if self.control=="Wiimote":
            # Setup Wiimotes
            print 'Press 1+2 on your Wiimote now'
            # TODO try catch
            self.wm=cwiid.Wiimote()
            self.wm.rpt_mode=cwiid.RPT_BTN | cwiid.RPT_ACC
            self.wmstate=self.wm.state


    def mouseInputs(self,world,event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Activate ball
            if event.button == 1:
                pos=(event.pos[0]-self.mouseOffset[0],
                     event.pos[1]-self.mouseOffset[1])
                self.activateBall(pos)
            # Next ball
            if event.button == 3: self.selectNextBall()
        # Deactivate ball
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.deactivateBall()
        # Update
        elif event.type == pygame.MOUSEMOTION and self.active:
            pos=(event.pos[0]-self.mouseOffset[0],
                 event.pos[1]-self.mouseOffset[1])
            self.updateControl(world,pos)

    def wmInputs(self,world):
        wmstate=self.wm.state
        # Next ball
        if (wmstate['buttons'] & cwiid.BTN_A) and \
        not (self.wmstate['buttons'] & cwiid.BTN_A):
            self.selectNextBall()
        # Activate ball
        if (wmstate['buttons'] & cwiid.BTN_B) and \
        not (self.wmstate['buttons'] & cwiid.BTN_B) :
            self.activateBall(wmstate['acc'])
        # Deactivate ball
        if not (wmstate['buttons'] & cwiid.BTN_B) and \
        (self.wmstate['buttons'] & cwiid.BTN_B):
            self.deactivateBall()
        # Push ball
        if (wmstate['buttons'] & cwiid.BTN_B) and self.active:
            self.updateControl(world,wmstate['acc'])

        self.wmstate=wmstate


    def selectNextBall(self):
        self.balls.selectNext(self)

    def activateBall(self,pos):
        self.balls.activate(self)
        if self.ball!=None:
            self.active=True
            self.createControl(pos)

    def deactivateBall(self):
        if self.active==True and self.ball!=None:
            self.active=False
            self.balls.deactivate(self)
            self.destroyControl()

    def createControl(self,vect):
        if self.control=='Mouse':
            self.joint=self.world.createJoint(self.ball,vect)
        elif self.control=='Wiimote':
            center=self.ball.body.massData.center
            fx=vect[0]*self.ball.body.GetMass()
            fy=vect[1]*self.ball.body.GetMass()
            self.ball.body.ApplyForce(Box2D.b2Vec2(fx,fy), center)

    def destroyControl(self):

        if self.control=='Mouse':
            self.world.destroyJoint(self.joint)
        elif self.control=='Wiimote':
            world.destroyForce(self.force)


    def updateControl(self,world,vect):

        # Mouse vect=position
        # Wiimote vect=acceleration

        if self.control=='Mouse' and self.active==True:
            self.ball.body.isSpleeping=False
            vect=world.s2wPos(vect)
            self.joint.target=Box2D.b2Vec2(vect[0], vect[1])
        elif self.control=='Wiimote':
            point=self.ball.body.getMassData.center
            print vect
            fx=vect[0]*self.ball.body.GetMass()
            fy=vect[1]*self.ball.body.GetMass()
            print fx
            print fy
            self.ball.body.ApplyForce(Box2D.b2Vec2(fx,fy), point)

    def incrementPoints(self,ball):
        self.points+=1
        self.hud.update()
        if ball is self.ball:
            self.ball=None
            self.active=False

def MinimumSize(font,font_size,num_players,line_spacing=5):
    font=pygame.font.SysFont(font,font_size)
    line_size=font.size('Player 9:  100')
    line_size=(line_size[0],line_size[1]+line_spacing)
    return (line_size[0],line_size[1]*num_players)

class HUD(object):

    def __init__(self,surface,players,font,font_size,font_color,bgcolor,line_spacing=5):

        for player in players:
            player.hud=self

        self.surface=surface
        self.font=pygame.font.SysFont(font,font_size)
        self.font_color=font_color
        self.bg_color=bgcolor
        self.line_spacing=line_spacing

        line_height=MinimumSize(font,font_size,1,line_spacing)[1]
        text_size=MinimumSize(font,font_size,len(players),line_spacing)
        hud_size=(text_size[0]+10,text_size[0]+10)

        hud_top=pgview.centerRectangles((0,0),surface.get_size(),hud_size)
        if hud_top==None:
            print 'HUD larger than area'
            sys.exit()
        hud_top=(hud_top[0],10)

        text_top=pgview.centerRectangles(hud_top,hud_size,text_size)
        if text_top==None:
            print 'Text larger than HUD'
            sys.exit()


        # x and y so that text is centered
        pos=[text_top]
        y=text_top[1]
        for player in players:
            y+=line_height
            pos.append((text_top[0],y))
        self.pos=pos

        self.players=players
        self.surface=surface
        self.changed=False

        self.surface.fill(self.bg_color,pygame.Rect(hud_top,hud_size))
        self.update()


    def update(self):
        for i in range(len(self.players)):
            txt='Player ' + str(self.players[i].playerNum) + ':  ' \
                    + str(self.players[i].points)
            text=self.font.render(txt,True,self.font_color,self.bg_color)
            rect=pygame.Rect(self.pos[i],(text.get_width(),text.get_height()))
            self.surface.blit(text,rect)
        self.changed=True

    def hasChanged(self):
        if self.changed:
            self.changed=False
            return True
        else: return False

    def draw(self):
        return self.surface.get_rect(topleft=self.surface.get_offset())



class Menu(object):
    def __init__(self,screen,optionList,
            font_type,font_size,border_spacing,item_spacing):
        """optionList[i]=(option text,callback) """
        self.screen=screen
        self.optionList=optionList

        self.font=pygame.font.SysFont(font_type,font_size)
        self.font=font_type
        self.font_size=font_size
        self.border_spacing=border_spacing
        self.item_spacing=item_spacing


        self.highlightedItem=None

    def menuSize(self):
        itemSize=self.itemSize()
        menuSize=(itemSize[0],(itemSize[1]+item_spacing)*len(self.optionList))
        return menuSize


    def itemSize(self):
        line_size=self.font.size(' '.ljust(self.maxlen()))
        return (line_size[0]+border_spacing,line_size[1]+2*border_spacing)

    def maxLength(self):
        maxlen=0
        for option,callback in self.optionList:
            if len(option)>maxlen: maxlen=len(option)
        return maxlen

    def showMenu(self):

        self.screen_back=self.screen.copy()

        menu_size=self.menuSize('arial',12,2,5,optionList)
        top_menu=centerRectangles((0,0),screen.size,menu_size())


        menuItem_top=top_menu
        menuItem_size=self.itemSize()
        self.menuItem_size=menuItem_size()

        self.menuItem_top=[]
        self.text_top=[]
        for option,callback in self.optionList:
            # Menu item rectangle
            surf=pygame.Surface(menuItem_size)
            surf.fill((255,255,255))

            # Menu item text
            text_size=self.font.size(option)
            text_surf=self.font.render(option,True,(0,0,0),(255,255,255))
            text_top=centerRectangles((0,0),menuItem_size,text_size)
            surf.blit(text_surf,text_top)

            # Blit item on screen
            self.screen.blit(surf,menuItem_top)

            # Store positions
            self.text_top.append(text_top)
            self.menuItem_top.append(menuItem_top)

            # Next item
            menuItem_top=(menuItem_top[0],menuItem_top[1]+menuItem_size[1]+self.item_spacing)

        pygame.display.uptdate()


    def highlightItem(self,index):
        text_surf=self.font.render(option,True,(0,0,255),(255,255,255))
        self.screen.blit(text_surf,self.text_top[index])
        self.hightlightedItem=index

    def unhighlight(self):
        if self.hilightedItem==None: return
        text_surf=self.font.render(option,True,(0,0,0),(255,255,255))
        self.screen.blit(text_surf,self.text_top[self.highlightedItem])

    def highlightDown(self):
        self.unhighlightItem()
        if self.highlightedItem==None: index=0
        else:
            index=self.highlightededItem+1
            if index>len(self.menuItem_top)-1: index=0
        self.highlightItem(index)

    def highlightUp(self):
        self.unhighlightItem()
        if self.highlightedItem==None: index=len(self.menuItem_top)-1
        else:
            index=self.highlightedItem-1
            if index<0: index==len(self.menuItem_top)-1
        self.highlightItem(index)

    def highlightMouseOver(self,pos):
        mouseOver=None
        for i in range(len(self.menuItem_top)):
            top=self.menuItem_top[i]
            size=self.menuItem_size
            if pos[0]<top[0] or pos[1]<top[1]: break
            elif pos[0]<top[0]+size[0] and pos[1]<top[1]+size[1]:
                mouseOver=i
                break

        if mouseOver!=None:
            self.unhighlight()
            self.highlight(mouseOver)

    def callback(self):
        if self.highlightedItem!=None:
            index=self.highlightedItem
            self.optionList[index][1]()


    def getCallback(self,pos):
        for i in range(len(self.menuItem_top)):
            top=self.menuItem_top[i]
            size=self.menuItem_size
            if pos[0]<top[0] or pos[1]<top[1]: break
            elif pos[0]<top[0]+size[0] and pos[1]<top[1]+size[1]:
                return self.optionList[i][1]

#    def getCallbackHighlighted(self)
#        return self.optionList[self.highlightedItem][1]


    def run(self):

        self.showMenu()

        while True:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.quit()
                    elif event.key == pygame.K_UP:
                        self.highlightDown()
                    elif event.key == pygame.K_DOWN:
                        self.highlightUp()
                    elif event.key == pygame.K_ENTER:
                        self.callback()


                for player in self.players:
                    if player.control=='Mouse':
                        if event.type == pygame.MOUSEBUTTONDOWN:
                            if event.button == 1:
                                self.callback()
                        elif event.type == pygame.MOUSEMOTION:
                            self.highlightMouseOver(event.pos)


            #for player in self.players:
            #    if player.control=='Wiimote': player.wmInputs(self.world)

    def quit(self):
        self.screen.blit(self.screen_backup)
        pygame.display.uptdate()



