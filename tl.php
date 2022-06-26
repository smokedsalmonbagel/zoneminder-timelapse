<?php


/*
        @Author: Tyler Conlon
        @Date: 11-6-2019
        @Links: https://github.com/smokedsalmonbagel/zoneminder-timelapse
*/


//phpinfo();
error_reporting(E_ALL & ~E_NOTICE);
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
//error_reporting(E_ALL);
ini_set('max_execution_time', 300);

$tl_destination ='/external/zoneminder/tl';
$tl_log = '/var/log/timelapse';

if ( !canView( 'Stream' ) )
{
    $view = "error";
     return;
}


function resize_image($file, $w, $h, $crop=FALSE) {
    list($width, $height) = getimagesize($file);
    $r = $width / $height;
    if ($crop) {
        if ($width > $height) {
            $width = ceil($width-($width*abs($r-$w/$h)));
        } else {
            $height = ceil($height-($height*abs($r-$w/$h)));
        }
        $newwidth = $w;
        $newheight = $h;
    } else {
        if ($w/$h > $r) {
            $newwidth = $h*$r;
            $newheight = $h;
        } else {
            $newheight = $w/$r;
            $newwidth = $w;
        }
    }
    $src = imagecreatefromjpeg($file);
    $dst = imagecreatetruecolor($newwidth, $newheight);
    imagecopyresampled($dst, $src, 0, 0, 0, 0, $newwidth, $newheight, $width, $height);

    return $dst;
}

?>
<head>
 
<script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
<script src="skins/classic/js/VideoFrame.min.js"></script>


 <style>
 body{
	font-family: Verdana, Geneva, sans-serif;
}
 
 .column {
  float: left;
  width: 50%;
}

/* Clear floats after the columns */
.row:after {
  content: "";
  display: table;
  clear: both;
}
 </style>

<script type="text/javascript">


function updateslider(val)
{
	console.log(val);
}
var video;
$(document).ready(function() {
	
	
	var nextVideo = "../tl/c4/18_12_10_03_17.mpg";
	
	video = VideoFrame({
			id : 'videoPlayer',
			frameRate: 30,
			callback : function(response) {
			console.log('callback response: ' + response);
		}
		});
	
	
	
	
	$( ".playvid" ).click(function() {

	video.video.src = $(this).attr('data-attr');
		video.video.load();
		//videoPlayer.playbackRate = 10.0;
		video.video.play();
		console.log("test");

	});
		
	
 

		$("#videospeed").bind('onSlide', function(evt, val){
		  updateslider(val);
		  console.log(video.get() );
		});

	
		$( ".showcam" ).click(function() {
		
		if($( '#camdiv-'+$(this).attr('camid') ).attr( "data-show") == "true")
		{
			$( '#camdiv-'+$(this).attr('camid') ).hide( "fast" );
			$( '#camdiv-'+$(this).attr('camid') ).attr( "data-show","false" );
		}
		else
		{
	     $( '#camdiv-'+$(this).attr('camid') ).show( "fast" );
		 $( '#camdiv-'+$(this).attr('camid') ).attr( "data-show","true" );
		}
	});
	
});




window.addEventListener('keypress', function (evt) {
    if (video.video.paused) { //or you can force it to pause here
        if (evt.keyCode === 44) { //, key
            //one frame back
  
			
			video.seekBackward(1);
        } else if (evt.keyCode === 46) { // . key
            //one frame forward

			video.seekForward(1);
        }
		console.log(video.get() );
    }        
});


 </script>

</head>

<body>
  <div id="page">
    <div id="header">
      <h2>Timelapse</h2>
    </div>
    <div id="content">
	

	
	
	<?php 
	
	

$videos = json_decode(file_get_contents($tl_destination.'/index.json'),True);


	
	echo '<div style="width:100%">
		<video style="width:100%;" id="videoPlayer" src="" autobuffer controls>
		';



foreach($videos as $cam => $vids) 
{
	foreach($vids as $vid)
	{
		echo '<source src="?view=get_file&f='.$vid['path'].'" type="video/mp4" />';
	}
}

echo '
</video>
<div id="sliderAmount">1</div>
<input type="range" min="0" max="500" value="1" class="slider" id="videospeed"/>
</div>
';
foreach($videos as $cam => $vids)
{
	$img = '<img loading="lazy" alt="'.$vids[0]['path'].'" width="200" src="?view=get_file&f='.$vids[0]['preview'].'"/>';
	echo '<div style="" class="showcam" camid="'.$cam.'">'.$cam.' - Show / hide<br>'.$img.'</div><div style="display:none;" id="camdiv-'.$cam.'">';
	
	foreach($vids as $vid)
	{
		if ($vid['preview'])
		    $img = '<img loading="lazy" alt="'.$vid['path'].'" width="200" src="?view=get_file&f='.$vid['preview'].'"/>';
		else
			$img = '<img alt="?view=get_file&f='.$vid['path'].'" width="200" height="112" src="#"/>';
		
		$ds = date('D M jS, Y',strtotime(explode(' ',$vid['date'])[0]));
		echo '<div style="padding:1px;display:inline-block;position: relative; text-align: center;color: black;">
		
			<div style=""><a class="playvid" data-attr="?view=get_file&f='.$vid['path'].'" href="#">'.$img.'</a> </div>
			
			<div style="position: absolute;bottom: 16px;left: 5px;"><a href="?view=get_file&f='.$vid['path'].'">(DL)</a></div>
			<div style="position: absolute;bottom: 0px;left: 5px;background-color: rgba(255, 255, 255, 0.3);">'.$ds.'</div>
		</div>';
	}
	echo '</div>';
}
echo '<br><br>Log:<br>';
	
$lf = escapeshellarg($tl_log.'/tl.log'); 

	$daemonll = `tail -n 50 $lf`;
	$dloglines = explode("\n",$daemonll);
	foreach($dloglines as $ll)
	{
		echo '<div style="font-size:10px;">'.$ll.'</div>';
	}	

?>

</div>
</div>
</body>