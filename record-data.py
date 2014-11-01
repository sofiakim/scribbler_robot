"""records IR sensor data"""
from util import *
from sys import argv
from pickle import dump
from time import time
f=open(argv[1],'w')
xp_initialize()
out=[]
for irp in xrange(122,147,3):
	robot.setIRPower(irp)
	get_obstacle(7)
	while True:
		data=[]
		raw_input('press enter to start %d: '%irp)
		try:
			start=time()
			end=start+50
			motors(-.1,-.1)
			while True:
				t1=time()
				val=get_obstacle('center')
				t2=time()
				data.append({
					't':(t1+t2)/2-start,
					'v':val,
				})
				if t2>=end:
					break
			stop()
			print'ir power:',irp,'samples:',len(data)
			break
		except KeyboardInterrupt:
			stop()
	out.append({
		'irp':irp,
		'data':data,
	})
	f.seek(0)
	dump(out,f)
	f.flush()
f.close()
