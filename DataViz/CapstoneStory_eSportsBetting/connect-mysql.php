<?php
DEFINE ('DB_USER','csgobetting');
DEFINE ('DB_PSWD','Password1');
DEFINE ('DB_HOST','csgobetting.database.windows.net');
DEFINE ('DB_NAME', 'csgobetting');

$dbcon = mysqli_connect(DB_HOST, DB_USER, DB_PSWD, DB_NAME)
?>