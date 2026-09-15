import re
import os

html_path = r'C:\Users\home\.gemini\antigravity\scratch\civicpulse\static\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Replace Leaflet variable with googleMap
html = html.replace('let leafletMap = null;', 'let googleMap = null;')

# Update Google Map JS Implementation
old_map_js = """    // ── Leaflet Map ──
    function initGoogleMap() {
      leafletMap = L.map('google-map').setView([18.6630, 77.8980], 14);
      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO', maxZoom: 19
      }).addTo(leafletMap);
    }

    function populateMapMarkers() {
      if (!googleMap) return;
      mapMarkers.forEach(m => leafletMap.removeLayer(m));
      mapMarkers = [];
      tickets.forEach(ticket => {
        const isCrit = ticket.severity === 'Critical';
        const color = isCrit ? '#D95338' : ticket.gated ? '#325D88' : '#C97A2B';
        const customIcon = L.divIcon({
          className: '',
          html: `<div class="custom-marker" style="background:${color};">${ticket.severityScore}</div>`,
          iconSize: [32, 32], iconAnchor: [16, 16]
        });
        const marker = L.marker(ticket.coords, { icon: customIcon }).addTo(leafletMap);
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
        google.maps.event.trigger(googleMap, "resize");
        leafletMap.setView([18.6630, 77.8980], 14);
      }
    }"""

new_map_js = """    // ── Google Maps ──
    let userLocationMarker = null;

    function initGoogleMap() {
      if (typeof google === 'undefined') {
        console.warn('Google Maps API not loaded.');
        return;
      }
      googleMap = new google.maps.Map(document.getElementById("google-map"), {
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
            } else {
               userLocationMarker.setPosition(pos);
            }
          },
          () => { console.warn("Geolocation tracking failed."); },
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
html = html.replace(old_map_js, new_map_js)

# Triage update status to handle assignee + priority
old_triage_func = """    async function deploySquad(id) {
      try {
        await fetch(`${API}/api/tickets/${id}/status`, {
          method: 'PATCH', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'Squad En Route' })
        });
      } catch(e) { const t = tickets.find(i => i.id === id); if (t) t.status = 'Squad En Route'; }
      await loadTickets();
      triggerToast(`Deployment confirmed: Squad en route to ${id}!`);
    }"""
new_triage_func = """    async function deploySquad(id) {
      try {
        await fetch(`${API}/api/tickets/${id}/status`, {
          method: 'PATCH', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'Squad En Route', assignee: 'Municipal Quick Response' })
        });
      } catch(e) { const t = tickets.find(i => i.id === id); if (t) { t.status = 'Squad En Route'; t.assignee = 'Municipal Quick Response'; } }
      await loadTickets();
      triggerToast(`Deployment confirmed: Squad en route to ${id}!`);
    }
    
    async function resolveTicket(id) {
      try {
        await fetch(`${API}/api/tickets/${id}/status`, {
          method: 'PATCH', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'Resolved' })
        });
      } catch(e) { const t = tickets.find(i => i.id === id); if (t) t.status = 'Resolved'; }
      await loadTickets();
      triggerToast(`Issue ${id} has been resolved!`);
    }"""
html = html.replace(old_triage_func, new_triage_func)


# Add Login UI & Script Handling to HTML body
login_modal = """
  <!-- Auth Modal -->
  <div id="auth-modal" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-beige-900/40 backdrop-blur-sm hidden opacity-0 transition-opacity duration-200">
    <div class="bg-beige-50 rounded-3xl max-w-sm w-full p-6 sm:p-8 editorial-border shadow-elevated relative">
      <button onclick="document.getElementById('auth-modal').classList.add('hidden')" class="absolute top-6 right-6 w-8 h-8 rounded-full bg-beige-200 text-beige-700 hover:bg-beige-300 flex items-center justify-center transition">
        <i data-lucide="x" class="w-4 h-4"></i>
      </button>
      <h3 class="text-2xl font-serif font-bold text-beige-900 mb-6">Sign In</h3>
      
      <form onsubmit="handleLogin(event)" class="space-y-4">
        <div>
          <label class="block text-xs font-mono font-bold text-beige-600 uppercase mb-1">Email</label>
          <input type="email" id="login-email" class="w-full bg-white border border-beige-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-terracotta-500" value="admin@municipal.gov" required />
        </div>
        <div>
          <label class="block text-xs font-mono font-bold text-beige-600 uppercase mb-1">Password</label>
          <input type="password" id="login-password" class="w-full bg-white border border-beige-300 rounded-xl px-4 py-3 text-sm focus:outline-none focus:border-terracotta-500" value="admin123" required />
        </div>
        <button type="submit" class="w-full py-3.5 mt-2 rounded-xl bg-beige-900 hover:bg-beige-800 text-beige-50 font-bold text-xs uppercase tracking-wider transition">Sign In</button>
      </form>
      <div class="mt-4 text-[10px] text-beige-500 text-center font-mono space-y-1">
        <p>Test Municipal: admin@municipal.gov / admin123</p>
        <p>Test RWA: admin@greenvalley.com / admin123</p>
      </div>
    </div>
  </div>
"""
html = html.replace("<!-- MODAL: REPORT CREATION", login_modal + "\n  <!-- MODAL: REPORT CREATION")

# Add auth state variables
html = html.replace("let uploadedFile = null;", "let uploadedFile = null;\n    let currentUser = null;")

# Add Auth JS
auth_js = """
    // ── Auth ──
    async function checkAuth() {
        try {
            const res = await fetch(`${API}/api/auth/me`);
            if (res.ok) {
                currentUser = await res.json();
                updateAuthUI();
            }
        } catch (e) { console.warn("Not logged in"); }
    }

    async function handleLogin(e) {
        e.preventDefault();
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        try {
            const res = await fetch(`${API}/api/auth/login`, {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });
            if (res.ok) {
                currentUser = await res.json();
                document.getElementById('auth-modal').classList.add('hidden');
                updateAuthUI();
                triggerToast(`Logged in as ${currentUser.name}`);
                if (currentUser.role === 'municipal' || currentUser.role === 'rwa') {
                    switchView('authority');
                }
            } else {
                triggerToast('Invalid credentials');
            }
        } catch (e) { console.error('Login failed'); }
    }

    function updateAuthUI() {
        if (!currentUser) return;
        const authBtn = document.querySelector('aside .underline');
        if (authBtn) {
            authBtn.innerText = `Logged in: ${currentUser.name}`;
            authBtn.onclick = null;
        }
        if (currentUser.role === 'citizen') {
            document.getElementById('user-karma-badge').innerText = currentUser.karma + ' PTS';
        }
    }
"""
html = html.replace("// ── Init ──", auth_js + "\n    // ── Init ──")
html = html.replace("lucide.createIcons();", "lucide.createIcons();\n      await checkAuth();")
html = html.replace("switchView('authority')", "document.getElementById('auth-modal').classList.remove('hidden')")
html = html.replace("onclick=\"document.getElementById('auth-modal').classList.remove('hidden')\"", "onclick=\"switchView('authority')\"")

# Add Live location tracking directly in form for submission
submit_gps = """      // Auto-attach location if available via browser GPS
      if (navigator.geolocation) {
         navigator.geolocation.getCurrentPosition(
             (pos) => {
                 formData.append('lat', pos.coords.latitude);
                 formData.append('lng', pos.coords.longitude);
             },
             () => { console.warn("No GPS"); }
         );
      }"""
html = html.replace("if (uploadedFile) {", submit_gps + "\n\n      if (uploadedFile) {")

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

