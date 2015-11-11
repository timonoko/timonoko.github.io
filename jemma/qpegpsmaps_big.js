//<![CDATA[

var map;

function load() {
    if (GBrowserIsCompatible()) {
	map = new GMap2(document.getElementById("map"));
	map.addControl(new GSmallMapControl());
//	map.addControl(new GScaleControl());
//	map.addControl(new GOverviewMapControl());
	var scale = 10;
	var centre = new GLatLng(60.20, 25.0);
    
	map.setCenter(centre, scale);


	function calcScale() {
	    var bounds = map.getBounds();
	    var neb = bounds.getNorthEast();
	    var swb = bounds.getSouthWest();
	    
	    var se = new GLatLng( swb.lat(), neb.lng() );

	    var dy = se.distanceFrom(swb);

	    // 2817 factor is the FRITZ factor - gpsdrive m/pixel scale factor
	    return (dy*2817.947378/800.0).toFixed(2);
	}

	function outputMercator() {
	    var bounds = map.getBounds();
	    var zoom = map.getZoom();
	    var output = document.getElementById("bounds");

	    var ne = bounds.getNorthEast();
	    var sw = bounds.getSouthWest();

	    var dist = calcScale();

	    var newtext = "<p>MERCATOR <i>name</i> "+ dist +" 1000 730 ";
	    newtext += sw.lng() + " " + ne.lat() + " 0 0 " + ne.lng() + " ";
	    newtext += sw.lat() + " 1000 730 </p>";

	    output.innerHTML = '';
	    output.innerHTML = newtext;
	}

	GEvent.addListener(map, 'moveend', function() {
	    outputMercator();
	});

	outputMercator();
    }
    else {
	alert("Sorry, the Google Maps API is not compatible with this browser");
    }
}    
//]]>
