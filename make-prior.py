#!/usr/bin/env python
"""generates prior from data"""
if __name__=="__main__":
	from pickle import load,dump
	from sys import argv
	from numpy import *
	from scipy.stats import linregress
	from model import Prior
	data={}
	with open(argv[1])as f:
		for ent in load(f):
			start=ent['data'][0]['t']*1.5-.5*ent['data'][1]['t']
			t=[]
			v=[]
			for sample in ent['data']:
				t.append(sample['t']-start)
				v.append(sample['v'])
			t=array(t)
			v=array(v)
			errors=zeros(Prior._N+1)
			counts=zeros(Prior._N+1)
			vals=[]
			for j,(start,end)in enumerate(zip(Prior._times,Prior._times[1:])):
				i=(start<=t)&(t<end)
				count=i.sum()
				m_t,b_t,_,_,sigma_t=linregress(arange(len(t))[i],t[i])
				m_v,b_v,r,_,sigma_v=linregress(t[i],v[i])
				sigma_t=std(t[i]-(b_t+m_t*arange(len(t))[i]))#XXX do not recompute
				sigma_v=std(v[i]-(b_v+m_v*t[i]))#XXX do not recompute
				var_t=(sigma_t*m_v)**2*(1-r**2)#basically 0
				var_v=sigma_v**2+1e-1
				var=(var_t+var_v)*count
				vals.append((m_v*start+b_v,m_v*end+b_v,count))
				errors[j]+=.5*var
				errors[j+1]+=.5*var
				counts[j]+=.5*count
				counts[j+1]+=.5*count
			sigma=(errors/counts)**.5

			mu=zeros(Prior._N+1)
			for i,(left,right,w)in enumerate(vals):
				mu[i]+=.5*left*w
				mu[i+1]+=.5*right*w
			mu/=counts
			data[ent['irp']]={
				'mu':map(float,mu),
				'sigma':map(float,sigma),
			}
	with open(argv[2],'w')as f:
		dump(data,f)
