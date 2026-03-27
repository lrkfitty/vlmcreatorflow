"""
VLM Visual Office — Live Data Server
Serves visual_office.html on port 5001 + /api/status endpoint
Run: /opt/homebrew/bin/python3.11 office_server.py
"""
import json, os, glob
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime

BASE  = Path(__file__).parent
TMP   = BASE / '.tmp'

AGENT_COLORS = {
    'outreach':   '#00ff88',
    'autoposter': '#ff00cc',
    'gmail':      '#ff3333',
    'crm':        '#3399ff',
    'gemini':     '#00eeff',
    'kling':      '#cc00ff',
    'remotion':   '#ff4400',
    'claude':     '#ffd700',
}

def read_json(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default

def build_status():
    # ── Leads ────────────────────────────────────────────────────────────────
    leads = read_json(TMP / 'leads.json', [])
    leads_total = len(leads) if isinstance(leads, list) else 0
    emails_sent = sum(1 for l in leads if isinstance(l, dict) and l.get('email_1_sent')) if isinstance(leads, list) else 0

    # ── Queued posts ──────────────────────────────────────────────────────────
    approved = read_json(TMP / 'approved_posts.json', [])
    shay_sched  = read_json(TMP / 'shay_schedule.json',  [])
    neo_sched   = read_json(TMP / 'neo_schedule.json',   [])
    queued = sum([
        len([p for p in (approved if isinstance(approved, list) else []) if not p.get('posted')]),
        len([p for p in (shay_sched if isinstance(shay_sched, list) else []) if not p.get('posted')]),
        len([p for p in (neo_sched  if isinstance(neo_sched,  list) else []) if not p.get('posted')]),
    ])

    # ── Activity log ─────────────────────────────────────────────────────────
    raw_activity = read_json(TMP / 'activity_log.json', [])
    activity = []
    if isinstance(raw_activity, list):
        for item in raw_activity[-12:]:
            if isinstance(item, dict):
                ag = item.get('agent', item.get('source', 'system')).lower()
                color = next((v for k, v in AGENT_COLORS.items() if k in ag), '#aaaaaa')
                activity.append({
                    'time':   item.get('time', item.get('timestamp', ''))[:5] if item.get('time') or item.get('timestamp') else '',
                    'agent':  item.get('agent', item.get('source', 'SYSTEM')).upper(),
                    'action': item.get('action', item.get('message', item.get('event', ''))),
                    'color':  color,
                })
    elif isinstance(raw_activity, dict):
        # some logs are dicts keyed by timestamp
        for ts, val in list(raw_activity.items())[-12:]:
            activity.append({'time': ts[:5], 'agent': 'SYSTEM', 'action': str(val)[:60], 'color': '#aaaaaa'})

    # Supplement with cron log lines if activity sparse
    if len(activity) < 4:
        for log_file in [TMP / 'cron_post.log', TMP / 'outreach_cron.log']:
            if log_file.exists():
                lines = log_file.read_text().strip().splitlines()
                for line in lines[-6:]:
                    if line.strip():
                        parts = line[:19], line[20:]
                        ts = parts[0][-5:] if len(parts[0]) >= 5 else ''
                        activity.append({'time': ts, 'agent': log_file.stem.replace('_cron','').upper(), 'action': parts[1][:70] if len(parts) > 1 else line[:70], 'color': '#aaaaaa'})

    return {
        'leads_total':  leads_total,
        'emails_sent':  emails_sent,
        'queued_posts': queued,
        'activity':     activity[-8:],
        'ts':           datetime.now().isoformat(),
    }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass  # suppress request logs

    def send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_cors()
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

        elif self.path.startswith('/sprites/'):
            fname = self.path[len('/sprites/'):]
            sprite_path = BASE / 'assets' / 'sprites' / fname
            if sprite_path.exists() and sprite_path.suffix in ('.png', '.jpg'):
                data = sprite_path.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type', 'image/png')
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
    port = 5001
    server = HTTPServer(('0.0.0.0', port), Handler)
    print(f'\n  VLM Visual Office')
    print(f'  ─────────────────────────────────────')
    print(f'  http://localhost:{port}/visual_office')
    print(f'  http://localhost:{port}/api/status')
    print(f'  ─────────────────────────────────────')
    print(f'  Ctrl+C to stop\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  Server stopped.')
