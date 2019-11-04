"""Gathering Billboard Hot 100 chart data using billboard.py API"""

import numpy as np
import billboard
import time
import sys
import csv

reload(sys)
sys.setdefaultencoding('utf8')

# Start retrieval from mid 1958 to the end of 2012
date_range=2012-1958+1
old_day=0
old_month=0

chart_dict={}

# Iterate over the weeks of each year with checks for the month and when a leap year occurs
# Query billboard.py using date and store in dict 
for i in xrange(0,date_range):
	for j in xrange(1,13):

		# Month checks 
		if ((j==1) or (j==3) or (j==5) or (j==7) or (j==8) or (j==10) or (j==12)):
			month=31
		elif ((j==4) or (j==6) or (j==9) or (j==11)):
			month=30
		else:
			if ((i+1958)%4):
				month=28
			else:
				month=29

		# The online records only begin in August of 1958
		if (i==0 and j<8):
			continue
		elif (i==0 and j==8):
			start=4
		# Billboard skipped a week in 1962 when they reverted the day of release to Saturday
		# See https://en.wikipedia.org/wiki/List_of_Billboard_Hot_100_number-one_singles_of_1962
		elif (i==4 and j==1):
			start=6
		else:
			start=old_day+7-old_month
		for k in xrange(start,month+1,7):
			if (j<10):
				j_string=str(0)+str(j)
			else:
				j_string=str(j)
			if (k<10):
				k_string=str(0)+str(k)
			else:
				k_string=str(k)
			date=str(1958+i)+'-'+j_string+'-'+k_string
			try:
				chart_dict[date]=billboard.ChartData('hot-100',date)
			except:
				print(date)
				continue
			time.sleep(2+np.random.randint(2))
		old_day=k
		old_month=month

# Write record to file, 100 songs in each weekly record
with open('data/chart_record.tsv','wb') as csvfile:
	writer=csv.writer(csvfile,delimiter='\t')
	writer.writerow(['date','position','artist','title','last','peak','week'])
	for record in chart_dict.iteritems():
		date=record[0]
		for song in record[1]:
			try:
				title=song.title
				artist=song.artist
				position=song.rank
				peak=song.peakPos
				last=song.lastPos
				week=song.weeks
				writer.writerow([date,position,artist,title,last,peak,week])
			except:
				continue
	
