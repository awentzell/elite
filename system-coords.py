#!/usr/bin/env python

import csv, json, re, requests, sys
from datetime import datetime, timedelta

edsm_systems_url = 'https://www.edsm.net/api-v1/systems'

if len(sys.argv) < 2:
	print 'usage: %s <system list csv>' % sys.argv[0]
	sys.exit()

markers = {}

with open(sys.argv[1]) as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		# state tracker
		marker_placed = False

		# skip entries newer than 60 days
		if datetime.today() - datetime.strptime(re.split('T', row['timestamp'])[0], '%Y-%m-%d') < timedelta(days=60):
			continue

		# make sure we have the name of the system, not a star
		system_name = re.split('[ A-Z]+$', row['system'])[0]

		# is this another codex entry in an already-marked system?
		if system_name in markers:
			markers[system_name]['text'] += "\n%s: %s"  % (row['system'], row['name'])
			marker_placed = True
		else:
			# is this a known system to EDSM?
			resp = requests.get(url=edsm_systems_url, params=dict(systemName=system_name, showCoordinates=1))
			data = resp.json()

			if len(data) > 0:
				for entry in data:
					# we got a response, but some entries may be missing coordinates
					if 'coords' in entry and not marker_placed:
						markers[system_name] = {
							"pin" : "blue",
							"text" : "%s: %s" % (row['system'], row['name']),
							"x" : entry['coords']['x'],
							"y" : entry['coords']['y'],
							"z" : entry['coords']['z']
						}
						marker_placed = True
			else:
				# system was not found, let's try the sector
				proc_gen_sector_name = re.split(' [A-Z].-[A-Z]', system_name)[0]

				if proc_gen_sector_name:
					if proc_gen_sector_name in markers:
						# marker for this sector exists; only add this entry's system/codex entry info
						markers[proc_gen_sector_name]['text'] += "\n%s: %s"  % (row['system'], row['name'])
						marker_placed = True
					else:
						# no sector marker exists yet; get coords from any system in-sector
						resp = requests.get(url=edsm_systems_url, params=dict(systemName=proc_gen_sector_name, showCoordinates=1))
						data = resp.json()

						if len(data) > 0:
							for entry in data:
								if 'coords' in entry and not marker_placed:
									# add new marker with system/codex entry info
									markers[proc_gen_sector_name] = {
										"pin" : "blue",
										"text" : "%s: %s" % (row['system'], row['name']),
										"x" : entry['coords']['x'],
										"y" : entry['coords']['y'],
										"z" : entry['coords']['z']
									}
									marker_placed = True

		if not marker_placed:
			# couldn't find system/sector or its coords; add to catch-all marker
			if 'unknown' in markers:
				markers['unknown']['text'] += "\n%s: %s"  % (row['system'], row['name'])
			else:
				markers['unknown'] = {
					"pin" : "red",
					"text" : "%s: %s" % (row['system'], row['name']),
					"x" : -32000,
					"y" : 0,
					"z" : -19000
				}

# print marker data without dict keys, for EDastro format
print json.dumps({"markers" : markers.values()})
