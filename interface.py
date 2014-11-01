#!/usr/bin/python
import cherrypy
import os
import myro
import util
import sys
import itertools
import shelve
import threading
import simplejson as json
import bisect
import numpy
import datetime
import deadreckoningNew as deadreckoning
util.connect_async()
def ajax(handler):
	return cherrypy.expose(cherrypy.tools.allow(methods=('POST',))(cherrypy.tools.json_out()(handler)))
deltas = []
deltas_change = threading.Condition()
@util.state.watch
def update(*t_key_val):
	try:
		deltas_change.acquire()
		deltas.append(t_key_val)
		deltas_change.notifyAll()
	finally:
		deltas_change.release()
class Subscription(object):
	def __init__(self):
		self.prefix.reverse()
	def __iter__(self):
		return self
	def next(self):
		if self.prefix:
			return elt_to_js(self.prefix.pop())
		while True:
			if self.i < len(deltas):
				self.i += 1
				return elt_to_js(deltas[self.i-1])
			try:
				deltas_change.acquire()
				deltas_change.wait()
			finally:
				deltas_change.release()
class ScribblerCommander(object):
	#photo_delay = 1.#s
	@cherrypy.expose
	def index(self, do):
		# check if action is safe
		if hasattr(self, do):
			handler = getattr(self, do)
			if hasattr(handler, 'exposed') and handler.exposed:
				getattr(self, do)()
		# switch POST to a GET
		raise cherrypy.HTTPRedirect('/')
	@ajax
	def forward(self):
		myro.forward(1)
	@ajax
	def backward(self):
		myro.backward(1)
	@ajax
	def left(self):
		myro.turn(1)
	@ajax
	def right(self):
		myro.turn(-1)
	@ajax
	def stop(self):
		myro.stop()
	@ajax
	def battery(self):
		try:
			return myro.getBattery() / 9.
		except AttributeError:
			raise cherrypy.HTTPError(503, 'Service Unavailable')
	@ajax#XXX handle non-ajax
	#@util.every(10)#XXX debug
	def photo(self=None):
		try:
			deltas_change.acquire()
			if util.state.age('photo') > 1.:
				filename = 'photos/%s.jpg' % datetime.datetime.now().isoformat()
				fd = open(filename, 'w')
				try:
					util.grab_jpeg_color(fd.write, 1)
				finally:
					fd.close()
				util.state['photo'] = {
					'path': filename,
					'x': deadreckoning.getX(),
					'y': deadreckoning.getY(),
					'theta': deadreckoning.getHeading(),
				}
			return util.state['photo']
		finally:
			deltas_change.release()
	@ajax
	def subscribe(self, t=None):
		'''subscribe to events after t'''
		if t is None:
			i = len(deltas)
			cur = dict((key, util.state.history(key)[-1]) for key in util.state)
			j = len(deltas)
			prefix = []
			#hide race conditions
			for t, key, val in deltas[i:j]:
				if t > cur[key][0]:
					cur[key] = t, val
			for key in cur:
				t, val = cur[key]
				prefix.append((key, val, t))
			t = 0
			if j:
				t = deltas[j-1][0]
			return {'t':t, 'deltas':prefix}
		t = float(t)
		while True:#completely different logic
			if deltas and deltas[-1][0] > t:
				i = bisect.bisect_left(deltas, (numpy.nextafter(t, t+1),))
				j = len(deltas)
				return {'t':deltas[j-1][0], 'deltas':[(key, val, t) for (t, key, val) in deltas[i:j]]}
			try:
				deltas_change.acquire()
				deltas_change.wait(25)
			finally:
				deltas_change.release()
			return {'t':t, 'deltas':[]}
	@ajax
	def history(self, key, t=None):
		'''return history before t'''
		if t is None:
			t = float('inf')
		else:
			t = float(t)
		if key in util.state:
			return [elt for elt in util.state.history(key) if elt[0] < t]
		return []
	@ajax
	def set_target(self, x=None, y=None):
		'''sets the pathfinding target'''
		if y is None:
			pathfinder.set_target(None)
		else:
			pathfinder.set_target((x, y))
if __name__=="__main__":
	current_dir = os.path.dirname(os.path.abspath(__file__))
	config = {
		'/' : {
			'tools.staticdir.root' : current_dir,
			'tools.staticfile.root' : current_dir,
			'tools.staticfile.on' : True,
			'tools.staticfile.filename' : 'index.html',
			'tools.staticfile.match' : '^/$', # only match the exact url /
		},
		'/static' : {
			'tools.staticdir.on' : True,
			'tools.staticdir.dir' : 'static',
		},
		'/photos' : {
			'tools.staticdir.on' : True,
			'tools.staticdir.dir' : 'photos',
		},
	}
	auth = {
		'tools.auth_digest.on': False,
		'tools.auth_digest.realm': 'scribbler-commander',
		'tools.auth_digest.get_ha1': cherrypy.lib.auth_digest.get_ha1_file_htdigest('htdigest'),
		'tools.auth_digest.key': 'f5d935a764a2d627',
	}
	config['/'].update(auth)
	config['/photos'].update(auth)
	cherrypy.quickstart(ScribblerCommander(), config=config)
