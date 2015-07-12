################################################################################
# V1: This File is for listing all of the defined nodes, which could also viewed by
# `cobbler list`
# V2: I added more operations, like add a new definition of the node, and present
# these functionalities to end-user, and designed its logic for jumping. 
# V3: Import Ansible, to let ansible do playbook deployment on the base of the 
# Cobbler deployed base-system.  
# V4: Integration with Ansible Playbooks, but the playbooks needs to be customizated. 
################################################################################

################################################################################
# Todo:
# 1. Username/Password. Not everyone are allowed to using this service.
# 2. Playbook Customization.  https://github.com/edx/configuration/wiki/Ansible-variable-conventions-and-overriding-defaults, 
# ansible-playbook ... -e "test_var=foo", but for python wrapped, how to ? 
# 3. Remove the added Nodes. 
# 4. Edit the added Nodes. 
# 5. Insert id_rsa.pub into the system. (Done in Cobbler)
# 6. Modify the Cloudstack playbook, for customize the database password. 
################################################################################

# Use Cobbler API
import xmlrpclib
# Use bottle, for rendering HTML
from bottle import route, run, debug, template, view, request, redirect, static_file
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
# Ansible related
from ansible.playbook import PlayBook
from ansible.inventory import Inventory
from ansible import callbacks
from ansible import utils
# Use jijia2 and templates for rendering the temp-files,tmpfiles will be used for playing playbooks. 
import jinja2
from tempfile import NamedTemporaryFile
import os
import re


### Definitions for Cobbler
# Cobbler Server instance and token will be used during the lifetime of this file
CobblerServer = xmlrpclib.Server("http://127.0.0.1/cobbler_api")
token = CobblerServer.login("cobbler", "engine")

# Global variable for indicating a playbook is deployed or not
global FinishDeploying
FinishDeploying=0
global DeployStarted
DeployStarted=0

####  extra vars , I don't know how to put these extra vars into ansible books? 
#vars1={"CSManagement":{"ManagementIP":"10.47.58.154"}}
#print vars1["CSManagement"]["ManagementIP"]
# extra_vars = {"vars":{"CSManagement":{"ManagementIP":"10.47.58.154"}}}
#extra_vars = {'CSManagement.ManagementIP': "10.47.58.154"}

###  Definitions for Ansible
# Boilerplace callbacks for stdout/stderr and log output
#utils.VERBOSITY = 0
utils.VERBOSITY = 3
playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
stats = callbacks.AggregateStats()
runner_cb = callbacks.PlaybookRunnerCallbacks(stats, verbose=utils.VERBOSITY)

# Dynamic Inventory
# We fake a inventory file and let Ansible load if it's a real file.
# Just don't tell Ansible that, so we don't hurt its feelings.
# Added CSManagement.ManagementIP for overriding the configuration which available in playbook definition. 
inventory = """
[customer]
{{ public_ip_address }}

[customer:vars]
domain={{ domain_name }}
customer_id={{ customer_id }}
customer_name={{ customer_name }}
customer_email={{ customer_email }}
CSManagement.ManagementIP={{ customer_CSMangementIP }}
"""

### Actual codes goes from here
# Well, you want to use customized css or js here
@route('/static/:path#.+#', name='static')
def static(path):
	return static_file(path, root='static')

# By visit http://Your_URL/system will get all of the installed system node name
@route('/listsystem')
def list_system():
	# Use an list for recording all of the single_record(which is a tuple)
	SystemTableName = ('Node Name', 'MAC Address', 'IP Address', 'Gateway', 'Hostname', 'Profile', 'DNS Name', 'Created Time', 'Modified Time')
	AllSystems = []

	# Append each record of systems into the AllSystem list.
	for i in CobblerServer.get_systems():
		try:
			single_record = (i['name'] , i['interfaces']['eth0']['mac_address'] , i['interfaces']['eth0']['ip_address'] , i['gateway'] , i['hostname'] , i['profile'] , i['interfaces']['eth0']['dns_name'] , str(i['ctime']) , str(i['mtime']))
			AllSystems.append(single_record)
		except Exception, e:
			print e

	# Append SystemTableName at the first position of the AllSystems
	AllSystems.insert(0, SystemTableName)

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
		Added_Profile = request.GET.get('ProfileList','').strip()
		Added_DnsName = request.GET.get('DnsName','').strip()
		# Really insert into the cobbler backend
		insert_system_to_cobbler(Added_NodeName, Added_MacAddress, Added_IpAddress, Added_Gateway, Added_Hostname, Added_Profile, Added_DnsName)

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
		# profiles holds all of the distros which could be fetched via `cobbler profile list`, notice the differences between distros
		profiles = []
		namelist = []
		maclist = []
		iplist = []
		for i in CobblerServer.get_profiles():
			profiles += [i['name']]
		for i in CobblerServer.get_systems():
			namelist += [i['name']]
			maclist += [i['interfaces']['eth0']['mac_address']]
			iplist += [i['interfaces']['eth0']['ip_address']]
		# Check the name/ip_address exists or not in this page, using javascript?
		output = template('./template/newsystemtpl', profiles=profiles, namelist=namelist, maclist=maclist, iplist=iplist)
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
	# Don't forget to sync
	CobblerServer.sync(token)

