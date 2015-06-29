%#template which contains all of the playbook list, choose whichever for deployment
<!DOCTYPE html>
<html>
<head>
<title>
Node Info List
</title>
<link rel="stylesheet" media="all" href="../static/css/custom.css" type="text/css">
%#<link rel="stylesheet" href="static/css/pure/base-min.css">
%#<link rel="stylesheet" href="static/css/pure/forms.css">
%#<link rel="stylesheet" href="static/css/pure/buttons.css">
</head>
<h1>
Node Info
</h1>
<p>Select following playbook for deployment</p>
<form class="pure-form pure-form-aligned" actions="/deployment" method="GET">
%for playbook in playbookfullname:
<input type="radio" name="playbook" value={{playbook}}>{{playbook}}<br>
%end
<input type="submit" name="Deploy" value="Deploy">
</form>

</html>
