// ============================================================================
//  agent.js — tiny receiver to run ON a target machine so it can RECEIVE the
//  "send message" action from the topology UI.
//
//  Run on each machine you want to message:   node agent.js
//  It listens on :9911 and, when a message arrives, prints it and pops a
//  Windows message box to the logged-in user (local `msg *`, no remote RPC).
//
//  Zero dependencies. Read-only except for showing a popup. Your own machines.
// ============================================================================

const http = require("http");
const os = require("os");
const { exec } = require("child_process");

const PORT = 9911;

http.createServer((req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  if (req.method === "OPTIONS") { res.writeHead(204); res.end(); return; }

  if (req.url === "/info") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ agent: true, host: os.hostname() }));
    return;
  }

  if (req.url === "/message" && req.method === "POST") {
    let body = "";
    req.on("data", (c) => (body += c));
    req.on("end", () => {
      let text = "(empty)", from = "";
      try { const j = JSON.parse(body || "{}"); text = j.text || text; from = j.from || ""; } catch {}
      const stamp = new Date().toLocaleTimeString();
      const peer = from || req.socket.remoteAddress;
      console.log(`\n📨  [${stamp}]  from ${peer}:  ${text}\n`);

      // pop a message box on this machine. Uses PowerShell + WinForms so it
      // works on Windows Home (where msg.exe is absent). Non-blocking.
      const safe = String(text).replace(/'/g, "''");
      const ps = `Add-Type -AssemblyName System.Windows.Forms; ` +
        `[System.Windows.Forms.MessageBox]::Show('${safe}','📨 Topology message from ${String(peer).replace(/'/g, "''")}')`;
      exec(`powershell -NoProfile -WindowStyle Hidden -Command "${ps.replace(/"/g, '\\"')}"`, { windowsHide: true }, () => {});

      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ ok: true, host: os.hostname() }));
    });
    return;
  }

  res.writeHead(404); res.end("topology-agent");
}).listen(PORT, () => {
  console.log(`topology-agent  →  listening on :${PORT}  (host: ${os.hostname()})`);
  console.log(`waiting for messages from the topology UI…`);
});
