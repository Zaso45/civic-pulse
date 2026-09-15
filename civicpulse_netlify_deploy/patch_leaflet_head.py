import re
import os

html_path = r'C:\Users\home\.gemini\antigravity\scratch\civicpulse\static\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace Google Maps script with Leaflet
html = html.replace(
    '<!-- Google Maps API -->\n  <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&libraries=marker"></script>',
    '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />\n  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
)

# Replace google-map ID with leaflet-map
html = html.replace('id="google-map"', 'id="leaflet-map"')

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

