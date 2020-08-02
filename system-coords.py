#!/usr/bin/env python

import csv, json, re, requests, sys, urllib

edsm_url = 'https://www.edsm.net/api-v1/system'

if len(sys.argv) < 2:
	print 'usage: %s <system list csv>' % sys.argv[0]
	sys.exit()

map_data = { "markers": []}

with open(sys.argv[1]) as csvfile:
	reader = csv.reader(csvfile)
	for row in reader:
		# system_name = urllib.quote(re.split('[ A-Z]+$', row[1])[0])
		system_name = re.split('[ A-Z]+$', row[1])[0]
		# print '%s\t%s\t%s' % (row[0], row[1], system_name)
		resp = requests.get(url=edsm_url, params=dict(systemName=system_name, showCoordinates=1))
		data = resp.json()
		if data == []:
			data = { "coords": {'x': 0, 'y': 0, 'z': 0}}

		# print json.dumps(data)
		# print

		map_data['markers'].append(
			{
			"pin" : "blue",
			"text" : "%s: %s" % (row[1], row[0]),
			"x" : data['coords']['x'],
			"y" : data['coords']['y'],
			"z" : data['coords']['z'] 
        })

print json.dumps(map_data,indent=2)