# Pages for serving a single node
@route('/Node/<NodeName:path>', method='GET')
def node_item(NodeName):
	# 1.1 Use NodeName for retriving the IP Address
	# use xmlrpcapi for getting the ip address
	for i in CobblerServer.get_systems():
		if i['name'] == NodeName:
			NodeIP = i['interfaces']['eth0']['ip_address']
	print NodeIP

	# 1.2 Just use ssh to detect whether remote machine is ready for be fucked or not. 
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		# 1.2.1 you are trying and hoping you will OK
		s.connect((NodeIP, 22))
		# 2.1 Start flirting(try to ssh remote machine using paramiko)!
		try:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(NodeIP, username="root", password="engine")
			#  Everything is OK, Go to 3, start deploying!
		except Exception, e:
			# 2.2 flirting failed, check your own reason. 
			print e
			output = template('./template/checksshservicealive')
			return output
	except socket.error as e:
		# 1.2.2 you could reach the 22 port, go back and checking.
		print "No, the port is unreachable, keep calm and checking connections"
		# These maybe the deployment is going, so refresh it using javascript.
		output = template('./template/checksshportalive')
		return output
		#return "<p>Your 22 Port seems down, check it!"+ "<br>Reason:<br>"+ str(e)
	s.close()
	# 3. Now you can really go to the Deployment webpage and fucking now!
	redirect('/Deploy/'+ NodeName)

# Pages for serving a single node
@route('/Deploy/<NodeName:path>', method='GET')
def deployOn_IP(NodeName):
	global DeployStarted, FinishDeploying
	# Retrive GET Var from Bottle API
	if request.GET.get('playbook','').strip():
		playbook = request.GET.get('playbook', '').strip()
	if request.GET.get('Deploy','').strip():
		if FinishDeploying == 1:
			DeployStarted = 0
			# Here we could redirect to a new webpage which indicates the statistics for this deployment. 
			return "Check your log for fail or not"
		else:
			# Here the Ansible module will be called, and hint user that we are deploying, wait for succeed or fail. 
			# a subprocess or thread will be spawned for deploying using Ansible
			if DeployStarted == 0:
				# Thread could only be started once. 
				if request.GET.get('playbook', '').strip():
					playbook = request.GET.get('playbook', '').strip()
					t = clientThread(NodeName, playbook)
					t.start()
					DeployStarted = 1
			# Default will return this auto-refreshable webpage
			output = template('./template/underdeployment')
			return output
	# Default all of the playbooks will be deplayed.
	else:
		# Here we provide the playbook list and let user for selecting.   
		FinishDeploying = 0
		# Here we should list all of the playbooks, render the template, and send it to the user
		# Search all of the yml and appended them into the array. 
		playbookname = []
		playbookfullname = []
		for path, subdirs, files in os.walk('./playbooks'):
			for filename in files:
				f = os.path.join(path, filename)
				#  # Get the short name for displaying
				#  if re.search('.yml$', filename):
				#  	playbookname += [filename]
				# Full name including directory structure will also be filled
				if re.search('.yml$', f):
					playbookfullname += [f]

		output = template('./template/deployment', playbookfullname = playbookfullname)
		return output

#  a client thread for changing some global status
class clientThread(threading.Thread):
        def __init__(self, NodeName, playbook):
		self.domain_name = NodeName
		self.playbook = playbook
		# Get the Node's corresponding IP Address and use it for deployment
		for i in CobblerServer.get_systems():
			if i['name'] == NodeName:
				self.public_ip_address = i['interfaces']['eth0']['ip_address']
		threading.Thread.__init__(self)

        def run(self):
                self.handle_task()

	# In handle_task we will call Ansible instead of debugging 
        def handle_task(self):
		# Run a Ansible playbook here.
		inventory_template = jinja2.Template(inventory)
		print self.domain_name
		print self.public_ip_address
		rendered_inventory = inventory_template.render({
			'public_ip_address': self.public_ip_address, 
			'domain_name': self.domain_name, 
			'customer_id' : 'bobdylan', 
			'customer_name' : 'BobDylan', 
			'customer_email' : 'bobdylan@heavensdoor.com',
			'customer_CSMangementIP': self.public_ip_address
			# and the rest of our variables
		})
		
		# Create a temporary file and write the template string to it
		hosts = NamedTemporaryFile(delete=False)
		hosts.write(rendered_inventory)
		hosts.close()
		
		# First we will test install/uninstall the ntp server on its server.
		extra_vars_managementIP = {"vars":{"CSManagement":{"ManagementIP":self.public_ip_address}}}
		pb = PlayBook(
			playbook = self.playbook, 
			host_list = hosts.name,     # Our hosts, the rendered inventory file
			remote_user = 'root',
			callbacks = playbook_cb,
			runner_callbacks = runner_cb,
			stats=stats,
			extra_vars = extra_vars_managementIP,
			private_key_file = '/root/.ssh/id_rsa'
		)
		results = pb.run()
		
		# Ensure on_stats callback is called
		# for callback modules
		playbook_cb.on_stats(pb.stats)
		
		os.remove(hosts.name)
		print "***************************************************************"
		print "See this means you have finished the Playbook running in Thread"
		print "***************************************************************"
		global FinishDeploying
		FinishDeploying = 1

# Enable Debug
debug(True)

run(reloader=True, port=8848, host='0.0.0.0')
#run(reloader=True, port=8848, host='192.168.1.99')
