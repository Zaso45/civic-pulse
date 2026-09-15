import re
import os

html_path = r'C:\Users\home\.gemini\antigravity\scratch\civicpulse\static\index.html'

with open(html_path, 'r', encoding='utf-8') as f:
    html = f.read()

# Fix the switchView('authority') that got mistakenly replaced
html = html.replace("onclick=\"document.getElementById('auth-modal').classList.remove('hidden')\"", "onclick=\"switchView('authority')\"")

# Fix the auth check that was broken
broken_auth = """                if (currentUser.role === 'municipal' || currentUser.role === 'rwa') {
                    document.getElementById('auth-modal').classList.remove('hidden');
                }"""
fixed_auth = """                if (currentUser.role === 'municipal' || currentUser.role === 'rwa') {
                    switchView('authority');
                }"""
html = html.replace(broken_auth, fixed_auth)

# Add a dedicated login button trigger in the top bar to open the modal properly
old_topbar = """        <span class="underline cursor-pointer hover:text-beige-900" onclick="switchView('authority')">RWA / Municipal Sign In &rarr;</span>"""
new_topbar = """        <span class="underline cursor-pointer hover:text-beige-900" onclick="document.getElementById('auth-modal').classList.remove('hidden')">RWA / Municipal Sign In &rarr;</span>"""
html = html.replace(old_topbar, new_topbar)


with open(html_path, 'w', encoding='utf-8') as f:
    f.write(html)

