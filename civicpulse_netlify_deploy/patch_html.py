import re
import os

html_path = r'C:\Users\home\.gemini\antigravity\scratch\civicpulse\static\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace Leaflet with Google Maps
html = re.sub(
    r'<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />\n\s*<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>',
    r'<!-- Google Maps API -->\n  <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_GOOGLE_MAPS_API_KEY&libraries=marker"></script>',
    html
)

html = html.replace('id="leaflet-map"', 'id="google-map"')
html = html.replace('initLeafletMap()', 'initGoogleMap()')
html = html.replace('leafletMap.invalidateSize()', 'google.maps.event.trigger(googleMap, "resize")')
html = html.replace('!leafletMap', '!googleMap')

# Mobile Camera Support
html = html.replace(
    '<input type="file" id="form-image" accept="image/jpeg,image/png,image/webp" class="hidden" onchange="handleImageUpload(event)" />',
    '<input type="file" id="form-image" accept="image/jpeg,image/png,image/webp" capture="environment" class="hidden" onchange="handleImageUpload(event)" />'
)

# Enhanced Triage HTML
old_triage_th = """              <th class="pb-3">Designated Entity</th>
              <th class="pb-3">Workflow State</th>
              <th class="pb-3 text-right">Action</th>"""
new_triage_th = """              <th class="pb-3">Assignee</th>
              <th class="pb-3">Priority</th>
              <th class="pb-3">Workflow State</th>
              <th class="pb-3 text-right">Actions</th>"""
html = html.replace(old_triage_th, new_triage_th)

# Bottom Mobile Nav Bar
nav_bar = """
  <!-- Mobile Bottom Nav -->
  <nav class="lg:hidden fixed bottom-0 w-full bg-beige-50/95 backdrop-blur-md border-t border-beige-200 z-40 pb-safe">
    <div class="flex justify-around items-center h-16">
      <button onclick="switchView('feed')" class="flex flex-col items-center justify-center w-full h-full text-terracotta-500">
        <i data-lucide="layers" class="w-5 h-5"></i>
        <span class="text-[9px] font-bold mt-1">Feed</span>
      </button>
      <button onclick="switchView('map')" class="flex flex-col items-center justify-center w-full h-full text-beige-500 hover:text-beige-900">
        <i data-lucide="map-pin" class="w-5 h-5"></i>
        <span class="text-[9px] font-bold mt-1">Radar</span>
      </button>
      <div class="relative w-full h-full flex justify-center">
        <button onclick="openModal()" class="absolute -top-5 w-14 h-14 bg-terracotta-500 rounded-full text-white shadow-card flex items-center justify-center active:scale-95 transition-transform">
          <i data-lucide="camera" class="w-6 h-6"></i>
        </button>
      </div>
      <button onclick="switchView('gated')" class="flex flex-col items-center justify-center w-full h-full text-beige-500 hover:text-beige-900">
        <i data-lucide="shield-alert" class="w-5 h-5"></i>
        <span class="text-[9px] font-bold mt-1">Gated</span>
      </button>
      <button onclick="switchView('authority')" class="flex flex-col items-center justify-center w-full h-full text-beige-500 hover:text-beige-900">
        <i data-lucide="shield-check" class="w-5 h-5"></i>
        <span class="text-[9px] font-bold mt-1">Dispatch</span>
      </button>
    </div>
  </nav>
"""
html = html.replace("</body>", nav_bar + "\n</body>")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

