#!/usr/bin/env python

import subprocess
import re
import math
import cairo
from random import *
import os, time

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
		elif elements[2] == 'Sat':
			self.day = 5
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
		self.max_row = 0

def render_timetable(input_filename, output_filename, title):
	# Read HTML file contents into a string
	html_file = open(input_filename, 'r')
	html_content = html_file.read()
	html_file.close()

	# Extract timetable entries from HTML table
	html_table_rows = re.findall('<tr>(.*?)</tr>',html_content,re.DOTALL)
	entries = []
	min_hour = 24
	max_hour = 0
	for n in range(len(html_table_rows)):
		entries.append(Entry(html_table_rows[n]))
		if entries[n].day > 4:
			entries.pop()
			continue
		if entries[n].finish_hour > max_hour:
			max_hour = entries[n].finish_hour
		if entries[n].start_hour < min_hour:
			min_hour = entries[n].start_hour

	# Create array of days
	days = []
	days.append(Day())
	days.append(Day())
	days.append(Day())
	days.append(Day())
	days.append(Day())

	# Divide up the entries into the five days
	for n in range(len(entries)):
		days[entries[n].day].entries.append(entries[n])

	# Determine the number of rows needed for each day
	# in the timetable (due to concurrent classes)
	for n in range(len(days)):
		print('Day ' + str(n) + ': ' + str(len(days[n].entries)) + ' entries')
		for m in range(len(days[n].entries)):
			for mm in range(m):
				if days[n].entries[m].start_hour < days[n].entries[mm].finish_hour:
					days[n].entries[m].row += 1
					if days[n].entries[m].row > days[n].max_row:
						days[n].max_row = days[n].entries[m].row

	# Print out info gleaned so far, just for debugging
	for n in range(len(days)):
		print('Day ' + str(n) + ': ' + str(days[n].max_row + 1) + ' rows')
		for m in range(len(days[n].entries)):
			print(days[n].entries[m].start + '-' + days[n].entries[m].finish + ', row ' + str(days[n].entries[m].row))

	# Calculate the number of rows needed for all five days together
	for n in range(1,len(days)):
		days[n].first_row = days[n-1].first_row + days[n-1].max_row + 1

	total_rows = days[n].first_row + days[n].max_row + 1
	total_hours = max_hour - min_hour
		
	print('Total rows = ' + str(total_rows))
	print('total_hours=' + str(total_hours) + ' ' + 'min_hour=' + str(min_hour) + ' max_hour=' + str(max_hour))

	# Render timetable as bitmap
	#image_width, image_height = 1024, 768
	image_width, image_height = 1280, 1024
	surface = cairo.ImageSurface (cairo.FORMAT_ARGB32, image_width, image_height)
	ctx = cairo.Context (surface)

	# draw white background
	ctx.set_source_rgb(1,1,1)
	ctx.rectangle(0,0,image_width,image_height)
	ctx.fill()

	# Timetable grid drawing properties
	header_font_size = 40
	day_label_font_size = 18
	entry_font_size = 14
	time_font_size = 14
	clearance = 5
	ctx.set_line_width(1)
	ctx.select_font_face("Arial", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
	# Calculate width of widest day label
	day_margin = 0
	ctx.set_font_size(day_label_font_size)
	for d in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
		if ctx.text_extents(d)[2] > day_margin:
			day_margin = ctx.text_extents(d)[2]
	day_margin *= 1.8
	row_height = (image_height)/(total_rows + 1.5) # Extra 0.1 is for small gap at bottom of page
	hour_width = (image_width - day_margin)/(total_hours + 0.25)

	# Draw timetable header
	ctx.set_source_rgb(0,0,0)
	ctx.set_font_size(header_font_size)
	x_bearing, y_bearing, text_width, text_height = ctx.text_extents(title)[:4]
	ctx.move_to(3*clearance - x_bearing, 3*clearance - y_bearing)
	ctx.show_text(title)
	
	# Display last refresh time
	refresh_time = "Last downloaded: " + time.strftime("%H:%M %d-%m-%Y", time.localtime(os.stat(input_filename).st_mtime))
	ctx.set_font_size(day_label_font_size)
	x_bearing, y_bearing, text_width, text_height = ctx.text_extents(refresh_time)[:4]
	ctx.move_to(image_width - text_width - 3*clearance - x_bearing, 3*clearance - y_bearing)
	ctx.show_text(refresh_time)

	# Draw time labels
	ctx.set_font_size(time_font_size)
	for h in range(min_hour, max_hour + 1):
		x_bearing, y_bearing, text_width, text_height = ctx.text_extents(str(h) + ':00')[:4]
		ctx.move_to(day_margin + (h - min_hour)*hour_width - text_width/2 - x_bearing, row_height - text_height - y_bearing - clearance)
		ctx.show_text(str(h) + ':00')

	# Draw timetable grid
	for n in range(len(days)):
		# Draw background colour for this day
		if n%2:
			ctx.set_source_rgb(0.8,0.8,1)
		else:
			ctx.set_source_rgb(0.5,0.5,1)
		left = 0
		top = (1 + days[n].first_row) * row_height
		width = image_width #(1 + max_hour) * hour_width
		height = (days[n].max_row + 1) * row_height
		ctx.rectangle(left,top,width,height)
		ctx.fill()
		
		# Draw label for this day
		if n == 0: d = 'Mon'
		elif n == 1: d = 'Tue'
		elif n == 2: d = 'Wed'
		elif n == 3: d = 'Thu'
		elif n == 4: d = 'Fri'
		ctx.set_source_rgb(0,0,0)
		ctx.set_font_size(day_label_font_size)
		x_bearing, y_bearing, text_width, text_height = ctx.text_extents(d)[:4]
		ctx.move_to(day_margin/2 - text_width/2 - x_bearing, top + height/2 - text_height/2 - y_bearing)
		ctx.show_text(d)
		
		# Draw entries for this day
		ctx.set_font_size(entry_font_size)
		for m in range(len(days[n].entries)):
			# entry box
			left = day_margin + (days[n].entries[m].start_hour - min_hour)*hour_width
			top = (1 + days[n].first_row + days[n].entries[m].row)*row_height
			width = (days[n].entries[m].finish_hour - days[n].entries[m].start_hour)*hour_width
			height = row_height
			ctx.rectangle(left,top,width,height)
			ctx.stroke()
			# entry text
			top += clearance
			left += clearance
			mod_name = days[n].entries[m].module_name
			while ctx.text_extents(mod_name)[2] > width - 2*clearance:
				# Print as much of mod_name as will fit on one line
				cut_point = 0
				while ctx.text_extents(mod_name[:cut_point+1])[2] < width - 2*clearance:
					cut_point += 1
				ctx.move_to(left, top)
				x_bearing, y_bearing, text_width, text_height = ctx.text_extents(mod_name[:cut_point])[:4]
				ctx.move_to(left - x_bearing, top - y_bearing)
				ctx.show_text(mod_name[:cut_point])
				mod_name = mod_name[cut_point:]
				top += entry_font_size
			# Print the remaining part of mod_name
			ctx.move_to(left, top)
			x_bearing, y_bearing, text_width, text_height = ctx.text_extents(mod_name)[:4]
			ctx.move_to(left - x_bearing, top - y_bearing)
			ctx.show_text(mod_name)
			top += entry_font_size
			room = days[n].entries[m].room
			ctx.move_to(left, top)
			x_bearing, y_bearing, text_width, text_height = ctx.text_extents(room)[:4]
			ctx.move_to(left - x_bearing, top - y_bearing)
			ctx.show_text(room)
			top += entry_font_size
			start_finish = days[n].entries[m].start + '-' + days[n].entries[m].finish
			ctx.move_to(left, top)
			x_bearing, y_bearing, text_width, text_height = ctx.text_extents(start_finish)[:4]
			ctx.move_to(left - x_bearing, top - y_bearing)
			ctx.show_text(start_finish)
	
	# Finally, write the timetable image to a PNG file
	surface.write_to_png (output_filename) # Output to PNG

# Now, here's the script to actually generate the timetables

# Login to webtimetables.dit.ie
subprocess.call("wget --output-document=dummy.html --save-cookies=cookie.txt --keep-session-cookies --post-data \"reqtype=login&type=null&appname=unknown&appversion=unknown&username=Student%20Engineering&userpassword=engineering\" \"http://webtimetables.dit.ie/TTSuiteRBLIVE/PortalServ\"", shell=True)

# Find out what week it is
subprocess.call("wget --output-document=week.html --cookies=on --load-cookies=cookie.txt --keep-session-cookies --save-cookies=cookie.txt \"http://webtimetables.dit.ie/TTSuiteRBLIVE/PortalServ?reqtype=weekstructure\"", shell=True)

# Read HTML file contents into a string
html_file = open('week.html', 'r')
html_content = html_file.read()
html_file.close()
week_number = re.findall('This week is week number (\d*)', html_content, re.DOTALL)
week_number = week_number[0]
week_number = '4'

# Retrieve timetable - i.e. "grid"/list for DT021 years 1 to 4, for this week
for year in range(1,5):
	subprocess.call("wget --output-document=DT021-" + str(year) + ".html --cookies=on --load-cookies=cookie.txt --keep-session-cookies --save-cookies=cookie.txt \"http://webtimetables.dit.ie/TTSuiteRBLIVE/PortalServ?reqtype=timetable&action=getgrid&sType=class&sKey=200910|DT021|DT021/" + str(year) + "|" + str(year) + "&sTitle=BE%20in%20Electrical/Electronic%20Engineering&sYear=" + str(year) + "&sWeeks=" + week_number + "&namevalue=BE%20in%20Electrical/Electronic%20Engineering&instCode=-2&instName=\"", shell=True)

# Retrieve timetable - i.e. "grid"/list for DT009 years 1 to 3, for this week
for year in range(1,4):
	subprocess.call("wget --output-document=DT009-" + str(year) + ".html --cookies=on --load-cookies=cookie.txt --keep-session-cookies --save-cookies=cookie.txt \"http://webtimetables.dit.ie/TTSuiteRBLIVE/PortalServ?reqtype=timetable&action=getgrid&sType=class&sKey=200910|DT009|DT009/" + str(year) + "|" + str(year) + "&sTitle=BEngTech%20in%20Electrical%20%26%20Control%20Systems&sYear=" + str(year) + "&sWeeks=" + week_number + "&namevalue=BEngTech%20in%20Electrical%20%26%20Control%20Systems&instCode=-2&instName=\"", shell=True)
	
# Logout of webtimetables.dit.ie
subprocess.call("wget --output-document=dummy.html --cookies=on --load-cookies=cookie.txt --keep-session-cookies --save-cookies=cookie.txt \"http://webtimetables.dit.ie/TTSuiteRBLIVE/PortalServ?reqtype=logout\"", shell=True)

# Render timetables
render_timetable("DT021-1.html", "DT021-1.png", "DT021 year 1")
render_timetable("DT021-2.html", "DT021-2.png", "DT021 year 2")
render_timetable("DT021-3.html", "DT021-3.png", "DT021 year 3")
render_timetable("DT021-4.html", "DT021-4.png", "DT021 year 4")
render_timetable("DT009-1.html", "DT009-1.png", "DT009 year 1")
render_timetable("DT009-2.html", "DT009-2.png", "DT009 year 2")
render_timetable("DT009-3.html", "DT009-3.png", "DT009 year 3")

