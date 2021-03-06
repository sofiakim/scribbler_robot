#!/usr/bin/env python
import numpy # currently unused, should be used for optimization
from math import hypot, atan2
from heapq import *
import threading # might not be necessary if thread not started here
#import util # needed for state object
from time import sleep
from model import Map,Prior
from movement import pi, SCRIBBLER_RADIUS

obstaclemap = Map(Prior(), 40, 40) # XXX dimensions and initial P (currently grid points every 10 cm)

def set_target(xy):
    '''sets the target to x, y
    returns immediately'''
    newtarget = xy

# NOTES:
# - call set_target on a target point (grid coords -- not real coords)
#   to set the target of the A*
# - once A* finishes, the result path of coordinates is in 
#	util.state["pathpoints"]
#
# - TODO `cost` and `neighbors` do special things based on the map data -- 
#   some integration still needs doing
#

"""
newtarget is None when there is no A* to do, 
is equal to finish when the A* is being done,
and is not equal to finish when the A* has to 
be restarted with a new target.
"""
newtarget = None

start = util.state["where"][0],util.state["where"][1]
finish = None

# XXX all of these should probably be stored in state
closedset = set([])
camefrom = {}
g_score = {start:0} # best known cost from start

def resetAstar(new_start, new_finish):
    """
    Reset the A* search space to do a search from given start position 
    to given end position, return the generator object
    """
    
    global start, finish, openset, closedset, camefrom, g_score, f_score
    start, finish = new_start, new_finish
    closedset = set([])
    camefrom = {}
    util.state["pathpoints"] = []
    if new_finish is None or new_start is None:
        return None
    openset = [(cost(start, finish), start)]
    g_score = {start:0} # best known cost from start
    f_score = {start:cost(start,finish)} # estimated total cost to target
    return astar().next # returns generator's next function


def cost((x1,y1),(x2,y2)): 
    """
    Returns the equivalent distance between two given points.

    XXX Here is where the obstacle sensor comes in
    """
    # XXX needs to check obstacle probability to evaluate cost
    # XXX use obstaclemap.p
    # XXX currently doesn't check edge cases (or even negative indices)
    
    return hypot(x1-x2,y1-y2)/(1-obstaclemap.p[x2][y2]) 
#	ignores prior path length (that's what A* is for)
#   gonna get ugly -- 
#   scales equivalent distance up with probability of obstacle at target
#   not quite it, will figure tomorrow :D

openset = [(cost(start, finish), start)]
f_score = {start:cost(start,finish)} # estimated total cost to target

# XXX global pathpoints for debugging
#pathpoints = []
iterastar = None

@util.every(50) # has to be turned back into threaded
def pathfinderThread():
    """The thread that continually waits on target change and 
    runs A* whenever a new target is set"""
    global iterastar, pathpoints
    # stuff happens
    if newtarget != finish:
	    start = util.state["where"][:2]
        # we currently scrap partial paths, which might be useful, 
        # but that's okay.
        iterastar = resetAstar(start,newtarget)
    if newtarget != None and iterastar != None:
        try:
            # step once thru A*
            iterastar()
        except StopIteration:
            # A* finished, so we update state
            util.state["pathpoints"] = trace_path(start, finish)
            newtarget = None
            iterastar = None

definitely_obstacle = 0.85
def neighbors(x,y=None):
    """
    Generates all neighbors of input location.
    We use a genexpr to produce neighbors because there may be important 
    edge cases best handled before the neighbors are even created

    XXX another place the sensors can come in
    """
    if isinstance(x,tuple): x,y = x[0], x[1]
    # XXX needs to check bounds to decide which neighbors get yielded
    canleft, canright, canup, candown = x>0,x<obstaclemap.w-1,y>0,y<obstaclemap.h-1
    
    if canright:
        if canup: yield (x + 1, y - 1)
        yield (x + 1, y)
        if candown: yield (x + 1,y + 1)
    if candown: yield (x, y + 1)
    if canleft:
        if candown: yield (x - 1, y + 1)
        yield (x - 1, y)
        if canup: yield (x - 1, y - 1)
    if canup: yield (x, y - 1)


# pauses to yield current best subtarget

# this A* is completely transparent in its workings so it can be 
# interrupted with incomplete path if need be

def astar():
    """
    computes A* over an arbitrary graph generated by neighbors() 
    and weighted by cost()
    """
    done = 0
    while openset and not done:
        current = heappop(openset)
        yield current # produces current best target, and distance to final target
        if current[1] == finish:
            #DONE DONE DONE
            done = True
            continue
            #break
        closedset.add(current[1])
        for i in neighbors(current[1]):
            tentative_g = g_score[current[1]] + cost(current[1],i)
            tentative_f = tentative_g + cost(i,finish)
            if i in closedset and tentative_f >= f_score[i]:
                continue
            if i not in openset or tentative_f < f_score[i]:
                camefrom[i] = current[1]
                g_score[i] = tentative_g
                f_score[i] = tentative_f
                if i not in openset:
                    heappush(openset, (tentative_f,i))

def trace_path(src, dest):
    """
    Iterate backwards from dest, following came-from links until 
    reaching src. Returns list of points on the path, starting at src, 
    ending at dest.
    """
    path = [dest]
    cur = camefrom[dest]
    while cur != src:
        #print cur
        path.append(cur)
        cur = camefrom[cur]
    return [(obstaclemap.x[i[0]], obstaclemap.y[i[1]]) for i in reversed(path)]


def arclength_turn(theta):
	"""
	Returns a pair [left, right] describing how far forward each wheel 
	must move to turn by angle theta CCW
	"""
	return (-theta*SCRIBBLER_RADIUS,theta*SCRIBBLER_RADIUS)

def path_to_arclengths(path):
	p = util.state["where"]
	out = []
	heading = p[2]
	cur = p[:2]
	for dest in path[1:]: 
		# turn to target
		turnby = atan2(dest[0]-cur[0],dest[1]-cur[1])-heading
		out.append(arclength_turn(turnby))
		heading += turnby
		# move to target
		dist = hypot(dest[0]-cur[0], dest[1]-cur[1])
		out.append((dist,dist))
		cur = dest
	return out


def findloops(graph):
    """
    A utility function for checking for problems in an A* came-from tree
    """
    for i in graph.keys():
        j = graph[i]
        l = []
        while j in graph.keys():
            if j in l:
                print "AHAHA " + str(l)
                break
            l.append(j)
            j = graph[j]

"""
pathfinder = astar()
for i in pathfinder:
#   print i
    pass
print "##"
for i in trace_path(start, finish):
    print i
print "###"
#print camefrom[(4,3)]
#print camefrom[(4,4)]
#print camefrom[(0,0)]
print "####"
findloops(camefrom)
"""

if __name__ == "__main__":
    set_target((30,30))
    print "stuff happens"
    
    input()
    
    
