"""
SLP Central Server Hub - Main Entry Point

Serves the web-based control dashboard on port 5000.
"""

import os
import json
import asyncio
import logging
import subprocess
import sys
from datetime import datetime
from typing import Dict, Any, List, Optional

import psutil
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="SLP Central Server Hub", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES: Dict[str, Dict[str, Any]] = {
    "klar": {
        "name": "Klar",
        "sl_id": "klar-001",
        "port": 4271,
        "status": "offline",
        "auto_restart": True,
        "domain": "klar.oscyra.solutions",
        "process": None,
        "uptime_start": None,
        "requests": 0,
        "latency_ms": 0,
        "error_rate": 0.0,
    },
    "sverkan": {
        "name": "Sverkan",
        "sl_id": "sverkan-001",
        "port": 4272,
        "status": "offline",
        "auto_restart": True,
        "domain": "sverkan.oscyra.solutions",
        "process": None,
        "uptime_start": None,
        "requests": 0,
        "latency_ms": 0,
        "error_rate": 0.0,
    },
    "upsum": {
        "name": "Upsum",
        "sl_id": "upsum-001",
        "port": 4273,
        "status": "offline",
        "auto_restart": False,
        "domain": "upsum.oscyra.solutions",
        "process": None,
        "uptime_start": None,
        "requests": 0,
        "latency_ms": 0,
        "error_rate": 0.0,
    },
    "testview": {
        "name": "TestView",
        "sl_id": "testview-001",
        "port": 4274,
        "status": "offline",
        "auto_restart": False,
        "domain": "testview.oscyra.solutions",
        "process": None,
        "uptime_start": None,
        "requests": 0,
        "latency_ms": 0,
        "error_rate": 0.0,
        "bridge_port": 9001,
    },
}

LOG_STORE: Dict[str, List[str]] = {k: [] for k in SERVICES}
active_connections: List[WebSocket] = []


def get_service_status_summary():
    result = {}
    for key, svc in SERVICES.items():
        uptime = None
        if svc["uptime_start"]:
            delta = datetime.now() - svc["uptime_start"]
            uptime = str(delta).split(".")[0]
        result[key] = {
            "name": svc["name"],
            "sl_id": svc["sl_id"],
            "port": svc["port"],
            "status": svc["status"],
            "auto_restart": svc["auto_restart"],
            "domain": svc["domain"],
            "uptime": uptime,
            "requests": svc["requests"],
            "latency_ms": svc["latency_ms"],
            "error_rate": svc["error_rate"],
        }
    return result


