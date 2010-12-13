
import pygame
import numpy

BG_COLOR=(0,255,255)

size=numpy.array([40,40])
scale=numpy.array([12,12])
wtop=numpy.array([-1,1])*(size/2)
wbot=numpy.array([1,-1])*(size/2)

S=numpy.array([(scale[0], 0,        1),
               (0,        scale[1], 1),
               (0,        0,        1))

M=numpy.array([(1,  0, 1),
               (0, -1, 1),
               (0,  0, 1)])

def w2sScale(vect):
    """Scale vector from world to screen"""
    return dot(S,abs(vect))

p=w2sScale(wtop)
P=numpy.array([(1, 0, p[0]),
               (0, 1, p[1]),
               (0, 0, 1)])
T=dot(P,dot(M,S))

def w2sPos(vect):
    """Transform world coordinates to screen coordinates"""
    vect=numpy.array(vect+(1,))
    return dot(T,vect)

TI=numpy.array([(1/scale[0], 0,         -p[0]/scale[0]),
                (0,          -1/scale[1], p[1]/scale[1] ),
                (0,          0,          1)])

SI=numpy.array([(1/scale[0], 0,          0),
                (0,          1/scale[1], 0 ),
                (0,          0,          1)])
def s2wScale(vect):
    """Scale vector from screen to world"""
    return dot(SI,abs(vect))

def s2wPos(vect):
    """Transform screen coordinates to world coordinates"""
    vect=numpy.array(vect+(1,))
    return dot(TI,vect)
#WIDTH=40
#HEIGHT=40
#AWIDTH=int(WIDTH/2)
#AHEIGHT=int(HEIGHT/2)
#
#WTOP=-AWIDTH,AHEIGHT
#WBOT=AWIDTH,-AHEIGHT
#
#SCALE=12,12
#
#
#def w2sScale(pos):
#    """Scale vector from world to screen"""
#    pos=(abs(pos[0])*SCALE[0], abs(pos[1])*SCALE[1])
#    return pos
#
#def w2sPos(pos):
#    """Convert world coordinates to screen coordinates"""
#    pos=(TRANS[0]+pos[0]*SCALE[0], TRANS[1]-pos[1]*SCALE[1])
#    return pos
#
#def s2wScale(pos):
#    """Scale vector from world to screen"""
#    pos=(abs(pos[0])/SCALE[0], abs(pos[1])/SCALE[1])
#    return pos
#
#def s2wPos(pos):
#    """Convert world coordinates to screen coordinates"""
#    pos=((pos[0]-TRANS[0])/SCALE[0], (-pos[1]+TRANS[1])/SCALE[1])
#    return pos
#
#TRANS=w2sScale(WTOP)
#
#STOP=0,0
#SBOT=w2sPos(WBOT)

