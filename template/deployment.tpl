%#template which contains all of the playbook list, choose whichever for deployment
<!DOCTYPE html>
<html>
%# <script>
%#  function timedRefresh(timeoutPeriod) {
%#      setTimeout("location.reload(true);",timeoutPeriod);
%#  }
%#  </script>
%#  %# 5 seconds for wait
%#  <body onload="JavaScript:timedRefresh(5000);"> 
<p>Select following playbook for deployment</p>
<form actions="/deployment" method="GET">
* CloudStack<br>
* NTP<br>
<input type="submit" name="save" value="Deploy">
</form>
</body>

</html>