def add_log(service_key: str, message: str, level: str = "INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    entry = f"[{ts}] {level}: {message}"
    LOG_STORE[service_key].append(entry)
    if len(LOG_STORE[service_key]) > 500:
        LOG_STORE[service_key] = LOG_STORE[service_key][-500:]


async def broadcast(data: dict):
    disconnected = []
    for ws in active_connections:
        try:
            await ws.send_json(data)
        except Exception:
            disconnected.append(ws)
    for ws in disconnected:
        active_connections.remove(ws)


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SLP Control Hub</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
      color: #e0e0e0;
      min-height: 100vh;
    }
    header {
      background: rgba(0,229,255,0.05);
      border-bottom: 1px solid rgba(0,229,255,0.2);
      padding: 1rem 2rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }
    header h1 {
      font-size: 1.6rem;
      background: linear-gradient(135deg, #00e5ff, #00ffa3);
      -webkit-background-clip: text;
      background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .tabs {
      display: flex;
      gap: 1rem;
    }
    .tab-btn {
      background: transparent;
      border: 1px solid rgba(0,229,255,0.3);
      color: #00e5ff;
      padding: 0.5rem 1.5rem;
      border-radius: 50px;
      cursor: pointer;
      font-size: 0.9rem;
      transition: all 0.2s;
    }
    .tab-btn.active, .tab-btn:hover {
      background: rgba(0,229,255,0.15);
    }
    .tab-content { display: none; padding: 2rem; }
    .tab-content.active { display: block; }
    .section-title {
      font-size: 1.2rem;
      color: #00e5ff;
      margin-bottom: 1.5rem;
      font-weight: 600;
    }
    .services-table {
      width: 100%;
      border-collapse: collapse;
      background: rgba(255,255,255,0.03);
      border-radius: 8px;
      overflow: hidden;
    }
    .services-table th {
      background: rgba(0,229,255,0.1);
      color: #00e5ff;
      padding: 1rem;
      text-align: left;
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .services-table td {
      padding: 1rem;
      border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .badge {
      display: inline-block;
      padding: 0.3rem 0.8rem;
      border-radius: 50px;
      font-size: 0.8rem;
      font-weight: 600;
    }
    .badge.online { background: rgba(0,255,163,0.2); color: #00ffa3; }
    .badge.offline { background: rgba(255,255,255,0.08); color: #888; }
    .badge.starting { background: rgba(255,200,0,0.2); color: #ffc800; }
    .badge.error { background: rgba(255,68,68,0.2); color: #ff4444; }
    .btn-group { display: flex; gap: 0.5rem; }
    .btn {
      background: transparent;
      border: 1px solid rgba(0,229,255,0.4);
      color: #00e5ff;
      padding: 0.4rem 1rem;
      border-radius: 6px;
      cursor: pointer;
      font-size: 0.85rem;
      transition: all 0.2s;
    }
    .btn:hover { background: rgba(0,229,255,0.1); }
    .btn.danger { border-color: rgba(255,68,68,0.4); color: #ff4444; }
    .btn.danger:hover { background: rgba(255,68,68,0.1); }
    .btn.success { border-color: rgba(0,255,163,0.4); color: #00ffa3; }
    .btn.success:hover { background: rgba(0,255,163,0.1); }
    .protocol-card {
      background: rgba(0,229,255,0.05);
      border: 1px solid rgba(0,229,255,0.2);
      border-radius: 8px;
      padding: 1.5rem;
      margin-top: 2rem;
    }
    .protocol-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
      margin-top: 1rem;
    }
    .metric-card {
      background: rgba(255,255,255,0.03);
      border: 1px solid rgba(0,229,255,0.15);
      border-radius: 8px;
      padding: 1rem;
    }
    .metric-card .label {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 1px;
      color: #888;
      margin-bottom: 0.5rem;
    }
    .metric-card .value {
      font-size: 1.4rem;
      color: #00e5ff;
      font-weight: 600;
    }
    .log-panel {
      background: #050505;
      border: 1px solid rgba(0,229,255,0.15);
      border-radius: 8px;
      padding: 1rem;
      height: 350px;
      overflow-y: auto;
      font-family: 'Courier New', monospace;
      font-size: 0.85rem;
    }
    .log-panel .log-line { padding: 0.2rem 0; color: #00e5ff; }
    .log-panel .log-line.warn { color: #ffc800; }
    .log-panel .log-line.error { color: #ff4444; }
    .log-panel .log-line.success { color: #00ffa3; }
    .slc-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 1.5rem;
    }
    .slc-card {
      background: rgba(255,255,255,0.03);
      border: 1px solid rgba(0,229,255,0.15);
      border-radius: 8px;
      padding: 1.2rem;
    }
    .slc-card h3 { color: #00e5ff; margin-bottom: 1rem; font-size: 1rem; }
    .slc-stat { display: flex; justify-content: space-between; margin: 0.5rem 0; font-size: 0.9rem; }
    .slc-stat .k { color: #888; }
    .slc-stat .v { color: #e0e0e0; font-weight: 500; }
    .service-selector {
      display: flex;
      gap: 0.5rem;
      margin-bottom: 1rem;
      flex-wrap: wrap;
    }
    .ws-status {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 0.8rem;
      color: #888;
    }
    .ws-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #ff4444;
    }
    .ws-dot.connected { background: #00ffa3; animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
  </style>
</head>
<body>
  <header>
    <h1>SLP Central Server Hub</h1>
    <div style="display:flex;align-items:center;gap:1.5rem;">
      <div class="ws-status">
        <div class="ws-dot" id="wsDot"></div>
        <span id="wsLabel">Connecting...</span>
      </div>
      <div class="tabs">
        <button class="tab-btn active" onclick="showTab('dcc')">Control Center</button>
        <button class="tab-btn" onclick="showTab('slc')">Status Logs</button>
      </div>
    </div>
  </header>

  <!-- DCC -->
  <div id="tab-dcc" class="tab-content active">
    <div class="section-title">Services</div>
    <table class="services-table">
      <thead>
        <tr>
          <th>Service</th>
          <th>SL-ID</th>
          <th>Port</th>
          <th>Status</th>
          <th>Uptime</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody id="serviceRows"></tbody>
    </table>

    <div class="protocol-card">
      <div class="section-title">SL Protocol Status</div>
      <div class="protocol-grid">
        <div class="metric-card">
          <div class="label">Core</div>
          <div class="value" id="protoCore">Active</div>
        </div>
        <div class="metric-card">
          <div class="label">Encryption</div>
          <div class="value" style="font-size:1rem;">DTLS 1.3 + Noise</div>
        </div>
        <div class="metric-card">
          <div class="label">Base Port</div>
          <div class="value">4270</div>
        </div>
        <div class="metric-card">
          <div class="label">Active Services</div>
          <div class="value" id="activeCount">0</div>
        </div>
      </div>
    </div>
  </div>

  <!-- SLC -->
  <div id="tab-slc" class="tab-content">
    <div class="slc-grid" id="slcGrid"></div>

    <div style="margin-top:2rem;">
      <div class="section-title">Live Log Output</div>
      <div class="service-selector" id="logSelector"></div>
      <div class="log-panel" id="logPanel">
        <div class="log-line">[system] Select a service to view logs</div>
      </div>
    </div>
  </div>

  <script>
    let services = {};
    let selectedLogService = null;
    let ws = null;

    function showTab(name) {
      document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
      document.getElementById('tab-' + name).classList.add('active');
      event.target.classList.add('active');
    }

    function renderServices() {
      const tbody = document.getElementById('serviceRows');
      tbody.innerHTML = '';
      let active = 0;
      for (const [key, svc] of Object.entries(services)) {
        if (svc.status === 'online') active++;
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><strong>${svc.name}</strong><br><small style="color:#888">${svc.domain}</small></td>
          <td style="font-family:monospace;color:#888">${svc.sl_id}</td>
          <td>${svc.port}</td>
          <td><span class="badge ${svc.status}">${svc.status.toUpperCase()}</span></td>
          <td style="color:#888;font-size:0.9rem">${svc.uptime || '--'}</td>
          <td>
            <div class="btn-group">
              ${svc.status === 'online'
                ? `<button class="btn danger" onclick="serviceAction('${key}','stop')">Stop</button>
                   <button class="btn" onclick="serviceAction('${key}','restart')">Restart</button>`
                : `<button class="btn success" onclick="serviceAction('${key}','start')">Start</button>`
              }
            </div>
          </td>
        `;
        tbody.appendChild(tr);
      }
      document.getElementById('activeCount').textContent = active;
    }

    function renderSLC() {
      const grid = document.getElementById('slcGrid');
      grid.innerHTML = '';
      for (const [key, svc] of Object.entries(services)) {
        const card = document.createElement('div');
        card.className = 'slc-card';
        card.innerHTML = `
          <h3>
            <span style="display:inline-block;width:10px;height:10px;border-radius:50%;
              background:${svc.status==='online'?'#00ffa3':'#ff4444'};
              margin-right:0.5rem;"></span>
            ${svc.name}
          </h3>
          <div class="slc-stat"><span class="k">Status</span><span class="v">${svc.status.toUpperCase()}</span></div>
          <div class="slc-stat"><span class="k">SL-ID</span><span class="v" style="font-family:monospace">${svc.sl_id}</span></div>
          <div class="slc-stat"><span class="k">Port</span><span class="v">${svc.port}</span></div>
          <div class="slc-stat"><span class="k">Uptime</span><span class="v">${svc.uptime||'--'}</span></div>
          <div class="slc-stat"><span class="k">Requests</span><span class="v">${svc.requests}</span></div>
          <div class="slc-stat"><span class="k">Latency</span><span class="v">${svc.latency_ms}ms</span></div>
          <div class="slc-stat"><span class="k">Error Rate</span><span class="v">${(svc.error_rate*100).toFixed(1)}%</span></div>
        `;
        grid.appendChild(card);
      }

      const sel = document.getElementById('logSelector');
      sel.innerHTML = '';
      for (const [key, svc] of Object.entries(services)) {
        const btn = document.createElement('button');
        btn.className = 'btn' + (selectedLogService === key ? ' active' : '');
        btn.textContent = svc.name;
        btn.onclick = () => {
          selectedLogService = key;
          fetchLogs(key);
          document.querySelectorAll('#logSelector .btn').forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
        };
        sel.appendChild(btn);
      }
    }

    async function fetchLogs(serviceKey) {
      const res = await fetch('/api/logs/' + serviceKey);
      const data = await res.json();
      const panel = document.getElementById('logPanel');
      panel.innerHTML = '';
      for (const line of data.logs) {
        const div = document.createElement('div');
        div.className = 'log-line' +
          (line.includes('ERROR') ? ' error' : line.includes('WARN') ? ' warn' : line.includes('SUCCESS') ? ' success' : '');
        div.textContent = line;
        panel.appendChild(div);
      }
      panel.scrollTop = panel.scrollHeight;
    }

    async function serviceAction(key, action) {
      await fetch('/api/services/' + key + '/' + action, { method: 'POST' });
    }

    function connectWS() {
      const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
      ws = new WebSocket(protocol + '://' + location.host + '/ws');
      ws.onopen = () => {
        document.getElementById('wsDot').classList.add('connected');
        document.getElementById('wsLabel').textContent = 'Live';
      };
      ws.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === 'services') {
          services = msg.data;
          renderServices();
          renderSLC();
          if (selectedLogService) fetchLogs(selectedLogService);
        }
      };
      ws.onclose = () => {
        document.getElementById('wsDot').classList.remove('connected');
        document.getElementById('wsLabel').textContent = 'Disconnected';
        setTimeout(connectWS, 3000);
      };
    }

    connectWS();
  </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def root():
    return DASHBOARD_HTML


@app.get("/dcc", response_class=HTMLResponse)
async def dcc():
    return DASHBOARD_HTML


@app.get("/slc", response_class=HTMLResponse)
async def slc():
    return DASHBOARD_HTML


@app.get("/testview-001/", response_class=HTMLResponse)
async def testview_root():
    with open("testview.html", "r") as f:
        return f.read()


@app.get("/testview-001/{path:path}", response_class=HTMLResponse)
async def testview_path(path: str):
    with open("testview.html", "r") as f:
        content = f.read()
    add_log("testview", f"HTTPS→SLP bridge: GET /testview-001/{path}", "INFO")
    return content


@app.get("/api/services")
async def get_services():
    return JSONResponse(get_service_status_summary())


@app.post("/api/services/{service_key}/{action}")
async def service_action(service_key: str, action: str):
    if service_key not in SERVICES:
        return JSONResponse({"error": "Service not found"}, status_code=404)

    svc = SERVICES[service_key]

    if action == "start":
        if svc["status"] == "online":
            return JSONResponse({"message": "Already running"})
        svc["status"] = "online"
        svc["uptime_start"] = datetime.now()
        add_log(service_key, f"{svc['name']} service started", "SUCCESS")
        await broadcast({"type": "services", "data": get_service_status_summary()})
        return JSONResponse({"message": f"{svc['name']} started"})

    elif action == "stop":
        if svc["status"] == "offline":
            return JSONResponse({"message": "Already stopped"})
        svc["status"] = "offline"
        svc["uptime_start"] = None
        add_log(service_key, f"{svc['name']} service stopped", "WARN")
        await broadcast({"type": "services", "data": get_service_status_summary()})
        return JSONResponse({"message": f"{svc['name']} stopped"})

    elif action == "restart":
        svc["status"] = "starting"
        add_log(service_key, f"{svc['name']} restarting...", "INFO")
        await broadcast({"type": "services", "data": get_service_status_summary()})
        await asyncio.sleep(1)
        svc["status"] = "online"
        svc["uptime_start"] = datetime.now()
        add_log(service_key, f"{svc['name']} restarted successfully", "SUCCESS")
        await broadcast({"type": "services", "data": get_service_status_summary()})
        return JSONResponse({"message": f"{svc['name']} restarted"})

    return JSONResponse({"error": "Unknown action"}, status_code=400)


@app.get("/api/logs/{service_key}")
async def get_logs(service_key: str):
    if service_key not in SERVICES:
        return JSONResponse({"error": "Service not found"}, status_code=404)
    return JSONResponse({"logs": LOG_STORE.get(service_key, [])})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        await websocket.send_json({
            "type": "services",
            "data": get_service_status_summary()
        })
        while True:
            await asyncio.sleep(5)
            await websocket.send_json({
                "type": "services",
                "data": get_service_status_summary()
            })
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info",
    )
