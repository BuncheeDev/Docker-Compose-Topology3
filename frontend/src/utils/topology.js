/**
 * Topology Utilities - Constants and Helper Functions
 */

// ============================================================================
// Colors
// ============================================================================

export const C = {
  gray: [153, 153, 166],
  blue: [115, 179, 255],
  green: [89, 242, 140],
  orange: [255, 166, 51],
  purple: [191, 128, 255],
  red: [255, 89, 89],
  yellow: [255, 204, 77],
  teal: [64, 224, 208],
  pink: [255, 128, 191],
  lime: [180, 230, 80],
}

export const STATUS = {
  ok: C.green,
  warn: C.yellow,
  degraded: C.orange,
  alert: C.red,
  down: C.red,
  neutral: C.gray,
}

// ============================================================================
// Helper Functions
// ============================================================================

export const rgba = (c, a) => `rgba(${c[0]},${c[1]},${c[2]},${a})`
export const formatK = (n) => (n >= 1e6 ? (n / 1e6).toFixed(1) + 'M' : n >= 1e3 ? (n / 1e3).toFixed(1) + 'K' : '' + n)
export const clamp = (v, lo, hi) => Math.max(lo, Math.min(hi, v))
export const jitter = (v, amt) => v + (Math.random() * 2 - 1) * amt

// ============================================================================
// Line Builders
// ============================================================================

function vpsLines(m) {
  return [
    'LLM runtime · model',
    'MQTT · DB · logs · metrics',
    'agent + healthcheck',
    `${m.active}/${m.total} svc · ${m.incidents} open`,
    `LLM 24h: ${m.calls} calls · ${formatK(m.tokens)} tok`,
  ]
}

function hostLines(n) {
  const m = n.metrics
  return [
    ...n.descLines,
    m.summary,
    m.latency != null ? `latency ${Math.round(m.latency)} ms` : '',
  ].filter(Boolean)
}

// ============================================================================
// Layout Functions
// ============================================================================

export function autoPos(index, total, allNodes) {
  const hub = allNodes?.[0] ?? { pos: [0.43, 0.55] }
  const start = -Math.PI * 0.3
  const end = Math.PI * 0.62
  const a = total <= 1 ? (start + end) / 2 : start + ((end - start) * index) / (total - 1)
  return [
    clamp(hub.pos[0] + Math.cos(a) * 0.3, 0.06, 0.94),
    clamp(hub.pos[1] + Math.sin(a) * 0.34, 0.08, 0.92),
  ]
}

// ============================================================================
// Presets
// ============================================================================

export function makeSample() {
  const ns = [
    {
      id: 'user',
      glyph: '👤',
      title: 'You',
      sub: 'user',
      width: 140,
      pos: [0.1, 0.55],
      core: true,
      colorMode: 'fixed',
      color: C.gray,
      online: true,
      pulse: false,
      lines: ['macOS host', 'menubar 🟢'],
    },
    {
      id: 'mac',
      glyph: '💻',
      title: 'Mac',
      sub: 'monitor.app',
      width: 220,
      pos: [0.43, 0.55],
      core: true,
      colorMode: 'fixed',
      color: C.blue,
      online: true,
      pulse: true,
      lines: ['SwiftUI · MenuBarExtra', 'SQLite · Swift Charts', '6 live · 30 snaps'],
    },
    {
      id: 'vps',
      glyph: '☁️',
      title: 'primary',
      sub: 'Cloud · RTX PRO 4000',
      width: 270,
      pos: [0.82, 0.55],
      core: true,
      kind: 'vps',
      colorMode: 'status',
      status: 'ok',
      online: true,
      pulse: true,
      metrics: { active: 42, total: 44, incidents: 0, calls: 128, tokens: 1900000 },
    },
    {
      id: 'nodeA',
      glyph: '🗄️',
      title: 'Node A',
      sub: '10.0.0.11',
      width: 230,
      pos: [0.22, 0.22],
      core: true,
      kind: 'host',
      colorMode: 'status',
      status: 'ok',
      online: true,
      pulse: true,
      descLines: ['container host', 'vector-db · DB · cache · logs', 'admin · metrics · CI'],
      metrics: { summary: '12 svc up', latency: 3.2, base: '12 svc up' },
    },
    {
      id: 'nodeB',
      glyph: '💻',
      title: 'Node B',
      sub: '10.0.0.12',
      width: 210,
      pos: [0.22, 0.88],
      core: true,
      kind: 'host',
      colorMode: 'status',
      status: 'ok',
      online: true,
      pulse: true,
      descLines: ['embedding svc :8100', 'dense + sparse + late-interaction'],
      metrics: { summary: 'service ready', latency: 5.1, base: 'service ready' },
    },
  ]

  ns.forEach((n) => {
    if (n.kind === 'vps') n.lines = vpsLines(n.metrics)
    if (n.kind === 'host') n.lines = hostLines(n)
  })

  const es = [
    {
      from: 'user',
      to: 'mac',
      color: C.gray,
      label: 'interacts',
      speed: 0.25,
      count: 2,
      curve: 0,
      gate: null,
    },
    {
      from: 'mac',
      to: 'vps',
      color: C.blue,
      label: 'ssh + mosquitto_sub\nstate/* · monitor/* · llm/*',
      speed: 0.7,
      count: 6,
      curve: -1,
      gate: 'vps',
    },
    {
      from: 'vps',
      to: 'mac',
      color: C.green,
      label: 'snapshot + llm/call/v1\n(retained MQTT)',
      speed: 0.55,
      count: 5,
      curve: 1,
      gate: 'vps',
    },
    {
      from: 'mac',
      to: 'nodeA',
      color: C.orange,
      label: 'HTTP /metrics\n(metrics exporter)',
      speed: 0.4,
      count: 3,
      curve: 0,
      gate: 'nodeA',
    },
    {
      from: 'mac',
      to: 'nodeB',
      color: C.purple,
      label: 'HTTP /health\n(service API)',
      speed: 0.4,
      count: 3,
      curve: 0,
      gate: 'nodeB',
    },
  ]

  return { nodes: ns, edges: es }
}

export function makeDegraded() {
  const m = makeSample()

  const vps = m.nodes.find((n) => n.id === 'vps')
  vps.metrics = { active: 38, total: 44, incidents: 2, calls: 20, tokens: 240000 }
  vps.status = 'alert'
  vps.lines = vpsLines(vps.metrics)

  const a = m.nodes.find((n) => n.id === 'nodeA')
  a.status = 'degraded'
  a.metrics = { summary: 'degraded', latency: 41, base: 'degraded' }
  a.lines = hostLines(a)

  const b = m.nodes.find((n) => n.id === 'nodeB')
  b.status = 'down'
  b.online = false
  b.pulse = false
  b.metrics = { summary: 'unreachable', latency: null, base: 'unreachable' }
  b.lines = hostLines(b)

  return m
}

// ============================================================================
// Device Detection
// ============================================================================

export function getDeviceGlyph(hostname, isGateway, isSelf) {
  if (isGateway) return '🌐'
  if (isSelf) return '💻'

  const name = (hostname || '').toLowerCase()

  if (/router|gw|gateway|switch/.test(name)) return '🌐'
  if (/phone|iphone|android|galaxy|mobile/.test(name)) return '📱'
  if (/tv|cast|roku|appletv/.test(name)) return '📺'
  if (/print/.test(name)) return '🖨️'
  if (/nas|synology|server|srv|esxi|vmware/.test(name)) return '🗄️'

  return '🖥️'
}
