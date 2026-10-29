// Minimal stdio JSON-RPC client for the Canvas Authoring MCP server.
// Usage: node tools/mcp-canvas.js <calls.json>
// calls.json: [ { "tool": "connect", "args": { ... } }, { "tool": "compile_canvas", "args": { "directoryPath": "..." } } ]
// Prints each tool result as text. Keeps one server process for the whole sequence.
const { spawn } = require('child_process');
const fs = require('fs');

const callsFile = process.argv[2];
if (!callsFile) { console.error('usage: node mcp-canvas.js <calls.json>'); process.exit(2); }
const calls = JSON.parse(fs.readFileSync(callsFile, 'utf8'));
const timeoutMs = Number(process.env.MCP_TIMEOUT_MS || 180000);

const proc = spawn('cmd.exe', ['/d', '/s', '/c', 'dnx Microsoft.PowerApps.CanvasAuthoring.McpServer --yes'], { stdio: ['pipe', 'pipe', 'pipe'], windowsVerbatimArguments: true });
let buffer = '';
const pending = new Map();
let nextId = 1;

proc.stderr.on('data', d => { if (process.env.MCP_VERBOSE) process.stderr.write(d.toString()); });
proc.stdout.on('data', d => {
  buffer += d.toString();
  let idx;
  while ((idx = buffer.indexOf('\n')) >= 0) {
    const line = buffer.slice(0, idx).trim();
    buffer = buffer.slice(idx + 1);
    if (!line.startsWith('{')) continue;
    let msg; try { msg = JSON.parse(line); } catch { continue; }
    if (msg.id !== undefined && pending.has(msg.id)) { pending.get(msg.id)(msg); pending.delete(msg.id); }
    else if (msg.method === 'elicitation/create' && msg.id !== undefined) {
      // Server asks the user for input (device-code sign-in). Print it and accept so the server keeps waiting for the user.
      console.log('\n===== SIGN-IN REQUIRED =====\n' + (msg.params && msg.params.message ? msg.params.message : JSON.stringify(msg.params)));
      proc.stdin.write(JSON.stringify({ jsonrpc: '2.0', id: msg.id, result: { action: 'accept', content: {} } }) + '\n');
    }
    else if (msg.method) { if (process.env.MCP_VERBOSE) console.error('[notify]', JSON.stringify(msg).slice(0, 500)); }
  }
});

function request(method, params) {
  const id = nextId++;
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => { pending.delete(id); reject(new Error(`timeout waiting for ${method}`)); }, timeoutMs);
    pending.set(id, msg => { clearTimeout(t); resolve(msg); });
    proc.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
  });
}
function notify(method, params) { proc.stdin.write(JSON.stringify({ jsonrpc: '2.0', method, params }) + '\n'); }

(async () => {
  try {
    await request('initialize', { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'galaxian-build', version: '0.1' } });
    notify('notifications/initialized');
    for (const c of calls) {
      const res = await request('tools/call', { name: c.tool, arguments: c.args || {} });
      console.log(`\n===== ${c.tool} =====`);
      if (res.error) { console.log('ERROR: ' + JSON.stringify(res.error)); continue; }
      const content = (res.result && res.result.content) || [];
      for (const part of content) console.log(part.type === 'text' ? part.text : JSON.stringify(part));
      if (res.result && res.result.isError) console.log('(isError=true)');
    }
  } catch (e) { console.error('FAILED: ' + e.message); process.exitCode = 1; }
  finally { proc.kill(); setTimeout(() => process.exit(), 200); }
})();
