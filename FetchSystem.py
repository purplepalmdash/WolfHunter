################################################################################
# This File is for listing all of the defined nodes, which could also viewed by
# `cobbler list`
################################################################################

# Use Cobbler API
import xmlrpclib
# Use bottle, for rendering HTML
from bottle import route, run, debug, template, view, request
# Beautify json output
import json

# Cobbler Server will be used during the lifetime of this file
CobblerServer = xmlrpclib.Server("http://127.0.0.1/cobbler_api")

# By visit http://Your_URL/system will get all of the installed system node name
@route('/listsystem')
def list_system():
	# Use an list for recording all of the single_record(which is a tuple)
	SystemTableName = ('Node Name', 'MAC Address', 'IP Address', 'Gateway', 'Hostname', 'Profile', 'DNS Name', 'Created Time', 'Modified Time')
	AllSystems = []

	# Append each record of systems into the AllSystem list.
	for i in CobblerServer.get_systems():
		single_record = (i['name'] , i['interfaces']['eth0']['mac_address'] , i['interfaces']['eth0']['ip_address'] , i['gateway'] , i['hostname'] , i['profile'] , i['interfaces']['eth0']['dns_name'] , str(i['ctime']) , str(i['mtime']))
		AllSystems.append(single_record)

	# Append SystemTableName at the first position of the AllSystems
	AllSystems.insert(0, SystemTableName)

	# !!!Debuging!!! Check the result of the AllSystems
	### for i in AllSystems:
	### 	for j in i:
	### 		print j
	### 	print i
	### 	print "##########################"

	# Use listsystemtpl for diplaying the system data to users.
	output = template('./template/listsystemtpl', rows = AllSystems)
	return output

# By visit http://Your_URL/newsystem will hint user for add a new system into the Cobbler.
# A form will be displayed to user, they input/choose items, and POST them to bottle, bottle will use the getted information 
# for setting up a new system, and insert it to the Cobbler. 
# Reference to tips/PythonAdd.txt, this file shows the whole step for adding a system.
@route('/newsystem', method='GET')
def new_system():
	if request.GET.get('save','').strip():
		# Get the Form Elements from the GET Method.
		# Idealy in the html we should use JavaScript for matching the conditions. 
		Added_NodeName = request.GET.get('NodeName','').strip()
		Added_MacAddress = request.GET.get('MacAddress','').strip()
		Added_IpAddress = request.GET.get('IpAddress','').strip()
		Added_Gateway = request.GET.get('Gateway','').strip()
		Added_Hostname = request.GET.get('Hostname','').strip()
		Added_Profile = request.GET.get('Profile','').strip()
		Added_DnsName = request.GET.get('DnsName','').strip()
		print Added_NodeName
		print Added_MacAddress
		print Added_IpAddress
		print Added_Gateway
		print Added_Hostname
		print Added_Profile
		print Added_DnsName
		insert_system_to_cobbler(Added_NodeName, Added_MacAddress, Added_IpAddress, Added_Gateway, Added_Hostname, Added_Profile, Added_DnsName)

		# Call Wrapped Cobbler function for really add the system into the Cobbler System.
		# TODO: We may encouter the node has been defined in the system, thus we have to hint for modifying or cancel.

		# Hint the User that we've received the request and submit them to the Cobbler System.
		# Idealy this will directly go the added systems. 
		return '<p>Well I Know! Your System will be submmited to the Cobbler System!</p>'
	else:
		# The Profiles should be retrived from the Cobbler System, and use template for rendering it.
		output = template('./template/newsystemtpl')
		return output

# Function for wrapping the Cobbler's API for inserting the definition into the Cobber System.
# Input: NodeName, MacAddress, IpAddress, Gateway, Hostname, Profile, DnsName
def insert_system_to_cobbler(NodeName, MacAddress, IpAddress, Gateway, Hostname, Profile, DnsName):
	print "Yes, you are about to insert your defined system into cobbler!"
	print NodeName
	print MacAddress
	print IpAddress
	print Gateway
	print Hostname
	print Profile
	print DnsName
	print "Yes, you left this function!"


# Testing  the templates
@route('/hello')
@route('/hello/<name>')
@view('hello_template')
def hello(name='World'):
	return dict(name=name)

# Enable Debug
debug(True)

run(reloader=True, port=8848, host='0.0.0.0')
