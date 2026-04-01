"""
VLM Visual Office — Live Data Server
Serves visual_office.html on port 5001 + /api/status endpoint
Pulls live agent data from Paperclip (http://localhost:3100)
Run: /opt/homebrew/bin/python3.11 office_server.py
"""
import json, os, glob
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError

BASE  = Path(__file__).parent
TMP   = BASE / '.tmp'

# ── Paperclip config ──────────────────────────────────────────────────────────
PC_URL  = 'http://localhost:3100'
PC_IDS  = BASE / '.paperclip_ids.json'

AGENT_COLORS = {
    'outreach':   '#00ff88',
    'autoposter': '#ff00cc',
    'gmail':      '#ff3333',
    'crm':        '#3399ff',
    'gemini':     '#00eeff',
    'kling':      '#cc00ff',
    'claude':     '#ffd700',
    'developer':  '#ff8800',
    'designer':   '#ff44aa',
}

ROLE_STATUS = {
    'ceo':      'ORCHESTRATING',
    'cmo':      'POSTING',
    'cto':      'OUTREACHING',
    'engineer': 'BUILDING',
    'designer': 'DESIGNING',
    'general':  'WATCHING',
}

def read_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default

def pc_get(path):
    """Fetch from Paperclip API (local_trusted — no auth needed)."""
    try:
        req = Request(f'{PC_URL}{path}', headers={'Accept': 'application/json'})
        with urlopen(req, timeout=3) as r:
            return json.loads(r.read())
    except Exception:
        return None

def build_paperclip_status(pc_ids):
    """Pull live agent + task data from Paperclip."""
    cid = pc_ids.get('company_id')
    agent_ids = pc_ids.get('agents', {})

    # Fetch all agents
    agents_data = pc_get(f'/api/companies/{cid}/agents') or []
    agents_map = {a['id']: a for a in (agents_data if isinstance(agents_data, list) else agents_data.get('agents', []))}

    # Fetch recent issues (tasks)
    issues_raw = pc_get(f'/api/companies/{cid}/issues?status=todo,in_progress,in_review,blocked') or []
    issues = issues_raw if isinstance(issues_raw, list) else issues_raw.get('issues', [])

    # Build activity from recent issues/tasks
    activity = []
    for issue in issues[-8:]:
        assignee_id = issue.get('assigneeAgentId')
        agent_obj   = agents_map.get(assignee_id, {})
        agent_name  = agent_obj.get('name', 'SYSTEM')
        ag_key      = agent_name.lower().replace(' ', '').replace('-', '')
        color       = next((v for k, v in AGENT_COLORS.items() if k in ag_key), '#aaaaaa')
        ts          = (issue.get('updatedAt') or issue.get('createdAt') or '')
        time_str    = ts[11:16] if len(ts) >= 16 else ''
        activity.append({
            'time':   time_str,
            'agent':  agent_name.upper(),
            'action': f"[{issue.get('status','?').upper()}] {issue.get('title','')[:60]}",
            'color':  color,
        })

    # Agent statuses
    agent_statuses = {}
    for key, aid in agent_ids.items():
        a = agents_map.get(aid, {})
        if a:
            agent_statuses[key] = {
                'name':   a.get('name', key),
                'status': ROLE_STATUS.get(a.get('role',''), 'ACTIVE'),
                'budget_cents': a.get('monthlyBudgetCents', 0),
                'spent_cents':  a.get('spentMonthlyCents', 0),
            }

    # Company spend
    company = pc_get(f'/api/companies/{cid}') or {}
    budget  = company.get('budgetMonthlyCents', 0)
    spent   = company.get('spentMonthlyCents', 0)

    return activity, agent_statuses, budget, spent, len(issues)

