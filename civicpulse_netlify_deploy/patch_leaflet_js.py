import re
import os

html_path = r'C:\Users\home\.gemini\antigravity\scratch\civicpulse\static\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace variables
html = html.replace('let googleMap = null;', 'let leafletMap = null;\n    let userLiveMarker = null;\n    let userLiveCoords = null;')
html = html.replace('if (!googleMap) {', 'if (!leafletMap) {')
html = html.replace('initGoogleMap();', 'initLeafletMap();')

# Replace switchView google map resize
old_resize = """          } else {
            google.maps.event.trigger(googleMap, "resize");
            populateMapMarkers();
          }"""
new_resize = """          } else {
            leafletMap.invalidateSize();
            populateMapMarkers();
          }"""
html = html.replace(old_resize, new_resize)

# Replace the Map Functions Block
old_map_functions = """    // ── Google Maps ──
    let userLocationMarker = null;

    function initGoogleMap() {
      if (typeof google === 'undefined') {
        console.warn('Google Maps API not loaded.');
        return;
      }
      googleMap = new google.maps.Map(document.getElementById("leaflet-map"), {
        center: { lat: 18.6630, lng: 77.8980 },
        zoom: 14,
        styles: [
          { elementType: "geometry", stylers: [{ color: "#f5f5f5" }] },
          { elementType: "labels.icon", stylers: [{ visibility: "off" }] },
          { elementType: "labels.text.fill", stylers: [{ color: "#616161" }] },
          { elementType: "labels.text.stroke", stylers: [{ color: "#f5f5f5" }] },
          { featureType: "administrative.land_parcel", elementType: "labels.text.fill", stylers: [{ color: "#bdbdbd" }] },
          { featureType: "poi", elementType: "geometry", stylers: [{ color: "#eeeeee" }] },
          { featureType: "poi", elementType: "labels.text.fill", stylers: [{ color: "#757575" }] },
          { featureType: "poi.park", elementType: "geometry", stylers: [{ color: "#e5e5e5" }] },
          { featureType: "poi.park", elementType: "labels.text.fill", stylers: [{ color: "#9e9e9e" }] },
          { featureType: "road", elementType: "geometry", stylers: [{ color: "#ffffff" }] },
          { featureType: "road.arterial", elementType: "labels.text.fill", stylers: [{ color: "#757575" }] },
          { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#dadada" }] },
          { featureType: "road.highway", elementType: "labels.text.fill", stylers: [{ color: "#616161" }] },
          { featureType: "road.local", elementType: "labels.text.fill", stylers: [{ color: "#9e9e9e" }] },
          { featureType: "transit.line", elementType: "geometry", stylers: [{ color: "#e5e5e5" }] },
          { featureType: "transit.station", elementType: "geometry", stylers: [{ color: "#eeeeee" }] },
          { featureType: "water", elementType: "geometry", stylers: [{ color: "#c9c9c9" }] },
          { featureType: "water", elementType: "labels.text.fill", stylers: [{ color: "#9e9e9e" }] }
        ]
      });

      // Track Live User Location
      if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
          (position) => {
            const pos = {
              lat: position.coords.latitude,
              lng: position.coords.longitude,
            };
            if (!userLocationMarker) {
               userLocationMarker = new google.maps.Marker({
                 position: pos,
                 map: googleMap,
                 icon: {
                   path: google.maps.SymbolPath.CIRCLE,
                   scale: 8,
                   fillColor: '#4285F4',
                   fillOpacity: 1,
                   strokeColor: 'white',
                   strokeWeight: 2,
                 },
                 title: 'Your Location'
               });
               // Center map immediately when we get the first live location lock
               googleMap.setCenter(pos);
               googleMap.setZoom(15);
            } else {
               userLocationMarker.setPosition(pos);
            }
          },
          (err) => { console.warn("Geolocation tracking failed: ", err.message); },
          { enableHighAccuracy: true }
        );
      }
    }

    function populateMapMarkers() {
      if (!googleMap) return;
      mapMarkers.forEach(m => m.setMap(null));
      mapMarkers = [];
      const infoWindow = new google.maps.InfoWindow();

      tickets.forEach(ticket => {
        const isCrit = ticket.severity === 'Critical';
        const color = isCrit ? '#D95338' : ticket.gated ? '#325D88' : '#C97A2B';
        
        // Ensure coords are correctly formatted for Google Maps
        const position = { 
            lat: Array.isArray(ticket.coords) ? ticket.coords[0] : ticket.lat, 
            lng: Array.isArray(ticket.coords) ? ticket.coords[1] : ticket.lng 
        };

        const marker = new google.maps.Marker({
          position: position,
          map: googleMap,
          icon: {
            path: google.maps.SymbolPath.CIRCLE,
            fillColor: color,
            fillOpacity: 1,
            strokeWeight: 2,
            strokeColor: '#FFFFFF',
            scale: 10
          },
          title: ticket.title
        });

        marker.addListener('click', () => {
          infoWindow.setContent(`
            <div style="font-family:'Plus Jakarta Sans',sans-serif; min-width:180px; padding:2px;">
              <div style="font-size:10px; font-weight:800; color:#9E8B76; text-transform:uppercase;">${ticket.id} &bull; ${ticket.severity}</div>
              <div style="font-size:13px; font-weight:700; color:#231B15; margin:3px 0;">${ticket.title}</div>
              <div style="font-size:11px; color:#756350;">${ticket.location}</div>
              <div style="margin-top:6px; font-size:11px; font-weight:bold; color:#D95338;">Status: ${ticket.status}</div>
            </div>
          `);
          infoWindow.open(googleMap, marker);
        });
        mapMarkers.push(marker);
      });
    }

    function recenterMap() {
      if (googleMap) {
        google.maps.event.trigger(googleMap, "resize");
        if (userLocationMarker) {
            googleMap.setCenter(userLocationMarker.getPosition());
        } else {
            googleMap.setCenter({ lat: 18.6630, lng: 77.8980 });
        }
        googleMap.setZoom(14);
      }
    }"""

