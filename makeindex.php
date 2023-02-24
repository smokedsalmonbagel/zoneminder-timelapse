<?php


/*
        @Author: Tyler Conlon
        @Date: 11-6-2019
        @Links: https://github.com/smokedsalmonbagel/zoneminder-timelapse
*/


$tl_destination = '/external/zoneminder/tl'; #no trailing slash here
$previews_dir_name = 'previews';#no slashes 

function newest($a, $b) 
{ 
	return filemtime($b)-filemtime($a) ; 
} 


function scan_dir($dir) {


	$fl = array();
	$dir = glob($dir); // put all files in an array 
	uasort($dir, "newest"); // sort the array by calling newest() 

	foreach($dir as $file) 
	{ 
		$fl[] .= $file; 
	}
	return $fl;
}

$videos = array();

	$fl = scan_dir($tl_destination.'/*');
	
	$i=0;
	natsort($fl);
	foreach ($fl as $key=>$path)
	{
		$vids = scan_dir($path.'/*.mp4');
		natsort($vids);
		$vids = array_reverse($vids, true);
		//echo  '------------' . $path . '------------<br>';
		#print_r( $vids) . '<br><br>';
		foreach ($vids as $i => $vid)
		{
			// Get the video path:
			$vp = str_replace($tl_destination,'',$vid);
			/* Break down video path to something like:
			[0] =>
			[1] => external
			[2] => zoneminder
			[3] => tl
			[4] => c16
			[5] => 22_12_24_00_00.mp4
			*/
			$vn = explode('/',$vid);
			#print_r($vn);
			$video_name_index = array_key_last($vn); #index of video name in path array
			$vc = $vn[$video_name_index - 1]; //should be the 'video camera'
			#echo $vc;
			
			$ds = explode('_',str_replace('.mp4','',$vn[$video_name_index]));//date string
			$vd = '20' . $ds[0] . '-' . $ds[1] . '-' .$ds[2] . ' ' . $ds[3] . ':' .$ds[4] . ':00';//video date - fix before year 2100 :-)
			//echo $vd;
			$videos[$vc][$i]['preview'] = Null;
			$previews = scan_dir($path.'/'.$previews_dir_name.'/'.$ds[0].'_'.$ds[1].'_'.$ds[2].'/*.jpg');
			if (sizeof($previews) > 0)
			{
				$target_hr = 19;
				$difs = array();
				$n=0;
				foreach($previews as $p)
				{
					$hr = explode('_',$p)[5];
					$difs[$n] = abs($target_hr - $hr);
					$n +=1;
					#print_r($hr);
					
				}
				$ind = array_search(min($difs), $difs);
				$preview = str_replace($tl_destination,'',$previews[$ind]);

				$videos[$vc][$i]['preview'] = $preview ;
			}
			
			

			$videos[$vc][$i]['path'] = $vp;
			$videos[$vc][$i]['date'] = $vd;
			
			$i++;
		}
	}
	
file_put_contents($tl_destination.'/index.json',json_encode($videos));

?>
