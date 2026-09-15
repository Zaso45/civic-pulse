import re

html_path = r'C:\Users\home\.gemini\antigravity\scratch\civicpulse\static\index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace variables
html = html.replace('let googleMap = null;', 'let leafletMap = null;\n    let userLiveMarker = null;\n    let userLiveCoords = null;')
html = html.replace('if (!googleMap) {', 'if (!leafletMap) {')
html = html.replace('initGoogleMap();', 'initLeafletMap();')

# Replace the switchView mapping
html = re.sub(
    r'google\.maps\.event\.trigger\(googleMap, "resize"\);',
    r'leafletMap.invalidateSize();',
    html
)

# Use regex to replace the entire map functions block
pattern = r'// ── Google Maps ──.*?function recenterMap\(\) \{.*?\}\n'
new_map = """// ── Leaflet Map ──
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
    }
"""

html = re.sub(pattern, new_map, html, flags=re.DOTALL)

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

