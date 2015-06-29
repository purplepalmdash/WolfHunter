%#template for serving the addsystem webpage
%#TODO: The checking should be done, for checking following issues:
%#1. NodeName has been taken
%#2. Formats are OK for sending in forms.
%#
%#
<!DOCTYPE html>
<html>
<head>
<title>
Add New Definition To System
</title>
<link rel="stylesheet" media="all" href="static/css/custom.css" type="text/css">
<link rel="stylesheet" href="static/css/pure/base-min.css">
<link rel="stylesheet" href="static/css/pure/forms.css">
<link rel="stylesheet" href="static/css/pure/buttons.css">

<script>
var namelist={{!namelist}}
var maclist={{!maclist}}
var iplist={{!iplist}}
function isInArray(array, search)
{
    return array.indexOf(search) >= 0;
}
function validateForm() {
    var x = document.forms["NodeInfoForm"]["NodeName"].value;
    if (x == null || x == "") {
        alert("NodeName must be filled out");
        return false;
    }
    if (isInArray(namelist, x)) {
        alert("NodeName has already been defined");
        return false;
    }
    var y = document.forms["NodeInfoForm"]["MacAddress"].value;
    if (y == null || y == "") {
        alert("MacAddress must be filled out");
        return false;
    }
    if (isInArray(maclist, y)) {
        alert("Mac Address has already been defined");
        return false;
    }
    var z = document.forms["NodeInfoForm"]["IpAddress"].value;
    if (z == null || z == "") {
        alert("IPAddress must be filled out");
        return false;
    }
    if (isInArray(iplist, z)) {
        alert("IP Address has already been defined");
        return false;
    }
}
</script>
</head>
<h1>
Add New Node To System
</h1>
<body>
<form class="pure-form pure-form-aligned" id="NodeInfoForm" name="NodeInfoForm" actions="/newsystem"  onsubmit="return validateForm()" method="GET">
Node name: <input type="text" name="NodeName"><br>
MAC Address: <input type="text" name="MacAddress"><br>
IP Address: <input type="text" name="IpAddress"><br>
Gateway: <input type="text" name="Gateway"><br>
Hostname: <input type="text" name="Hostname"><br>
Profile List: <select name="ProfileList">
%for profile in profiles:
<option value={{profile}}>{{profile}}</option>
%end
</select>
<br>
Dns Name: <input type="text" name="DnsName"><br>
<input type="submit" name="save" value="Add">
</fieldset>
</form>
</body>
</html>
