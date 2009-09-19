#!/usr/bin/env python

import math
import cairo
from random import *

WIDTH, HEIGHT = 640, 400

surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, WIDTH, HEIGHT)
ctx = cairo.Context (surface)

ctx.scale (WIDTH/1.0, HEIGHT/1.0) # Normalizing the canvas

# draw white background
ctx.set_source_rgb(1,1,1)
ctx.rectangle(0,0,1,1)
ctx.fill()

N = 500 # Number of blobs
rmin = 0.01 # max blob radius
rmax = 0.05 # min blob radius
sepmin = 0.005 # mimimum distance between blobs

safe_distance = rmax + rmax + sepmin

# Select blue colour
ctx.set_source_rgb(0,0,1)
	
# Create N blobs
x = []
y = []
r = []
for n in range(N):
	# Create new blob
	x.append(random())
	y.append(random())
	r.append(rmin + (rmax-rmin)*random())
	
# Grow or move all existing blobs
for i in range(n):
	for j in range(n):
		if i!=j and abs(x[j]-x[i])<safe_distance and abs(y[j]-y[i])<safe_distance: #and sqrt((x[j]-x[i])^2 + (y[j]-y[i])^2)
			d = math.sqrt((x[j]-x[i])**2 + (y[j]-y[i])**2)
			rsum = r[i] + r[j] + sepmin
			if rsum > d:
				r[i] = r[i] - (rsum-sepmin)/2
				r[j] = r[j] - (rsum-sepmin)/2

for n in range(5):
	#ctx.arc(x[n], y[n], r[n], 0, 2*math.pi)
	ctx.set_source_rgb(1.0, 0, 0)
	ctx.rectangle(int(14*random())/14.0, (1+n)/6.0, int(4*random())/14.0, 1/6.0)
	ctx.fill()

#for n in range(N):
#	print x[n], y[n]
#	radius = 0.01 + 0.02 * random()
#	distance = 0.4 * random()
#	ctx.set_source_rgb(0.5, random(), 0.5)
#	angle = random() * 2 * math.pi
#	ctx.arc(0.5 + distance * math.cos(angle), 0.5 + distance * math.sin(angle), radius, 0, 2*math.pi)
#	ctx.fill()

surface.write_to_png ("tt.png") # Output to PNG

