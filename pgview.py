
import pygame
import numpy

def centerRectangles(r1T,r1S,r2S):
    if r2S[0]>r1S[0] or r2S[1]>r1S[1]: return None
    r2T=(r1T[0]+int((r1S[0]-r2S[0])/2),r1T[1]+int((r1S[1]-r2S[1])/2))
    return r2T

BG_COLOR=(0,255,255)

size=numpy.array([40.,40.])
scale=numpy.array([10.,10.])
wtop=numpy.array([-1.,1.])*(size/2)
wbot=numpy.array([1.,-1.])*(size/2)

S=numpy.array([(scale[0], 0,        0),
               (0,        scale[1], 0),
               (0,        0,        1)])

M=numpy.array([(1,  0, 0),
               (0, -1, 0),
               (0,  0, 1)])

def w2sScale(vect):
    """Scale vector from world to screen"""
    vect=numpy.concatenate((vect,(1.,)))
    return numpy.dot(S,abs(vect)).tolist()[0:2]

p=w2sScale(wtop)
P=numpy.array([(1, 0, p[0]),
               (0, 1, p[1]),
               (0, 0, 1)])
T=numpy.dot(P,numpy.dot(M,S))

def w2sPos(vect):
    """Transform world coordinates to screen coordinates"""
    vect=numpy.concatenate((vect,(1.,)))
    return numpy.dot(T,vect).tolist()[0:2]

stop=numpy.array([(0,0)])
sbot=w2sScale(size)

TI=numpy.array([(1/scale[0], 0,         -p[0]/scale[0]),
                (0,          -1/scale[1], p[1]/scale[1] ),
                (0,          0,          1)])

SI=numpy.array([(1/scale[0], 0,          0),
                (0,          1/scale[1], 0 ),
                (0,          0,          1)])
def s2wScale(vect):
    """Scale vector from screen to world"""
    vect=numpy.concatenate((vect,(1.,)))
    return numpy.dot(SI,abs(vect)).tolist()[0:2]

def s2wPos(vect):
    """Transform screen coordinates to world coordinates"""
    vect=numpy.concatenate((vect,(1.,)))
    return numpy.dot(TI,vect).tolist()[0:2]


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

