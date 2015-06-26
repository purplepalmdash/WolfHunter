################################################################################
# This File is for listing all of the defined nodes, which could also viewed by
# `cobbler list`
################################################################################

# Use Cobbler API
import xmlrpclib
# Use bottle, for rendering HTML
from bottle import route, run, debug, template, view
# Beautify json output
import json

# Cobbler Server will be used during the lifetime of this file
CobblerServer = xmlrpclib.Server("http://127.0.0.1/cobbler_api")

# By visit http://Your_URL/system will get all of the installed system node name
# Todo: 2015_06_25: Use a template for beautifully displaying these items. 
@route('/system')
def list_system():
	# Use an list for recording all of the single_record(which is a tuple)
	AllSystems = []
	# Append each record of systems into the AllSystem list.
	for i in CobblerServer.get_systems():
		single_record = (i['name'] , i['interfaces']['eth0']['mac_address'] , i['interfaces']['eth0']['ip_address'] , i['gateway'] , i['hostname'] , i['profile'] , i['interfaces']['eth0']['dns_name'] , str(i['ctime']) , str(i['mtime']))
		AllSystems.append(single_record)

	# Check the result of the AllSystems
	for i in AllSystems:
		print i
	#AllSystems = CobblerServer.get_systems()[0]
	# output = template('./template/make_table', rows = AllSystems)
	# return output
	#return str(AllSystems)

@route('/hello')
@route('/hello/<name>')
@view('hello_template')
def hello(name='World'):
	return dict(name=name)

# Enable Debug
debug(True)

run(reloader=True, port=8848, host='0.0.0.0')
