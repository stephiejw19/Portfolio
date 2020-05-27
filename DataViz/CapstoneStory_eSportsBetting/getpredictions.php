<!doctype html>
<html>

<head>
<style>    
<style>
table {
    width: 100%;
    border-collapse: collapse;
}

table, td, th {
    border: 1px solid black;
    padding: 5px;
    color: white;
}
</style>
</head>
<body>

<?php
$q = intval($_GET['q']);

$con = mysqli_connect('csgobetting.database.windows.net','csgobetting','Password1','csgobetting');

if (!$con) {
    die('Could not connect: ' . mysqli_error($con));
}

mysqli_select_db($con, "dbo.predictions").
$sql= "SELECT tournament, StartTime, HomeTeamName, bet_on WHERE HomeTeamName = '".q"'";

result = mysqli_query($con,$sql);

echo "<table>";
echo "<tr><th>Tournament</th><th>Start Time></th><th>Team 1</th></tr>";

while($row = mysqli_fetch_array($result)) {
    echo "<tr>";
    echo "<td>" . $row['Tournament'] . "</td>";
    echo "<td>" . $row['StartTime'] . "</td>";
    echo "<td>" . $row['HomeTeamName'] . "</td>";
    echo "<td>" . $row['bet_on'] . "</td>";
    echo "</tr>";
}
echo "</table>";
mysqli_close($con);

?>

</body>
</html>