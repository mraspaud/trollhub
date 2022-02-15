
// center of the map
var scripts = document.getElementsByTagName('script');
var currentScript = scripts[scripts.length-1];

var center = [currentScript.getAttribute("center-lat"), currentScript.getAttribute("center-lon")];

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

map.on(L.Draw.Event.CREATED, function(e) {
  var type = e.layerType,
    layer = e.layer;

  layer.on('click', doWork);
  lastfeature = layer;
  drawnItems.addLayer(layer);
});




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
        case 'ascending': style = "transform: scaleY(-1);"; break;
        case 'descending': style = "transform: scaleX(-1);-webkit-transform: scale(-1, 1);"; break;
        default: style = feature.properties.pass_direction;
      }
      //layer.bindPopup('<p>ID: '+feature.properties.id+'</p><img class="quicklook" src="' + feature.properties.quicklook +'" style="'+style+'"/><p>here a nice quicklook and a <a href="'+feature.properties.id+'">download button</a></p>');
      if('quicklook' in feature.properties) {
        layer.bindPopup('<p class="thick">ID: ' + feature.properties.id + '</p><img class="quicklook" src="' + feature.properties.quicklook + '" style="' + style + '"/>');
      } else {
        layer.bindPopup('<p class="thick">ID: ' + feature.properties.id + '</p>');
      }
    }//,
    //style: {color: "#ff2222"}
  }).addTo(segmentItems);
}

function searchfun() {

            var json_data = drawnItems.toGeoJSON();
            json_data['sourceID'] = $('#sourceID').val();
            console.log(json_data['sourceID']);
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
            document.getElementById("searchbtn").classList.remove('btn-primary');
            document.getElementById("searchbtn").classList.add('btn-success');
            return false;
          }

function setCookie(cname, cvalue, exdays) {
  var d = new Date();
  d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
  var expires = "expires="+d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  var name = cname + "=";
  var ca = document.cookie.split(';');
  for(var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

function saveareas() {
            var json_data = drawnItems.toGeoJSON()
            setCookie("search_areas", JSON.stringify(json_data), 36500)

            return false;
          }


$('#searchform').submit(searchfun);
//$('#saveform').submit(saveareas);

function loadareas() {
  var content = getCookie("search_areas");
  if (content.length != 0) {
    var gjson = JSON.parse(content);
    L.geoJSON(gjson).addTo(drawnItems);
  }
}

document.onload = loadareas();

var lastTarget = null;

window.addEventListener("dragenter", function(e)
{
    lastTarget = e.target; // cache the last target here
    // unhide our dropzone overlay
    document.querySelector(".dropzone").style.visibility = "";
    document.querySelector(".dropzone").style.opacity = 1;
});

window.addEventListener("dragleave", function(e)
{
    // this is the magic part. when leaving the window,
    // e.target happens to be exactly what we want: what we cached
    // at the start, the dropzone we dragged into.
    // so..if dragleave target matches our cache, we hide the dropzone.
    // `e.target === document` is a workaround for Firefox 57
    if(e.target === lastTarget || e.target === document)
    {
        document.querySelector(".dropzone").style.visibility = "hidden";
        document.querySelector(".dropzone").style.opacity = 0;
    }
});

var dropZone = document.getElementById('dropzone');

function startUpload(files) {
    for (var i=files.length - 1; i >= 0; i--) {

      var reader = new FileReader();
      reader.onload = function(e) {
        var contents = e.target.result;
        var gjson = JSON.parse(contents);
        L.geoJSON(gjson).addTo(drawnItems);
      };
      console.log('... file[' + i + '].name = ' + files[i].name);
      reader.readAsText(files[i]);

    }
    //reader.readAsText(files[0]);
    // console.log(files)
}

window.addEventListener("drop", function(e) {
        e.preventDefault();
        startUpload(e.dataTransfer.files)
        console.log('dropped');
        if(e.target === lastTarget || e.target === document)
        {
            document.querySelector(".dropzone").style.visibility = "hidden";
            document.querySelector(".dropzone").style.opacity = 0;
        }
      });

window.addEventListener("dragover", function(e) {
        e.preventDefault();
        console.log('dragover');
      });

function download(filename, text) {
  var element = document.createElement('a');
  element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
  element.setAttribute('download', filename);

  element.style.display = 'none';
  document.body.appendChild(element);

  element.click();

  document.body.removeChild(element);
}

function exportfun() {
            download("trollhub_areas.geojson", getCookie("search_areas"));
            return false;
          }

var el = document.getElementById('exportlnk');
el.onclick = exportfun;

var el = document.getElementById('savelnk');
el.onclick = saveareas;


