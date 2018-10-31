  // BASECOORDS = [-13.9626, 33.7741];
  //
  // function makeMap() {
  //     var TILE_URL = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  //     var MB_ATTR = 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors';
  //     mymap = L.map('map').setView(BASECOORDS, 8);
  //     L.tileLayer(TILE_URL, {attribution: MB_ATTR}).addTo(mymap);
  // }
  //
  // var layer = L.layerGroup();
  //
  // function renderData(districtid) {
  //     $.getJSON("/district/" + districtid, function(obj) {
  //         var markers = obj.data.map(function(arr) {
  //             return L.marker([arr[0], arr[1]]);
  //         });
  //         mymap.removeLayer(layer);
  //         layer = L.layerGroup(markers);
  //         mymap.addLayer(layer);
  //     });
  // }
  //
  //
  // $(function() {
  //     makeMap();
  //     renderData('0');
  //     $('#distsel').change(function() {
  //         var val = $('#distsel option:selected').val();
  //         renderData(val);
  //     });
  // })



// center of the map
var center = [58., 16];

// Create the map
var map = L.map('map',{zoomControl: false}).setView(center, 6);

// Set up the OSM layer
L.tileLayer(
  'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: 'Data © <a href="http://osm.org/copyright">OpenStreetMap</a>',
    maxZoom: 18
  }).addTo(map);

var drawnItems = L.featureGroup().addTo(map);
var segmentItems = L.featureGroup().addTo(map);
var lastfeature;


// add a marker in the given location
//L.marker(center).addTo(map);

map.addControl(new L.Control.Draw({
  position: 'topright',
  edit: {
      featureGroup: drawnItems,
      poly : {
          allowIntersection : false
      }
  },
  draw: {
      polygon : {
          allowIntersection: false,
          showArea:true
      },
      polyline: false,
      circle: false,
      circlemarker: false,
      marker: false,
  }
}));
//
// // Initialise the FeatureGroup to store editable layers
// var editableLayers = new L.FeatureGroup();
// map.addLayer(editableLayers);
//
// var drawPluginOptions = {
//   position: 'topright',
//   draw: {
//     polygon: {
//       allowIntersection: false, // Restricts shapes to simple polygons
//       drawError: {
//         color: '#e1e100', // Color the shape will turn when intersects
//         message: '<strong>Oh snap!<strong> you can\'t draw that!' // Message that will show when intersect
//       },
//       shapeOptions: {
//         color: '#97009c'
//       }
//     },
//     // disable toolbar item by setting it to false
//     polyline: false,
//     circle: false, // Turns off this drawing tool
//     rectangle: true,
//     marker: false,
//     },
//   edit: {
//     featureGroup: editableLayers, //REQUIRED!!
//     remove: true
//   }
// };
//
// // Initialise the draw control and pass it the FeatureGroup of editable layers
// var drawControl = new L.Control.Draw(drawPluginOptions);
// map.addControl(drawControl);
//
// var editableLayers = new L.FeatureGroup();
// map.addLayer(editableLayers);

var cars = [
	{ "make":"Porsche", "model":"911S" },
	{ "make":"Mercedes-Benz", "model":"220SE" },
	{ "make":"Jaguar","model": "Mark VII" }
];

function doWork(event) {
	// ajax the JSON to the server
	//$.post("getFile", cars, function(){
  $.get("getFile/42", function(){

	});
	// stop link reloading the page
}

var defaultStyle = {
            color: "#2262CC",
            weight: 2,
            opacity: 0.6,
            fillOpacity: 0.1,
            fillColor: "#2262CC"
        };

var highlightStyle = {
    color: '#2262CC',
    weight: 3,
    opacity: 0.6,
    fillOpacity: 0.65,
    fillColor: '#2262CC'
};

map.on(L.Draw.Event.CREATED, function(e) {
  var type = e.layerType,
    layer = e.layer;

  //layer.bindPopup('A popup!');
  //layer.on('click', function(e) { console.log(e.layer) });
  layer.on('click', doWork);
  lastfeature = layer;
  drawnItems.addLayer(layer);
});


function draw_pass(data) {
  L.geoJSON(data, {
    onEachFeature: function (feature, layer) {
      var style = feature.properties.pass_direction;
      layer.setStyle(defaultStyle);
      layer.on("mouseout", function (e) {
        // Start by reverting the style back
        layer.setStyle(defaultStyle);
      });
      layer.on("mouseover", function (e) {
        // Start by reverting the style back
        layer.setStyle(highlightStyle);
      });
      switch (feature.properties.pass_direction) {
        case 'ASCENDING': style = "transform: scaleY(-1);"; break;
        case 'DESCENDING': style = "transform: scaleX(-1);-webkit-transform: scale(-1, 1);"; break;
        default: style = feature.properties.pass_direction;
      }
      layer.bindPopup('<p>ID: '+feature.properties.id+'</p><img class="quicklook" src="' + feature.properties.quicklook +'" style="'+style+'"/><p>here a nice quicklook and a <a href="'+feature.properties.id+'">download button</a></p>');
    }//,
    //style: {color: "#ff2222"}
  }).addTo(segmentItems);
}

function searchfun() {
            // $.getJSON('/search',
            //     JSON.stringify({'data': lastfeature.toGeoJSON()}),
            //     function(data) {
            //       L.geoJSON(data, {
            //         onEachFeature: function (feature, layer) {
            //           layer.bindPopup('<h1>'+feature.properties.id+'</h1><p>here a nice quicklook</p>');
            //         }
            //         // style: function(feature) {
            //         //   switch (feature.properties.party) {
            //         //     case 'Republican': return {color: "#ff0000"};
            //         //     case 'Democrat':   return {color: "#0000ff"};
            //         //   }
            //         // }
            //       }).addTo(map);
            // });
            var json_data = drawnItems.toGeoJSON()
            json_data['sourceID'] = document.forms['searchform']['sourceID'].value
            json_data['start_time'] = $("#datetimepicker7").datetimepicker('viewDate');
            json_data['end_time'] = $("#datetimepicker8").datetimepicker('viewDate');
            $.ajax({
              dataType: "json",
              url: '/search',
              type: 'POST',
              contentType : 'application/json',
              //data: JSON.stringify({'poly': lastfeature.toGeoJSON()}),
              data: JSON.stringify(json_data),
              //data: JSON.stringify({'bla': 'bli'}),
              success: draw_pass});
            segmentItems.clearLayers();
            event.preventDefault();
            return false;
          }


$('#searchform').submit(searchfun);
