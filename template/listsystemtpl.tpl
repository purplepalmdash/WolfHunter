%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<!DOCTYPE html>
<html>
%# <script>
%# function timedRefresh(timeoutPeriod) {
%#     setTimeout("location.reload(true);",timeoutPeriod);
%# }
%# </script>
%# %# 30 seconds for wait
%# <body onload="JavaScript:timedRefresh(30000);"> 
<p>The defined system definition are as follows:</p>
<table border="1">
%for row in rows:
  <tr>
  %for col in row:
    <td>{{col}}</td>
  %end
  </tr>
%end
</table>
</body>

</html>
