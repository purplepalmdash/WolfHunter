################################################################################
# This File is for listing all of the defined nodes, which could also viewed by
# `cobbler list`
################################################################################

# Use Cobbler API
import xmlrpclib
# Use bottle, for rendering HTML
from bottle import route, run, debug
# Beautify json output
import json

# Cobbler Server will be used during the lifetime of this file
CobblerServer = xmlrpclib.Server("http://127.0.0.1/cobbler_api")

# Visit http://Your_URL/system will get all of the installed system node name
@route('/system')
def list_system():
	AllSystems = '' 
	for i in CobblerServer.get_systems():
		# i in a dictionary, need to be prettified
		# `print type(i)` result is <type 'dict'>
		# print json.dumps(i, sort_keys=True, indent=4) +"\n##############################\n"

		# Display all of the interfaces
		#print json.dumps(i['interfaces'], sort_keys=True, indent=4) + "\n######\n"
		print json.dumps(i['interfaces']['eth0']['ip_address'], sort_keys=True, indent=4) + "\n######\n"
		AllSystems += i['name'] + '\t' \
				+ i['interfaces']['eth0']['ip_address'] + '\t' \
				+ '</br>'
		#+ i['mac_address'] + '  '\
		#+ ' </br>'
		#AllSystems += '</br>'

	print AllSystems
	#AllSystems = CobblerServer.get_systems()[0]
	return str(AllSystems)

# Enable Debug
debug(True)

run(reloader=True, port=8848, host='10.47.58.2')