new_map_functions = """    // ── Leaflet Map ──
    function initLeafletMap() {
      leafletMap = L.map('leaflet-map').setView([18.6630, 77.8980], 14);
      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO', maxZoom: 19
      }).addTo(leafletMap);

      // Track Live User Location
      if (navigator.geolocation) {
        navigator.geolocation.watchPosition(
          (position) => {
            const pos = [position.coords.latitude, position.coords.longitude];
            userLiveCoords = pos;

            if (!userLiveMarker) {
               userLiveMarker = L.circleMarker(pos, {
                 radius: 8,
                 fillColor: '#4285F4',
                 fillOpacity: 1,
                 color: 'white',
                 weight: 2
               }).addTo(leafletMap);
               userLiveMarker.bindTooltip("Your Location");
               
               // Center map immediately when we get the first live location lock
               leafletMap.setView(pos, 15);
            } else {
               userLiveMarker.setLatLng(pos);
            }
          },
          (err) => { console.warn("Geolocation tracking failed: ", err.message); },
          { enableHighAccuracy: true }
        );
      }
    }

    function populateMapMarkers() {
      if (!leafletMap) return;
      mapMarkers.forEach(m => leafletMap.removeLayer(m));
      mapMarkers = [];
      tickets.forEach(ticket => {
        const isCrit = ticket.severity === 'Critical';
        const color = isCrit ? '#D95338' : ticket.gated ? '#325D88' : '#C97A2B';
        const position = Array.isArray(ticket.coords) ? ticket.coords : [ticket.lat, ticket.lng];
        
        const customIcon = L.divIcon({
          className: '',
          html: `<div class="custom-marker" style="background:${color};">${ticket.severityScore}</div>`,
          iconSize: [32, 32], iconAnchor: [16, 16]
        });
        const marker = L.marker(position, { icon: customIcon }).addTo(leafletMap);
        marker.bindPopup(`
          <div style="font-family:'Plus Jakarta Sans',sans-serif; min-width:180px; padding:2px;">
            <div style="font-size:10px; font-weight:800; color:#9E8B76; text-transform:uppercase;">${ticket.id} &bull; ${ticket.severity}</div>
            <div style="font-size:13px; font-weight:700; color:#231B15; margin:3px 0;">${ticket.title}</div>
            <div style="font-size:11px; color:#756350;">${ticket.location}</div>
            <div style="margin-top:6px; font-size:11px; font-weight:bold; color:#D95338;">Status: ${ticket.status}</div>
          </div>`);
        mapMarkers.push(marker);
      });
    }

    function recenterMap() {
      if (leafletMap) {
        leafletMap.invalidateSize();
        if (userLiveCoords) {
            leafletMap.setView(userLiveCoords, 15);
        } else {
            leafletMap.setView([18.6630, 77.8980], 14);
        }
      }
    }"""
html = html.replace(old_map_functions, new_map_functions)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

