
    const API = '';
    let tickets = [];
    let userKarma = 920;
    let leafletMap = null;
    let userLiveMarker = null;
    let userLiveCoords = null;
    let mapMarkers = [];
    let uploadedFile = null;
    let currentUser = null;
    const PLACEHOLDER_SEEDS = [
      {
        id: "CP-701",
        scope: "city",
        type: "pothole",
        category: "Roads & Potholes",
        title: "Submerged Crater Pothole near Bodhan-Nizamabad Road",
        location: "Bodhan Main Corridor, Landmark: Old Bus Stand",
        description: "Heavy rains filled this 15cm deep cavity. Multiple bikes witnessed skidding during twilight hours.",
        severity: "Critical",
        severityScore: 94,
        status: "Crew Dispatched",
        upvotes: 48,
        createdAt: "22m ago",
        gated: false,
        coords: [18.6650, 77.8970],
        img: "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=700&q=80"
      },
      {
        id: "CP-702",
        scope: "gated",
        type: "gated",
        category: "Gated Society",
        society: "Green Valley Palms",
        unit: "Wing C, Basement -1",
        title: "Commercial Van Parked Across 2 Resident Bays",
        location: "Green Valley Palms, Slot B-104",
        description: "Third time this unregistered delivery van blocked elderly resident's slot. Security barrier let it enter without visitor OTP.",
        severity: "Medium",
        severityScore: 68,
        status: "Notice Issued",
        upvotes: 19,
        createdAt: "45m ago",
        gated: true,
        coords: [18.6720, 77.9020],
        img: "https://images.unsplash.com/photo-1506521781263-d8422e82f27a?auto=format&fit=crop&w=700&q=80"
      },
      {
        id: "CP-703",
        scope: "city",
        type: "water",
        category: "Water Supply & Drainage",
        title: "Pressurized Drinking Line Rupture Flooding Market",
        location: "Gandhi Chowk, Bodhan Ward 4",
        description: "Clean pipeline burst leaking thousands of litres per hour. Silt entering adjacent residences.",
        severity: "Critical",
        severityScore: 91,
        status: "Valve Closed",
        upvotes: 62,
        createdAt: "1h ago",
        gated: false,
        coords: [18.6610, 77.8890],
        img: "https://images.unsplash.com/photo-1584467735871-8e85353a8413?auto=format&fit=crop&w=700&q=80"
      },
      {
        id: "CP-704",
        scope: "gated",
        type: "gated",
        category: "Gated Society",
        society: "Silver Arch Enclave",
        unit: "Tower 2 Passenger Lift",
        title: "Passenger Lift Stuck with Shutter Vibrations",
        location: "Tower 2, Floor 7",
        description: "Emergency telephone in elevator has no dial tone. RWA maintenance AMC has delayed inspection by 2 weeks.",
        severity: "High",
        severityScore: 84,
        status: "AMC Contacted",
        upvotes: 35,
        createdAt: "2h ago",
        gated: true,
        coords: [18.6580, 77.9060],
        img: "https://images.unsplash.com/photo-1549488344-1f9b8d2bd1f3?auto=format&fit=crop&w=700&q=80"
      },
      {
        id: "CP-705",
        scope: "city",
        type: "electric",
        category: "Power & Lighting",
        title: "Exposed Transformer Terminal Wire on Pedestrian Walkway",
        location: "Railway Station Approach Road",
        description: "Live wires dangling within reach of cattle and pedestrians. Rain making contact zone dangerous.",
        severity: "Critical",
        severityScore: 96,
        status: "Under Triage",
        upvotes: 54,
        createdAt: "3h ago",
        gated: false,
        coords: [18.6695, 77.8915],
        img: "https://images.unsplash.com/photo-1509228468518-180dd4864904?auto=format&fit=crop&w=700&q=80"
      },
      {
        id: "CP-706",
        scope: "gated",
        type: "gated",
        category: "Gated Society",
        society: "Prestige Falcon Park",
        unit: "Clubhouse Terrace",
        title: "DJ Sound Rig Active at 1:15 AM (Decibels: 88dB)",
        location: "Clubhouse Open Deck",
        description: "Private birthday gathering playing heavy bass subwoofer far beyond society 10 PM quiet hour rules.",
        severity: "Low",
        severityScore: 48,
        status: "Guard Dispatched",
        upvotes: 23,
        createdAt: "4h ago",
        gated: true,
        coords: [18.6640, 77.9100],
        img: "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=700&q=80"
      }
    ];

    // ── Helpers ──
    function timeAgo(iso) {
      if (!iso) return 'Unknown';
      const diff = Date.now() - new Date(iso).getTime();
      const mins = Math.floor(diff / 60000);
      if (mins < 1) return 'Just now';
      if (mins < 60) return mins + 'm ago';
      const hrs = Math.floor(mins / 60);
      if (hrs < 24) return hrs + 'h ago';
      return Math.floor(hrs / 24) + 'd ago';
    }

    // ── Data Fetching ──
    async function loadTickets(type = 'all', sort = 'severity') {
      try {
        const params = new URLSearchParams({ sort });
        if (type !== 'all') params.set('type', type);
        const res = await fetch(`${API}/api/tickets?${params}`);
        tickets = await res.json();
        tickets.forEach(t => { t.createdAt = timeAgo(t.createdAt); });
      } catch(e) {
        console.error('API unavailable, using seeds', e);
        tickets = [...PLACEHOLDER_SEEDS];
      }
      renderTicketsGrid(tickets);
      renderGatedFeed();
      renderTriageTable();
      if (leafletMap) populateMapMarkers();
    }

    async function loadStats() {
      try {
        const res = await fetch(`${API}/api/stats`);
        const s = await res.json();
        userKarma = s.karma;
        document.getElementById('user-karma-badge').innerText = userKarma + ' PTS';
        document.getElementById('stats-resolved').innerText = s.defectsRepaired;
        document.getElementById('stats-active').innerText = s.criticalDispatches;
      } catch(e) { console.error('Stats API unavailable', e); }
    }

    
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
                    document.getElementById('auth-modal').classList.remove('hidden');
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

    // ── Init ──
    document.addEventListener("DOMContentLoaded", async () => {
      lucide.createIcons();
      await checkAuth();
      await loadTickets();
      await loadStats();
    });

    // ── View Routing ──
    function switchView(viewName) {
      document.querySelectorAll('.view-panel').forEach(p => p.classList.add('hidden'));
      document.querySelectorAll('.nav-tab').forEach(t => {
        t.classList.remove('bg-white', 'text-beige-900', 'shadow-soft');
        t.classList.add('text-beige-600');
      });
      const tv = document.getElementById(`view-${viewName}`);
      if (tv) tv.classList.remove('hidden');
      const tn = document.getElementById(`nav-${viewName}`);
      if (tn) { tn.classList.add('bg-white', 'text-beige-900', 'shadow-soft'); tn.classList.remove('text-beige-600'); }

      // Lazy-init map on first open, then refresh tiles + markers every visit
      if (viewName === 'map') {
        setTimeout(() => {
          if (!leafletMap) {
            initLeafletMap();
            populateMapMarkers();
          } else {
            leafletMap.invalidateSize();
            populateMapMarkers();
          }
        }, 100);
      }

      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    // ── Render Grid Cards ──
    function renderTicketsGrid(data) {
      const container = document.getElementById('tickets-grid');
      container.innerHTML = data.map(ticket => {
        const isCritical = ticket.severity === 'Critical';
        const isHigh = ticket.severity === 'High';
        const sevBg = isCritical ? 'bg-terracotta-500 text-white' : isHigh ? 'bg-amberwood text-white' : 'bg-beige-300 text-beige-800';
        return `
          <div class="bg-white rounded-3xl overflow-hidden editorial-border shadow-soft hover:shadow-card transition-all duration-300 flex flex-col justify-between group">
            <div>
              <div class="relative h-48 w-full bg-beige-200 overflow-hidden">
                <img src="${ticket.img}" alt="${ticket.title}" class="w-full h-full object-cover group-hover:scale-105 transition duration-500" />
                <div class="absolute inset-0 bg-gradient-to-t from-beige-900/60 via-transparent to-transparent"></div>
                <div class="absolute top-3 left-3 px-2.5 py-1 rounded-full text-[10px] font-mono font-bold tracking-wider ${sevBg} shadow-sm">
                  ${ticket.severity.toUpperCase()} (${ticket.severityScore}%)
                </div>
                <div class="absolute top-3 right-3 px-2 py-0.5 rounded-md text-[10px] font-mono font-bold ${ticket.gated ? 'bg-cobalt text-white' : 'bg-beige-50 text-beige-900'}">
                  ${ticket.gated ? 'GATED RWA' : 'MUNICIPAL WARD'}
                </div>
                <div class="absolute bottom-2 left-3 right-3 text-[11px] text-white/90 flex items-center justify-between font-mono">
                  <span>${ticket.createdAt}</span>
                  <span class="font-bold">${ticket.id}</span>
                </div>
              </div>
              <div class="p-5 space-y-2.5">
                <div class="text-[10px] font-mono font-bold text-amberwood uppercase tracking-wider">
                  ${ticket.gated ? `${ticket.society} &bull; ${ticket.unit}` : ticket.category}
                </div>
                <h3 class="font-bold text-base text-beige-900 group-hover:text-terracotta-500 transition line-clamp-2">${ticket.title}</h3>
                <p class="text-xs text-beige-600 line-clamp-2 leading-relaxed">${ticket.description}</p>
                <div class="flex items-center gap-1.5 text-xs text-beige-500 pt-1">
                  <i data-lucide="map-pin" class="w-3.5 h-3.5 text-beige-400"></i>
                  <span class="truncate">${ticket.location}</span>
                </div>
              </div>
            </div>
            <div class="p-4 bg-beige-50 border-t border-beige-200 flex items-center justify-between">
              <div class="flex items-center gap-2">
                <span class="w-2 h-2 rounded-full ${isCritical ? 'bg-terracotta-500 animate-ping' : 'bg-forest-600'}"></span>
                <span class="text-[11px] font-mono font-bold text-beige-700">${ticket.status}</span>
              </div>
              <button onclick="upvoteTicket('${ticket.id}')" class="px-3 py-1.5 rounded-xl bg-white hover:bg-beige-200 text-beige-800 text-xs font-bold font-mono editorial-border transition flex items-center gap-1.5 shadow-sm">
                <i data-lucide="arrow-big-up" class="w-4 h-4 text-terracotta-500"></i>
                <span id="v-${ticket.id}">${ticket.upvotes}</span>
              </button>
            </div>
          </div>`;
      }).join('');
      lucide.createIcons();
    }

    // ── Filter & Sort ──
    function filterTickets(filterType) {
      document.querySelectorAll('.feed-btn').forEach(btn => {
        btn.classList.remove('bg-beige-900', 'text-beige-50');
        btn.classList.add('bg-beige-100', 'text-beige-700');
      });
      event.target.classList.add('bg-beige-900', 'text-beige-50');
      event.target.classList.remove('bg-beige-100', 'text-beige-700');
      loadTickets(filterType, document.getElementById('sort-select').value);
    }

    function sortTickets(criteria) {
      loadTickets('all', criteria);
    }

    // ── Upvote (API) ──
    async function upvoteTicket(id) {
      try {
        const res = await fetch(`${API}/api/tickets/${id}/upvote`, { method: 'POST' });
        const data = await res.json();
        document.getElementById(`v-${id}`).innerText = data.upvotes;
        userKarma = data.karma;
        document.getElementById('user-karma-badge').innerText = userKarma + ' PTS';
      } catch(e) {
        const ticket = tickets.find(t => t.id === id);
        if (ticket) { ticket.upvotes += 1; document.getElementById(`v-${id}`).innerText = ticket.upvotes; }
      }
      triggerToast(`+10 Citizen Karma! Thank you for validating ticket ${id}.`);
    }

    // ── Gated Feed ──
    function renderGatedFeed() {
      const list = document.getElementById('gated-feed-list');
      const gatedOnly = tickets.filter(t => t.gated);
      list.innerHTML = gatedOnly.map(g => `
        <div class="pt-3 pb-3 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="flex items-start gap-3">
            <div class="w-10 h-10 rounded-xl bg-cobalt/10 text-cobalt flex items-center justify-center font-bold text-xs flex-shrink-0">
              <i data-lucide="shield" class="w-5 h-5"></i>
            </div>
            <div>
              <div class="flex items-center gap-2">
                <span class="text-xs font-mono font-bold text-beige-900">${g.society}</span>
                <span class="text-[11px] text-beige-500 font-semibold">&bull; ${g.unit}</span>
              </div>
              <h4 class="text-sm font-bold text-beige-900 mt-0.5">${g.title}</h4>
              <p class="text-xs text-beige-600 mt-0.5">${g.description}</p>
            </div>
          </div>
          <div class="flex items-center gap-3 flex-shrink-0">
            <span class="px-2.5 py-1 rounded-md text-[10px] font-mono font-bold bg-beige-100 text-beige-800">${g.status}</span>
            <button onclick="rwaAction('${g.id}')" class="px-3 py-1.5 rounded-xl bg-beige-900 hover:bg-beige-800 text-beige-50 text-xs font-bold transition">
              Escalate to RWA
            </button>
          </div>
        </div>
      `).join('');
      lucide.createIcons();
    }

    async function rwaAction(id) {
      try {
        await fetch(`${API}/api/tickets/${id}/status`, {
          method: 'PATCH', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'RWA Escalated' })
        });
      } catch(e) { const t = tickets.find(i => i.id === id); if (t) t.status = 'RWA Escalated'; }
      await loadTickets();
      triggerToast(`Ticket ${id} flagged to Management Committee.`);
    }

    // ── Triage Table ──
    function renderTriageTable() {
      const tbody = document.getElementById('triage-table-body');
      tbody.innerHTML = tickets.map(t => {
        const isCritical = t.severity === 'Critical';
        return `
          <tr class="hover:bg-beige-50/80 transition border-b border-beige-100">
            <td class="py-3 font-mono font-bold text-beige-900">${t.id}</td>
            <td class="py-3">
              <span class="font-bold text-beige-900 block truncate max-w-xs">${t.title}</span>
              <span class="text-[10px] font-mono text-beige-400 uppercase">${t.category}</span>
            </td>
            <td class="py-3 text-beige-600 max-w-xs truncate" title="${t.location}">${t.location}</td>
            <td class="py-3">
              <span class="font-mono font-bold text-xs ${isCritical ? 'text-terracotta-500' : 'text-amberwood'}">
                ${t.severityScore}% (${t.severity})
              </span>
            </td>
            <td class="py-3 font-semibold text-beige-800">${t.assignee || 'Unassigned'}</td>
            <td class="py-3 font-bold text-beige-600">${t.priority || 'Normal'}</td>
            <td class="py-3">
              <span class="px-2 py-0.5 rounded text-[10px] font-mono font-bold ${t.status==='Resolved'?'bg-forest-600 text-white':'bg-beige-200 text-beige-800'}">${t.status}</span>
            </td>
            <td class="py-3 text-right space-x-1">
              ${t.status === 'Resolved' ? '' : `
              <button onclick="deploySquad('${t.id}')" class="px-3 py-1.5 rounded-lg bg-beige-900 hover:bg-beige-800 text-beige-50 text-[11px] font-bold font-mono transition shadow-sm">
                Deploy
              </button>
              <button onclick="resolveTicket('${t.id}')" class="px-3 py-1.5 rounded-lg bg-forest-600 hover:bg-forest-700 text-white text-[11px] font-bold font-mono transition shadow-sm">
                Resolve
              </button>
              `}
            </td>
          </tr>`;
      }).join('');
    }

    async function deploySquad(id) {
      try {
        await fetch(`${API}/api/tickets/${id}/status`, {
          method: 'PATCH', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'Squad En Route', assignee: 'Municipal Response' })
        });
      } catch(e) { }
      await loadTickets();
      triggerToast(`Deployment confirmed: Squad en route to ${id}!`);
    }

    async function resolveTicket(id) {
      try {
        await fetch(`${API}/api/tickets/${id}/status`, {
          method: 'PATCH', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'Resolved' })
        });
      } catch(e) { }
      await loadTickets();
      triggerToast(`Issue ${id} has been resolved.`);
    }

    // ── Leaflet Map ──
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


    // ── Modal ──
    function openModal(defaultScope, defaultGatedCategory) {
      const modal = document.getElementById('report-modal');
      modal.classList.remove('hidden');
      setTimeout(() => modal.classList.remove('opacity-0'), 10);
      if (defaultScope === 'gated') {
        setFormScope('gated');
        if (defaultGatedCategory) document.getElementById('form-gated-category').value = defaultGatedCategory;
      } else { setFormScope('city'); }
    }

    function closeModal() {
      const modal = document.getElementById('report-modal');
      modal.classList.add('opacity-0');
      setTimeout(() => modal.classList.add('hidden'), 200);
      document.getElementById('ai-result').classList.add('hidden');
      document.getElementById('ai-placeholder').classList.remove('hidden');
      document.getElementById('ai-preview-img').src = '';
      document.getElementById('form-image').value = '';
      uploadedFile = null;
    }

    function setFormScope(scope) {
      document.getElementById('form-scope').value = scope;
      const cityBtn = document.getElementById('scope-btn-city');
      const gatedBtn = document.getElementById('scope-btn-gated');
      const gatedFields = document.getElementById('gated-fields-container');
      if (scope === 'gated') {
        gatedBtn.className = "py-2.5 rounded-xl bg-white text-beige-900 shadow-soft transition flex items-center justify-center gap-2";
        cityBtn.className = "py-2.5 rounded-xl text-beige-600 hover:text-beige-900 transition flex items-center justify-center gap-2";
        gatedFields.classList.remove('hidden');
      } else {
        cityBtn.className = "py-2.5 rounded-xl bg-white text-beige-900 shadow-soft transition flex items-center justify-center gap-2";
        gatedBtn.className = "py-2.5 rounded-xl text-beige-600 hover:text-beige-900 transition flex items-center justify-center gap-2";
        gatedFields.classList.add('hidden');
      }
    }

    function handleImageUpload(event) {
      const file = event.target.files[0];
      if (!file) return;
      uploadedFile = file;

      const reader = new FileReader();
      reader.onload = function(e) {
        // Show the AI result panel with user's image
        document.getElementById('ai-placeholder').classList.add('hidden');
        document.getElementById('ai-result').classList.remove('hidden');
        document.getElementById('ai-preview-img').src = e.target.result;
        document.getElementById('ai-file-name').innerText = file.name + ' (' + (file.size / 1024).toFixed(1) + ' KB)';

        // Simulate AI classification based on file name / form context
        const scope = document.getElementById('form-scope').value;
        const confidence = (88 + Math.random() * 10).toFixed(1);
        document.getElementById('ai-confidence').innerText = confidence + '% Confidence';

        const hazards = scope === 'gated'
          ? ['Parking Encroachment', 'Elevator Fault', 'Security Breach', 'Noise Violation', 'Water Leakage']
          : ['Severe Structural Pothole', 'Road Surface Crack', 'Drainage Overflow', 'Exposed Wiring', 'Broken Footpath'];
        const risks = ['Critical - Immediate Action', 'High Risk - Priority Queue', 'Medium Risk - Scheduled', 'Elevated - Monitor'];
        const defects = scope === 'gated'
          ? ['VIOLATION-01: Society Rule Breach', 'INFRA-01: Equipment Failure', 'SAFETY-01: Access Control Gap']
          : ['DEFECT-01: Asphalt Cavity (0.9m)', 'DEFECT-01: Surface Erosion', 'DEFECT-01: Infrastructure Damage'];

        // Animate with a brief delay to simulate processing
        document.getElementById('ai-hazard-type').innerText = 'Processing...';
        document.getElementById('ai-risk-level').innerText = 'Scanning...';
        document.getElementById('ai-defect-label').innerText = 'Analyzing...';

        setTimeout(() => {
          document.getElementById('ai-hazard-type').innerText = hazards[Math.floor(Math.random() * hazards.length)];
          document.getElementById('ai-risk-level').innerText = risks[Math.floor(Math.random() * risks.length)];
          document.getElementById('ai-defect-label').innerText = defects[Math.floor(Math.random() * defects.length)];
        }, 1200);
      };
      reader.readAsDataURL(file);
    }

    function clearUpload() {
      uploadedFile = null;
      document.getElementById('form-image').value = '';
      document.getElementById('ai-result').classList.add('hidden');
      document.getElementById('ai-placeholder').classList.remove('hidden');
      document.getElementById('ai-preview-img').src = '';
    }

    function triggerAIAnalysis() {
      document.getElementById('form-image').click();
    }

    // ── Submit Report (API with image upload) ──
    async function submitReport(e) {
      e.preventDefault();
      const scope = document.getElementById('form-scope').value;
      const isGated = scope === 'gated';

      // Build FormData to support file upload
      const formData = new FormData();
      formData.append('scope', scope);
      formData.append('title', document.getElementById('form-title').value);
      formData.append('location', document.getElementById('form-location').value);
      formData.append('description', document.getElementById('form-desc').value);
      formData.append('severityScore', '92');
      if (isGated) {
        formData.append('society', document.getElementById('form-society').value);
        formData.append('unit', document.getElementById('form-unit').value || 'General Common Area');
      }

      // Attach uploaded image if present
      // Await geolocation before submission
      await new Promise((resolve) => {
        if (navigator.geolocation) {
          navigator.geolocation.getCurrentPosition(
            (pos) => {
              formData.append('lat', pos.coords.latitude);
              formData.append('lng', pos.coords.longitude);
              resolve();
            },
            () => { console.warn("No GPS"); resolve(); },
            { timeout: 3000 }
          );
        } else {
          resolve();
        }
      });

      if (uploadedFile) {
        formData.append('image', uploadedFile);
      } else {
        // Fallback placeholder image
        formData.append('image_url', isGated
          ? 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=700&q=80'
          : 'https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=700&q=80');
      }

      try {
        const res = await fetch(`${API}/api/tickets`, {
          method: 'POST',
          body: formData  // No Content-Type header — browser sets multipart boundary
        });
        const data = await res.json();
        userKarma = data.karma;
        document.getElementById('user-karma-badge').innerText = userKarma + ' PTS';
      } catch(err) { console.error('Submit failed', err); }

      uploadedFile = null;
      await loadTickets();
      await loadStats();
      closeModal();
      clearUpload();
      e.target.reset();
      triggerToast(`+50 Karma! Incident registered & mapped successfully.`);
    }

    // ── CSV Export (API) ──
    function downloadCSVReport() {
      window.location.href = `${API}/api/export/csv`;
      triggerToast("CSV Audit file generated and downloaded.");
    }

    // ── Toast ──
    function triggerToast(text) {
      const toast = document.getElementById('toast');
      document.getElementById('toast-text').innerText = text;
      toast.classList.remove('opacity-0', 'translate-y-24', 'pointer-events-none');
      setTimeout(() => { toast.classList.add('opacity-0', 'translate-y-24', 'pointer-events-none'); }, 3500);
    }
  