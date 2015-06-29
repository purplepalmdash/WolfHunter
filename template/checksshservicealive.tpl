%#template which contains all of the playbook list, choose whichever for deployment
<!DOCTYPE html>
<html>
 <script>
  function timedRefresh(timeoutPeriod) {
      setTimeout("location.reload(true);",timeoutPeriod);
  }
  </script>
  %# 10 seconds for wait
  <body onload="JavaScript:timedRefresh(10000);"> 
<p>Your SSH Port (22) is reachable, But cannot get sshd service, Auto-Check in 10 Seconds!</p>
</body>

</html>

