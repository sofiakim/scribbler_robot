PYTHON=lib/python
run: data photos htdigest lib/python static/js/jquery-1.10.2.min.js kill
	trap 'make kill' EXIT; lib/python interface.py
data:
	mkdir data
photos:
	mkdir photos
demo: 
	$(PYTHON) model.py
kill:
	ps ax | fgrep " python $(PWD)/lib/root/lib/python2.4/site-packages/myro/simulator.py" | grep '^ *[0-9][0-9]*  *[^ ][^ ]*  *[^ ][^ ]*  *[0-9][0-9]*:[0-9][0-9]* python /' | awk '{print $$1}' | xargs kill 2>/dev/null || :
lib/python: 
	$(MAKE) -C lib libs
data.pickle:
	$(PYTHON) record-data.py data.pickle
prior.pickle: data.pickle make-prior.py
	./make-prior.py data.pickle prior.pickle
htdigest:
	#htdigest -c htdigest scribbler-commander admin
	echo 'admin:scribbler-commander:804b8a49d3abab8a63add62612942f6a' > htdigest
.PHONY: run kill demo
.PRECIOUS: data.pickle