def build_status():
    # ── Leads (from .tmp) ────────────────────────────────────────────────────
    leads       = read_json(TMP / 'leads.json', [])
    leads_total = len(leads) if isinstance(leads, list) else 0
    emails_sent = sum(1 for l in leads if isinstance(l, dict) and l.get('email_1_sent')) if isinstance(leads, list) else 0

    # ── Queued posts (from .tmp) ──────────────────────────────────────────────
    approved   = read_json(TMP / 'approved_posts.json', [])
    shay_sched = read_json(TMP / 'shay_schedule.json',  [])
    neo_sched  = read_json(TMP / 'neo_schedule.json',   [])
    queued = sum([
        len([p for p in (approved   if isinstance(approved,   list) else []) if not p.get('posted')]),
        len([p for p in (shay_sched if isinstance(shay_sched, list) else []) if not p.get('posted')]),
        len([p for p in (neo_sched  if isinstance(neo_sched,  list) else []) if not p.get('posted')]),
    ])

    # ── Paperclip live data ───────────────────────────────────────────────────
    pc_ids    = read_json(PC_IDS, {})
    pc_active = bool(pc_ids)
    activity  = []
    agent_statuses = {}
    budget_cents = spent_cents = active_tasks = 0

    if pc_active:
        try:
            activity, agent_statuses, budget_cents, spent_cents, active_tasks = build_paperclip_status(pc_ids)
        except Exception as e:
            pc_active = False

    # ── Fallback: activity from .tmp logs ─────────────────────────────────────
    if not activity:
        raw_activity = read_json(TMP / 'activity_log.json', [])
        if isinstance(raw_activity, list):
            for item in raw_activity[-12:]:
                if isinstance(item, dict):
                    ag    = item.get('agent', item.get('source', 'system')).lower()
                    color = next((v for k, v in AGENT_COLORS.items() if k in ag), '#aaaaaa')
                    activity.append({
                        'time':   (item.get('time') or item.get('timestamp') or '')[:5],
                        'agent':  item.get('agent', item.get('source', 'SYSTEM')).upper(),
                        'action': item.get('action', item.get('message', item.get('event', ''))),
                        'color':  color,
                    })

    return {
        'leads_total':     leads_total,
        'emails_sent':     emails_sent,
        'queued_posts':    queued,
        'active_tasks':    active_tasks,
        'budget_cents':    budget_cents,
        'spent_cents':     spent_cents,
        'agents':          agent_statuses,
        'paperclip_active': pc_active,
        'paperclip_url':   PC_URL,
        'activity':        activity[-8:],
        'ts':              datetime.now().isoformat(),
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass  # suppress request logs

    def send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
        self.end_headers()

    def do_POST(self):
        """Webhook receiver for Paperclip HTTP adapter heartbeats."""
        if self.path.startswith('/webhooks/'):
            length = int(self.headers.get('Content-Length', 0))
            body   = json.loads(self.rfile.read(length) or b'{}')
            agent  = self.path[len('/webhooks/'):]
            # Log the heartbeat to activity_log
            log_path = TMP / 'activity_log.json'
            try:
                log = read_json(log_path, [])
                if not isinstance(log, list): log = []
                log.append({
                    'time':   datetime.now().strftime('%H:%M'),
                    'agent':  agent.upper(),
                    'action': f"Heartbeat — {body.get('wakeReason','scheduled')}",
                })
                log_path.write_text(json.dumps(log[-50:]))
            except Exception: pass
            data = json.dumps({'ok': True}).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(data))
            self.send_cors()
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()

    def do_GET(self):
        if self.path in ('/', '/visual_office', '/visual_office.html'):
            html = (BASE / 'visual_office.html').read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', len(html))
            self.send_cors()
            self.end_headers()
            self.wfile.write(html)

        elif self.path == '/api/status':
            data = json.dumps(build_status()).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(data))
            self.send_cors()
            self.end_headers()
            self.wfile.write(data)

        elif self.path == '/api/paperclip/agents':
            """Proxy Paperclip agents list for the office canvas."""
            pc_ids = read_json(PC_IDS, {})
            cid    = pc_ids.get('company_id', '')
            result = pc_get(f'/api/companies/{cid}/agents') or []
            data   = json.dumps(result).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(data))
            self.send_cors()
            self.end_headers()
            self.wfile.write(data)

        elif self.path == '/api/paperclip/issues':
            pc_ids = read_json(PC_IDS, {})
            cid    = pc_ids.get('company_id', '')
            result = pc_get(f'/api/companies/{cid}/issues') or []
            data   = json.dumps(result).encode()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(data))
            self.send_cors()
            self.end_headers()
            self.wfile.write(data)

        elif self.path.startswith('/assets/'):
            fname      = self.path[len('/assets/'):]
            asset_path = BASE / 'assets' / fname
            if asset_path.exists() and asset_path.suffix in ('.png', '.jpg', '.jpeg'):
                data = asset_path.read_bytes()
                self.send_response(200)
                ct = 'image/jpeg' if asset_path.suffix in ('.jpg', '.jpeg') else 'image/png'
                self.send_header('Content-Type', ct)
                self.send_header('Content-Length', len(data))
                self.send_cors()
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(404)
                self.end_headers()

        elif self.path.startswith('/sprites/'):
            fname       = self.path[len('/sprites/'):]
            sprite_path = BASE / 'assets' / 'sprites' / fname
            if sprite_path.exists() and sprite_path.suffix in ('.png', '.jpg', '.gif'):
                data = sprite_path.read_bytes()
                self.send_response(200)
                ct = 'image/gif' if sprite_path.suffix == '.gif' else 'image/png'
                self.send_header('Content-Type', ct)
                self.send_header('Content-Length', len(data))
                self.send_cors()
                self.end_headers()
                self.wfile.write(data)
            else:
                self.send_response(404)
                self.end_headers()

        else:
            self.send_response(404)
            self.end_headers()


if __name__ == '__main__':
    port   = 5001
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'\n  VLM Visual Office + Paperclip')
    print(f'  ─────────────────────────────────────')
    print(f'  http://localhost:{port}/visual_office')
    print(f'  http://localhost:{port}/api/status')
    print(f'  Paperclip → {PC_URL}')
    print(f'  ─────────────────────────────────────')
    print(f'  Ctrl+C to stop\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Server stopped.')
