################################################################################
# This File is for listing all of the defined nodes, which could also viewed by
# `cobbler list`
################################################################################

# Use Cobbler API
import xmlrpclib
# Use cobbler BootAPI, Notice this method is not suggested from version 2.0
import cobbler.api as capi
# Use bottle, for rendering HTML
from bottle import route, run, debug, template, view, request, redirect
# Beautify json output
import json
# Use socket for detect the remote machine status(ssh port 22)
import socket
# Use paramiko for detect ssh connection
import paramiko
import time
# Use MultiThread for spawning tasks
import sys
import errno
import threading


# Cobbler Server instance and token will be used during the lifetime of this file
CobblerServer = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
token = CobblerServer.login("cobbler", "engine")
#handle = capi.BootAPI()

# Global variable for indicating a playbook is deployed or not
global FinishDeploying
FinishDeploying=0
global DeployStarted
DeployStarted=0

# By visit http://Your_URL/system will get all of the installed system node name
@route('/listsystem')
def list_system():
	print "#################Your visited listsystem############"
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
		# Really insert into the cobbler backend
		#insert_system_to_cobbler(Added_NodeName, Added_MacAddress, Added_IpAddress, Added_Gateway, Added_Hostname, Added_Profile, Added_DnsName)

		# Call Wrapped Cobbler function for really add the system into the Cobbler System.
		# TODO: We may encouter the node has been defined in the system, thus we have to hint for modifying or cancel.

		# Hint the User that we've received the request and submit them to the Cobbler System.
		# Idealy this will directly go the added systems. TODO: Jump to the wait page http://YourServer/NodeName.
		# Jump to the node spcified webpage, this page's behavior is listed as following: 
		# When not initialized, in wait Webpage(a. not sshable. b. sshable but key error. 3. sshable with key OK.) 
		# When initialized , to ansible playbooks and begin to deploy.
		redirect('/Node/'+Added_NodeName)
	else:
		# The Profiles should be retrived from the Cobbler System, and use template for rendering it.
		output = template('./template/newsystemtpl')
		return output

# Function for wrapping the Cobbler's API for inserting the definition into the Cobber System.
# Input: NodeName, MacAddress, IpAddress, Gateway, Hostname, Profile, DnsName
# Refers to the API from doc
def insert_system_to_cobbler(NodeName, MacAddress, IpAddress, Gateway, Hostname, Profile, DnsName):
	system_id = CobblerServer.new_system(token)
	CobblerServer.modify_system(system_id, "name", NodeName, token)
	CobblerServer.modify_system(system_id, 'modify_interface', {"macaddress-eth0": MacAddress, "ipaddress-eth0": IpAddress, "dnsname-eth0": DnsName,}, token)
	CobblerServer.modify_system(system_id, "profile", Profile, token)
	CobblerServer.modify_system(system_id, "gateway", Gateway, token)
	CobblerServer.modify_system(system_id, "hostname", Hostname, token)
	# After modify, sync them to the system
	CobblerServer.save_system(system_id, token)

# Pages for serving a single node
@route('/Node/<NodeName:path>', method='GET')
def node_item(NodeName):
	# 1.1 Use NodeName for retriving the IP Address
	# use a handle for get the ip address of the specified NodeName
	handle = capi.BootAPI()
	# Possible Risk(if there are other ip address? or the name is not eth0, like enp0sxx?)
	for x in handle.find_system(hostname=NodeName, return_list=True):
		NodeIP = x.interfaces['eth0']['ip_address']
	# 1.2 Just use ssh to detect whether remote machine is ready for be fucked or not. 
	print NodeIP
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		# 1.2.1 you are trying and hoping you will OK
		s.connect((NodeIP, 22))
		# 2.1 Start flirting(try to ssh remote machine using paramiko)!
		try:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(NodeIP, username="root", password="engine")
			# Everything is OK, Go to 3, start fucking!
			#return "<p>Saw this page means you can fuck freely!!!</p>"
		except Exception, e:
			# 2.2 flirting failed, check your own reason. 
			print e
			return "<p>Your 22 Port is OK, but there may be something you have to set with ssh"+ "<br>Reason:<br>"+ str(e)
	except socket.error as e:
		# 1.2.2 you could reach the 22 port, go back and checking.
		print "No, the port is unreachable, keep calm and checking connections"
		return "<p>Your 22 Port seems down, check it!"+ "<br>Reason:<br>"+ str(e)
	s.close()
	# 3. Now you can really go to the Deployment webpage and fucking now!
	redirect('/Deploy/'+ NodeName)

# Pages for serving a single node
@route('/Deploy/<NodeName:path>', method='GET')
def deployOn_IP(NodeName):
	global DeployStarted
	if request.GET.get('save','').strip():
		if FinishDeploying == 1:
			DeployStarted = 0
			print "Seems your playbook deployment finished"
			# Here we could redirect to a new webpage which indicates the statistics for this deployment. 
			return "Check your log for fail or not"
		else:
			# Here the Ansible module will be called, and hint user that we are deploying, wait for succeed or fail. 
			# a subprocess or thread will be spawned for deploying using Ansible
			print "under deployment, please wait!"
			if DeployStarted == 0:
				t = clientThread(1)
				t.start()
				DeployStarted = 1
			output = template('./template/underdeployment')
			# Before teturn output, create a thread for Ansible's deployment
			# t = clientThread(1)
			# t.start()
			return output
	# Default all of the playbooks will be deplayed.
	else:
		# Here we provide the playbook list and let user for selecting.   
		#FinishDeploying = 0
		output = template('./template/deployment')
		return output

#  a client thread for changing some global status
class clientThread(threading.Thread):
        def __init__(self, threadid):
                threading.Thread.__init__(self)

        def run(self):
                self.handle_task()

        def handle_task(self):
                while True:
                        print "Print from thread!"
                        time.sleep(1)


# Testing  the templates
@route('/hello')
@route('/hello/<name>')
@view('hello_template')
def hello(name='World'):
	return dict(name=name)

# Enable Debug
debug(True)

run(reloader=True, port=8848, host='0.0.0.0')

