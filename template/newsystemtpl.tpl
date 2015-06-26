%#template for serving the addsystem webpage
<p>See this means that you want to add a new system to Cobbler</p>
<p>!!!Fill the following form for define this system!!!</p>
<form actions="/newsystem" method="GET">
Node name: <input type="text" name="NodeName"><br>
MAC Address: <input type="text" name="MacAddress"><br>
IP Address: <input type="text" name="IpAddress"><br>
Gateway: <input type="text" name="Gateway"><br>
Hostname: <input type="text" name="Hostname"><br>
Profile: <input type="text" name="Profile"><br>
Dns Name: <input type="text" name="DnsName"><br>
<input type="submit" name="save" value="Add">
</form>
