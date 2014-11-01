from util import *
import math
xp_initialize()
robot.setIRPower(146)
get_obstacle(7)
lambd=math.exp(-1./5)
#lambd=0.
val=0.
while True:
	val=lambd*val+(1-lambd)*get_obstacle('center')
	x=int(val)
	print '\x1b[%dm%s\x1b[0m'%(31+(x>=0),'#'*(abs(x)/40))
