from pickle import load
from matplotlib.pyplot import *
from sys import argv
from itertools import cycle
from model import Prior
with open(argv[1])as f:
	fig=figure()
	ax=fig.add_subplot(111)
	#clr=iter(cycle('bgrcmykw'))
	clr=iter(cycle('bgrcmyk'))
	for ent in load(f):
		start=ent['data'][0]['t']*1.5-.5*ent['data'][1]['t']
		t=[]
		v=[]
		for sample in ent['data']:
			t.append(sample['t']-start)
			v.append(sample['v'])
		ax.scatter(t,v,c=next(clr),marker='x')
if len(argv)>2:
	with open(argv[2])as f:
		for irp,ent in sorted(load(f).items()):
			ax.errorbar(Prior._times,ent['mu'],yerr=ent['sigma'],fmt='-o')
show()
