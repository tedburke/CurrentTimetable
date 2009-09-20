#!/usr/bin/env python

import subprocess
import re
import math
import cairo
from random import *

class Entry:
	"""A timtable entry"""
	def __init__(self, html_table_row):
		elements = re.findall('<td class="gridData">(.*?)</td>',html_table_row,re.DOTALL)
		if elements[2] == 'Mon':
			self.day = 0
		elif elements[2] == 'Tue':
			self.day = 1
		elif elements[2] == 'Wed':
			self.day = 2
		elif elements[2] == 'Thu':
			self.day = 3
		elif elements[2] == 'Fri':
			self.day = 4
		self.start = elements[3]
		start_hm = re.findall('\d\d',self.start)
		self.start_hour = int(start_hm[0])
		self.start_minute = int(start_hm[1])
		self.finish = elements[4]
		finish_hm = re.findall('\d\d',self.finish)
		self.finish_hour = int(finish_hm[0])
		self.finish_minute = int(finish_hm[1])
		self.room = elements[5]
		self.module_name = elements[8]
		self.row = 0
		print('Day ' + str(self.day) + ' ' + self.start + '-' + self.finish + ' ' + self.module_name + ' Room ' + self.room)

class Day:
	"""This class stores the timetable entries and other properties for one day of the week"""
	def __init__(self):
		self.entries = []
		self.first_row = 0
		self.maxrow = 0

# Login to webtimetables.dit.ie
subprocess.call("wget --output-document=dummy.html --save-cookies=cookie.txt --keep-session-cookies --post-data \"reqtype=login&type=null&appname=unknown&appversion=unknown&username=Student%20Engineering&userpassword=engineering\" \"http://webtimetables.dit.ie/TTSuiteRBLIVE/PortalServ\"", shell=True)

# Retrieve timetable - i.e. "grid"/list for DT021 /1, week 4
subprocess.call("wget --output-document=dt021-1.html --cookies=on --load-cookies=cookie.txt --keep-session-cookies --save-cookies=cookie.txt \"http://webtimetables.dit.ie/TTSuiteRBLIVE/PortalServ?reqtype=timetable&action=getgrid&sType=class&sKey=200910|DT021|DT021/1|1&sTitle=BE%20in%20Electrical/Electronic%20Engineering&sYear=1&sWeeks=4&namevalue=BE%20in%20Electrical/Electronic%20Engineering&instCode=-2&instName=\"", shell=True)

# Logout of webtimetables.dit.ie
subprocess.call("wget --output-document=dummy.html --cookies=on --load-cookies=cookie.txt --keep-session-cookies --save-cookies=cookie.txt \"http://webtimetables.dit.ie/TTSuiteRBLIVE/PortalServ?reqtype=logout\"", shell=True)

# Retrieve HTML file
subprocess.call("wget --output-document=tt.html --save-cookies=cookie.txt --keep-session-cookies --post-data \"reqtype=login&type=null&appname=unknown&appversion=unknown&username=Student%20Engineering&userpassword=engineering\" \"http://webtimetables.dit.ie/TTSuiteRBLIVE/PortalServ\"", shell=True)

# Read HTML file contents into a string
html_file = open('dt021-1.html', 'r')
html_content = html_file.read()
html_file.close()

html_table_rows = re.findall('<tr>(.*?)</tr>',html_content,re.DOTALL)
entries = []
for n in range(len(html_table_rows)):
	entries.append(Entry(html_table_rows[n]))
days = []
days.append(Day())
days.append(Day())
days.append(Day())
days.append(Day())
days.append(Day())

for n in range(len(entries)):
	days[entries[n].day].entries.append(entries[n])

for n in range(len(days)):
	print('Day ' + str(n) + ': ' + str(len(days[n].entries)) + ' entries')
	for m in range(len(days[n].entries)):
		for mm in range(m):
			if days[n].entries[m].start_hour < days[n].entries[mm].finish_hour:
				days[n].entries[m].row += 1
				if days[n].entries[m].row > days[n].maxrow:
					days[n].maxrow = days[n].entries[m].row

for n in range(len(days)):
	print('Day ' + str(n) + ': ' + str(days[n].maxrow + 1) + ' rows')
	for m in range(len(days[n].entries)):
		print(days[n].entries[m].start + '-' + days[n].entries[m].finish + ', row ' + str(days[n].entries[m].row))

total_rows = 5
for n in range(len(days)):
	total_rows += days[n].maxrow

print('Total rows = ' + str(total_rows))

quit()

# Extract timetable entries from the HTML string


# Render timetable as bitmap
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

