from myro import *
from math import *

"""wheel speed on carpet in m/s"""
WHEEL_SPEED = 0.15

"""scribbler radius in m"""
SCRIBBLER_RADIUS = 0.075

"""pi"""
PI = 3.14159265359

def moveforward(distance=1, fwd=True):
    """moves forward a certain distance based on speed (0.15 m/s)"""
    if fwd==True:
        f=1
    else:
        f=-1
    forward(f,distance/WHEEL_SPEED)

def turnside(radians=PI, left=True):
    """rotates in a direction (1.99rad/sec)"""
    if radians < 0:
        radians = -radians
        left = not left
    if left:
        d=1
    else:
        d=-1
    turn(d,1,radians/1.99)
        
def circle(radius=0.5, radians=PI, dirleft = True, fwd = True):
    """makes robot move in circle based on radius and degrees"""
    if dirleft:
        d=1
    else:
        d=-1
    if fwd:
        f=1
    else:
        f=-1
    vin = (radius - SCRIBBLER_RADIUS) / (radius + SCRIBBLER_RADIUS)
    move(f*(1+vin)/2,d*(1-vin)/2)
    dist = 1.0*radius*radians
    angvel = (WHEEL_SPEED+WHEEL_SPEED*vin)/2
    wait(dist/angvel)
    stop()

def stuck(repeat=3):
    """goes back and forth to shake out when stuck"""
    if repeat>=0:
        f=1
    else:
        f=-1
        repeat=-repeat
    for _ in xrange(repeat):
        forward(-f,0.5)
        forward(f,1)

def shift(distance=1, left=True):
    """moves sideways and returns to its previous heading"""
    turnside(PI/2,left)
    moveforward(distance)
    if left==True:
        turnside(PI/2,False)
    else:
        turnside(PI/2)

def goto(x=0,y=0,heading=True):
    """goes to a location based on xy co-ordinate"""
    if x==0 and y==0:
        return
    if x>0:
        d=False
    else:
        d=True
        x=-x
    if y>=0:
        f=True
    else:
        f=False
        y=-y
    if x==0:
        if heading==True and f==False:
            turnside()
            moveforward(y)
        else:
            moveforward(y,f)
    else:
        direction = atan(y/x)
        distance = hypot(x,y)
        if d==False and f==True:
            turnside(PI/2-direction,False)
            moveforward(distance)
            if heading==False:
                turnside(PI/2-direction,True)
        elif d==True and f==True:
            turnside(PI/2-direction,True)
            moveforward(distance)
            if heading==False:
                turnside(PI/2-direction,False)
        elif d==False and f==False:
            turnside(PI-(PI/2-direction),False)
            moveforward(distance)
            if heading==False:
                turnside(PI-(PI/2-direction),True)
        elif d==True and f==False:
            turnside(PI-(PI/2-direction),True)
            moveforward(distance)
            if heading==False:
                turnside(PI-(PI/2-direction),False)

if __name__ == "__main__":
    initialize("COM40")
    #while True:
        #print map(getObstacle,xrange(3))
