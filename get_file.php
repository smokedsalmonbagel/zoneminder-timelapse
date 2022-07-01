<?php

/*
This file allows downloading of timelapse videos only if the user is authorized by zoneminder
put in  /usr/share/zoneminder/www/skins/classic/views
Note:you must enable and config the apache xsend module


*/

if ( !canView( 'Stream' ) )
{
    $view = "error";
     return;
}

$file = $_GET['f'];
$fp = '/external/zoneminder/tl/'.$_GET['f'];
if (file_exists($fp))
{ 
    // send the right headers
    header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');
    header('Cache-Control: post-check=0, pre-check=0', false);
    header('Pragma: no-cache');
    header('Content-type: ' . mime_content_type($fp));
    header('Content-Length: ' . filesize($fp));
	header('Content-Disposition: attachment; filename="'.str_replace('/','_',ltrim($file, '/')).'"');

    // Make sure you have X-Sendfile module installed on your server
    // To download this module, go to https://www.apachelounge.com/download/
    header('X-Sendfile: ' .$fp);
    exit;
}
else
{
    die('File loading failed.');
}


?>