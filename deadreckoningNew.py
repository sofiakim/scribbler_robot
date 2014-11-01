from util import *
import time
import threading
import math
DISTANCE_PER_COUNT = 0.49833887#Millimeters
ROBOT_DIAMETER = 142.5#Measurement in millimeters
DEFAULT_DIGITS = 6
PRINT_COORDINATES = False
UPDATE_INTERVAL = 0.1#Seconds
SPEED_CHANGE_SENSITIVITY = 2#in number of update intervals, lower = more sensitive
runThread = True

x_pos = 0.0#In millimeters
y_pos = 0.0#In millimeters
robotHeading = 0.0
moveHistory = []
beginTime = time.time()
previousTime = time.time()
lastMove = 0#number of update intervals ago

#resets coordinates
def reset_deadReckoning():
    global x_pos, y_pos, robotHeading, moveHistory, beginTime, previousTime
    x_pos = 0.0
    y_pos = 0.0
    robotHeading = 0.0
    moveHistory = []
    beginTime = time.time()
    previousTime = time.time()
    get_encoders(False)

#initializes dead reckoning odometry thread
def initialize_deadReckoning():
    '''initializes dead reckoning odometry thread'''    
    global runThread
    reset_deadReckoning()
    runThread = True
    dRThread = threading.Thread(target=deadReckoningThread)
    dRThread.start()

#dead reckoning thread
def deadReckoningThread():
    '''dead reckoning odometry thread'''
    global previousTime, lastMove
    while runThread:
        update()
        #lastMove += 1
        #if(len(moveHistory)>SPEED_CHANGE_SENSITIVITY and not withinError(getAverageSpeedSinceLastChange(SPEED_CHANGE_SENSITIVITY),getRecentAverageSpeed(SPEED_CHANGE_SENSITIVITY))):
            #lastMove = 0
        previousTime = time.time()
        if(PRINT_COORDINATES):
            getCoords(DEFAULT_DIGITS)
        time.sleep(max(0.0,UPDATE_INTERVAL-time.time()+previousTime))

#updates the position
def update():
    global x_pos, y_pos, robotHeading
    encoders = get_encoders(False)#gets number of encoder counts and reset it to 0
    distanceLeft = float(encoders[0])*DISTANCE_PER_COUNT/2.0#gets distance travelled by left wheel
    distanceRight = float(encoders[1])*DISTANCE_PER_COUNT/2.0#gets distance travelled by right wheel
    delta_t=time.time()-previousTime
    moveHistory.append([distanceLeft*0.001,distanceRight*0.001,delta_t])
    #state['trail']=distanceLeft*0.001,distanceRight*0.001
    cosCurrentAngle = math.cos(robotHeading)#cosine of current angle
    sinCurrentAngle = math.sin(robotHeading)#sine of current angle
    if(encoders[0]==encoders[1]):#if the distances are equal (robot is going straight)
        x_pos += distanceLeft * sinCurrentAngle#xPos global coordinate is updated
        y_pos += distanceLeft * cosCurrentAngle#yPos global coordinate is updated
    else:
        distRatio = ROBOT_DIAMETER * (distanceLeft + distanceRight) / 2.0 / (distanceRight - distanceLeft)#ratio modifier
        distDiff = distanceRight - distanceLeft#difference between distances travelled by left and right wheels
        x_pos += distRatio * (math.cos(distDiff/ROBOT_DIAMETER+robotHeading)-cosCurrentAngle)#updates global coordinate x
        y_pos += distRatio * (math.sin(distDiff/ROBOT_DIAMETER+robotHeading)-sinCurrentAngle)#updates global coordinate y
        robotHeading += distDiff/ROBOT_DIAMETER#updates current robot heading
    while robotHeading > math.pi:
        robotHeading -= 2*math.pi
    while robotHeading < -math.pi:
        robotHeading += 2*math.pi
    #state['where']=getX(),getY(),getHeading()

def stopThread():
    global runThread
    runThread = False

#gets coordinates
def getCoords(numberOfDigits=DEFAULT_DIGITS):
    print "(" + str(round(x_pos*0.001,numberOfDigits)) + "," + str(round(y_pos*0.001,numberOfDigits)) + " at angle "+str(round(robotHeading,numberOfDigits))+")"

def withinError(a,b,maxRelativeError):
    if((b-a)/a<maxRelativeError):
        return True
    else:
        return False

def getX():
    return x_pos*0.001

def getY():
    return y_pos*0.001

def getHeading():
    return (robotHeading+3*math.pi/2)%(2*math.pi)-math.pi

def getSpeed(move):
    return (move[0]+move[1])/2.0/move[2]

def convMoveListToSpeed(moveList):
    speedList = []
    for move in moveList:
        speedList.append(getSpeed(move))
    return speedList

def getAverageSpeedSinceLastChange(begin):
    speedList = convMoveListToSpeed(getMoveHistory(begin,lastMove))
    sumSpeed = 0.0
    for speed in speedList:
        sumSpeed += speed
    sumSpeed /= float(len(speedList))
    return sumSpeed

def getRecentAverageSpeed(numberOfMoves):
    speedList = convMoveListToSpeed(getMoveHistory(0,numberOfMoves+1))
    sumSpeed = 0.0
    for speed in speedList:
        sumSpeed += speed
    sumSpeed /= float(len(speedList))
    return sumSpeed

def getMoveExpected(time):
    pass#to be edited

def arcLengthToTime(arcLengthLeft,arcLengthRight):#Will use a constant motor value of 1 for now
    pass#to be edited

def getMoveHistory(begin=0,end=None):#returns in reverse chronological order, end is exclusive
    '''returns list of (left_arclength,right_arclength) in reverse chronological order'''
    output = []
    if end is None:
        end=len(moveHistory)
    for i in range(len(moveHistory)-1-begin,len(moveHistory)-1-end,-1):
        output.append(moveHistory[i])
    return output

if __name__=='__main__':
    xp_initialize()
