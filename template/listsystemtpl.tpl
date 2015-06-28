%#template to generate a HTML table from a list of tuples (or list of lists, or tuple of tuples or ...)
<!DOCTYPE html>
<html>
<head>
<title>
List Of All Of The Nodes In System
</title>
<link rel="stylesheet" media="all" href="static/css/custom.css" type="text/css">
</head>
<h1>
All of the Systems are listed Here!!!
</h1>
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
<script src="static/js/jquery.min.js"></script>
<script src="static/js/jquery.stickytableheaders.js"></script>
<script>
	$("table").stickyTableHeaders();
</script>

</html>
