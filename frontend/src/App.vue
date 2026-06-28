<template>
  <div id="stage" class="fixed inset-0 bg-topology-dark overflow-hidden">
    <!-- Starfield and grid backdrop -->
    <canvas id="space" class="absolute inset-0 w-full h-full pointer-events-none"></canvas>

    <!-- Edges canvas -->
    <canvas id="edges" class="absolute inset-0 w-full h-full" @click="handleCanvasClick"></canvas>

    <!-- Vignette overlay -->
    <div class="absolute inset-0 pointer-events-none" style="
        background: radial-gradient(130% 100% at 50% 42%, transparent 55%, rgba(2, 4, 9, 0.55) 100%);
        mix-blend-mode: multiply;
      "></div>

    <!-- HUD (Head-up Display) -->
    <div class="absolute top-4 left-4 right-4 flex justify-between items-start" style="z-index: 10">
      <!-- Title -->
      <div class="text-white">
        <h1 class="text-base font-semibold m-0">Live System Topology</h1>
        <p class="text-xs text-gray-400 m-0 mt-0.5">
          data-driven · nodes/edges · animated 60fps · live status colors
        </p>
      </div>

      <!-- Legend -->
      <div class="bg-black bg-opacity-50 border border-white border-opacity-15 rounded-lg p-2 text-xs">
        <div v-for="edge in uniqueEdges" :key="edge.from + '-' + edge.to"
          class="flex items-center gap-1 text-white text-opacity-80 mb-1">
          <div class="w-2 h-2 rounded-full"
            :style="{ backgroundColor: `rgb(${edge.color[0]}, ${edge.color[1]}, ${edge.color[2]})` }"></div>
          <span>{{ edge.from }} → {{ edge.to }}</span>
        </div>
      </div>
    </div>

    <!-- Nodes overlay -->
    <div id="nodes" class="absolute inset-0 pointer-events-none">
      <div v-for="node in nodes" :key="node.id" class="node" :data-id="node.id" :style="nodeStyle(node)"
        @pointerdown.stop.prevent="startDrag(node, $event)">
        <div class="flex items-center gap-2">
          <span class="text-xl leading-none">{{ node.glyph }}</span>
          <div class="min-w-0">
            <div class="text-xs font-semibold text-white truncate">{{ node.title }}</div>
            <div class="text-[10px] font-mono text-white text-opacity-60 truncate">{{ node.sub }}</div>
          </div>
        </div>
        <div v-if="node.lines && node.lines.length" class="mt-1 space-y-0.5">
          <div v-for="(ln, i) in node.lines" :key="i"
            class="text-[10px] text-white text-opacity-55 leading-tight truncate">
            {{ ln }}
          </div>
        </div>
      </div>
    </div>

    <!-- Control panel -->
    <div class="absolute bottom-4 left-4 flex gap-2 flex-wrap max-w-xs" style="z-index: 10">
      <button @click="loadDockerTopology()" :class="presetActive === 'docker' ? 'border-green-400 text-green-400' : ''"
        class="bg-black bg-opacity-55 text-white border border-white border-opacity-20 hover:border-opacity-45 rounded-lg px-3 py-1.5 text-xs cursor-pointer transition">
        🐳 Docker
      </button>
      <button @click="loadPreset('sample')" :class="presetActive === 'sample' ? 'border-green-400 text-green-400' : ''"
        class="bg-black bg-opacity-55 text-white border border-white border-opacity-20 hover:border-opacity-45 rounded-lg px-3 py-1.5 text-xs cursor-pointer transition">
        📊 Sample
      </button>
      <button @click="loadPreset('degraded')"
        :class="presetActive === 'degraded' ? 'border-green-400 text-green-400' : ''"
        class="bg-black bg-opacity-55 text-white border border-white border-opacity-20 hover:border-opacity-45 rounded-lg px-3 py-1.5 text-xs cursor-pointer transition">
        ⚠️ Degraded
      </button>
      <button @click="toggleLiveFeed" :class="liveActive ? 'border-green-400 text-green-400' : ''"
        class="bg-black bg-opacity-55 text-white border border-white border-opacity-20 hover:border-opacity-45 rounded-lg px-3 py-1.5 text-xs cursor-pointer transition">
        {{ liveActive ? '■ Live Feed' : '▶ Live Feed' }}
      </button>

      <div class="w-px bg-white bg-opacity-15 m-1"></div>

      <button @click="addNode"
        class="bg-black bg-opacity-55 text-white border border-white border-opacity-20 hover:border-opacity-45 rounded-lg px-3 py-1.5 text-xs cursor-pointer transition">
        ＋ Add Node
      </button>
      <button @click="removeNode"
        class="bg-black bg-opacity-55 text-white border border-white border-opacity-20 hover:border-opacity-45 rounded-lg px-3 py-1.5 text-xs cursor-pointer transition">
        － Remove Node
      </button>

      <div class="w-px bg-white bg-opacity-15 m-1"></div>

      <button @click="scanLAN()" :disabled="scanning"
        class="bg-black bg-opacity-55 text-white border border-white border-opacity-20 hover:border-opacity-45 rounded-lg px-3 py-1.5 text-xs cursor-pointer transition disabled:opacity-50">
        {{ scanning ? '⏳ Scanning...' : '🔍 Scan LAN' }}
      </button>
      <span class="text-xs text-white text-opacity-50 self-center">
        {{ nodes.length }} nodes · {{ edges.length }} edges
      </span>
    </div>

    <!-- Action panel (dynamically shown) -->
    <div v-if="selectedNode" :style="actionPanelStyle"
      class="absolute bg-opacity-97 bg-black border border-white border-opacity-20 rounded-lg p-3 min-w-60 z-50 pointer-events-auto"
      @click.stop>
      <div class="flex justify-between items-start mb-2">
        <div>
          <h3 class="text-sm font-semibold mb-1">{{ selectedNode.title }}</h3>
          <p class="text-xs text-white text-opacity-50 font-mono">
            {{ selectedNode.ip || 'demo node — no IP' }}
            <span v-if="selectedNode.mac"> · {{ selectedNode.mac }}</span>
          </p>
        </div>
        <button @click="selectedNode = null"
          class="text-white text-opacity-50 hover:text-opacity-100 text-lg leading-none">✕</button>
      </div>

      <input v-model="actionText" type="text" placeholder="Message text" :disabled="!selectedNode.ip"
        class="w-full bg-white bg-opacity-10 text-white border border-white border-opacity-20 rounded px-2 py-1.5 text-xs mb-2 disabled:opacity-50" />

      <div class="flex gap-2 mb-2">
        <button @click="executeAction('message')" :disabled="!selectedNode.ip"
          class="flex-1 bg-green-600 bg-opacity-20 text-green-400 hover:bg-opacity-30 border border-green-400 rounded px-2 py-1 text-xs font-semibold disabled:opacity-50">
          Send Message
        </button>
        <button @click="executeAction('ping')" :disabled="!selectedNode.ip"
          class="flex-1 bg-white bg-opacity-10 text-white hover:bg-opacity-20 border border-white border-opacity-25 rounded px-2 py-1 text-xs disabled:opacity-50">
          Ping
        </button>
      </div>

      <div v-if="actionResult" class="text-xs p-2 rounded bg-opacity-20" :style="actionResultStyle">
        {{ actionResult }}
      </div>
    </div>

    <!-- Info text -->
    <div class="absolute bottom-4 right-4 text-xs text-white text-opacity-40 max-w-xs text-right z-10">
      <p>🔍 Scan LAN → <b>Click node</b> for actions (message/ping) · Drag = move</p>
      <!-- <p>To see real messages, run <b>node agent.js</b> on target machine</p> -->
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import axios from 'axios'
import {
  makeSample,
  makeDegraded,
  autoPos,
  getDeviceGlyph,
  formatK,
  clamp,
  jitter,
  C,
  rgba,
  STATUS
} from './utils/topology'

// ============================================================================
// State
// ============================================================================

const nodes = ref([])
const edges = ref([])
const presetActive = ref('')
const liveActive = ref(false)
const scanning = ref(false)
const selectedNode = ref(null)
const actionText = ref('Hi')
const actionResult = ref('')
const actionResultStyle = ref({})
const liveTimer = ref(null)
const seq = ref(0)

// Canvas and rendering
let canvas = null
let ctx = null
let skyCanvas = null
let sctx = null
let W = 0
let H = 0
let DPR = 1
let stars = []
let drag = null
let animationId = null

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// ============================================================================
// Computed
// ============================================================================

const uniqueEdges = computed(() => {
  const seen = new Set()
  return edges.value.filter((e) => {
    const key = e.color.join(',')
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
})

const actionPanelStyle = computed(() => {
  if (!selectedNode.value) return {}
  const x = clamp(selectedNode.value.pos[0] * W + 18, 8, W - 260)
  const y = clamp(selectedNode.value.pos[1] * H - 30, 8, H - 210)
  return { left: x + 'px', top: y + 'px' }
})

// ============================================================================
// Methods - Canvas and Rendering
// ============================================================================

function seedStars() {
  stars = []
  const bands = [
    { count: 110, depth: 0.2, r: [0.4, 0.9], a: [0.15, 0.4] },
    { count: 60, depth: 0.55, r: [0.7, 1.5], a: [0.3, 0.6] },
    { count: 28, depth: 1, r: [1.2, 2.4], a: [0.5, 0.95] },
  ]
  for (const b of bands) {
    for (let i = 0; i < b.count; i++) {
      stars.push({
        x: Math.random(),
        y: Math.random(),
        depth: b.depth,
        r: b.r[0] + Math.random() * (b.r[1] - b.r[0]),
        a: b.a[0] + Math.random() * (b.a[1] - b.a[0]),
        tw: Math.random() * Math.PI * 2,
        hue: Math.random() < 0.2 ? 1 : 0,
      })
    }
  }
}

function drawSpace(t) {
  sctx.clearRect(0, 0, W, H)

  // Perspective grid
  const horizon = H * 0.46
  const vpx = W * 0.5
  sctx.lineWidth = 1

  // Converging verticals
  for (let i = -10; i <= 10; i++) {
    const a = 0.05 - Math.abs(i) * 0.003
    if (a <= 0) continue
    const fx = vpx + i * (W * 0.12)
    sctx.strokeStyle = `rgba(120,150,220,${a})`
    sctx.beginPath()
    sctx.moveTo(vpx, horizon)
    sctx.lineTo(fx, H)
    sctx.stroke()
  }

  // Receding horizontals
  for (let i = 1; i <= 14; i++) {
    const p = i / 14
    const y = horizon + Math.pow(p, 2.2) * (H - horizon)
    sctx.strokeStyle = `rgba(120,150,220,${0.07 * (1 - p)})`
    sctx.beginPath()
    sctx.moveTo(0, y)
    sctx.lineTo(W, y)
    sctx.stroke()
  }

  // Parallax starfield
  for (const s of stars) {
    const drift = t * 0.004 * s.depth
    const x = ((s.x - drift) % 1 + 1) % 1 * W
    const y = ((s.y - drift * 0.4) % 1 + 1) % 1 * H
    const tw = 0.7 + 0.3 * Math.sin(t * 1.5 * s.depth + s.tw)
    const a = s.a * tw
    const col = s.hue ? `255,210,170` : `190,210,255`

    if (s.depth >= 1) {
      sctx.fillStyle = `rgba(${col},${a * 0.25})`
      sctx.beginPath()
      sctx.arc(x, y, s.r * 2.6, 0, Math.PI * 2)
      sctx.fill()
    }

    sctx.fillStyle = `rgba(${col},${a})`
    sctx.beginPath()
    sctx.arc(x, y, s.r, 0, Math.PI * 2)
    sctx.fill()
  }
}

function bezier(t, p0, p1, p2) {
  const u = 1 - t
  return [
    u * u * p0[0] + 2 * u * t * p1[0] + t * t * p2[0],
    u * u * p0[1] + 2 * u * t * p1[1] + t * t * p2[1],
  ]
}

function px(id) {
  const node = nodes.value.find((n) => n.id === id)
  if (!node) return [0, 0]
  return [node.pos[0] * W, node.pos[1] * H]
}

// Resolve a node's [r,g,b] color from its colorMode (fixed color or live status)
function nodeColor(node) {
  if (node.colorMode === 'status') return STATUS[node.status] || STATUS.neutral
  return node.color || C.gray
}

// Absolute-position + style a node card so it sits exactly on its edge endpoint
function nodeStyle(node) {
  const c = nodeColor(node)
  const offline = node.online === false
  return {
    position: 'absolute',
    left: node.pos[0] * 100 + '%',
    top: node.pos[1] * 100 + '%',
    transform: 'translate(-50%, -50%)',
    width: (node.width || 180) + 'px',
    padding: '8px 10px',
    borderRadius: '12px',
    border: `1px solid ${rgba(c, offline ? 0.25 : 0.7)}`,
    background: `rgba(8, 12, 22, ${offline ? 0.55 : 0.8})`,
    boxShadow: node.pulse ? `0 0 18px ${rgba(c, 0.35)}` : 'none',
    opacity: offline ? 0.5 : 1,
    pointerEvents: 'auto',
    cursor: drag && drag.node === node && drag.moved ? 'grabbing' : 'grab',
    touchAction: 'none',
    userSelect: 'none',
    zIndex: node.core ? 6 : 5,
    backdropFilter: 'blur(2px)',
    transition: 'box-shadow .3s, border-color .3s, opacity .3s',
    boxSizing: 'border-box',
  }
}

// ============================================================================
// Methods - Drag & Move
// ============================================================================

function startDrag(node, e) {
  const stage = document.getElementById('stage')
  const rect = stage.getBoundingClientRect()
  drag = {
    node,
    rect,
    moved: false,
    startX: e.clientX,
    startY: e.clientY,
    // cursor position relative to node center, so the node doesn't jump on grab
    offsetX: e.clientX - (rect.left + node.pos[0] * rect.width),
    offsetY: e.clientY - (rect.top + node.pos[1] * rect.height),
  }
  window.addEventListener('pointermove', onDragMove)
  window.addEventListener('pointerup', endDrag)
}

function onDragMove(e) {
  if (!drag) return
  if (!drag.moved && Math.hypot(e.clientX - drag.startX, e.clientY - drag.startY) < 4) return
  drag.moved = true
  const { rect } = drag
  const x = (e.clientX - drag.offsetX - rect.left) / rect.width
  const y = (e.clientY - drag.offsetY - rect.top) / rect.height
  drag.node.pos = [clamp(x, 0.03, 0.97), clamp(y, 0.04, 0.96)]
}

function endDrag() {
  window.removeEventListener('pointermove', onDragMove)
  window.removeEventListener('pointerup', endDrag)
  if (!drag) return
  // A press without movement counts as a click → select the node
  if (!drag.moved) selectNode(drag.node)
  drag = null
}

function drawEdge(e, t) {
  if (!nodes.value.find((n) => n.id === e.from) || !nodes.value.find((n) => n.id === e.to)) return

  const from = px(e.from)
  const to = px(e.to)
  const dx = to[0] - from[0]
  const dy = to[1] - from[1]
  const dist = Math.hypot(dx, dy)
  if (dist < 1) return

  const pad = Math.min(80, dist * 0.35)
  const p1 = [from[0] + (dx * pad) / dist, from[1] + (dy * pad) / dist]
  const p2 = [to[0] - (dx * pad) / dist, to[1] - (dy * pad) / dist]
  const mid = [(p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2]
  const perp = [-dy / dist, dx / dist]
  const curveAmount = dist * 0.1 * e.curve
  const ctrl = [mid[0] + perp[0] * curveAmount, mid[1] + perp[1] * curveAmount]

  // Draw edge line
  ctx.beginPath()
  ctx.moveTo(p1[0], p1[1])
  ctx.quadraticCurveTo(ctrl[0], ctrl[1], p2[0], p2[1])
  ctx.strokeStyle = rgba(e.color, 0.18)
  ctx.lineWidth = 1.5
  ctx.stroke()

  // Draw arrow
  const ang = Math.atan2(p2[1] - ctrl[1], p2[0] - ctrl[0])
  const aSize = 9
  ctx.strokeStyle = rgba(e.color, 0.9)
  ctx.lineWidth = 2
  ctx.lineCap = 'round'
  ctx.beginPath()
  ctx.moveTo(p2[0], p2[1])
  ctx.lineTo(p2[0] - aSize * Math.cos(ang - Math.PI / 6), p2[1] - aSize * Math.sin(ang - Math.PI / 6))
  ctx.moveTo(p2[0], p2[1])
  ctx.lineTo(p2[0] - aSize * Math.cos(ang + Math.PI / 6), p2[1] - aSize * Math.sin(ang + Math.PI / 6))
  ctx.stroke()

  // Draw particles
  if (!e.gate || nodes.value.find((n) => n.id === e.gate)?.online) {
    for (let i = 0; i < e.count; i++) {
      const offset = i / e.count
      const phase = ((t * e.speed) + offset) % 1
      const p = bezier(phase, p1, ctrl, p2)
      const opacity = 0.4 + 0.5 * (1 - phase)
      const r = 4.5

      ctx.fillStyle = rgba(e.color, opacity * 0.18)
      ctx.beginPath()
      ctx.arc(p[0], p[1], r * 2, 0, Math.PI * 2)
      ctx.fill()

      ctx.fillStyle = rgba(e.color, opacity)
      ctx.beginPath()
      ctx.arc(p[0], p[1], r, 0, Math.PI * 2)
      ctx.fill()
    }
  }

  // Draw label
  const lp = bezier(0.5, p1, ctrl, p2)
  const lx = lp[0] + perp[0] * curveAmount * 0.6
  const ly = lp[1] + perp[1] * curveAmount * 0.6 - 10
  ctx.font = '500 9px ui-monospace, Consolas, monospace'
  ctx.textAlign = 'center'
  ctx.textBaseline = 'middle'
  ctx.fillStyle = rgba(e.color, 0.95)
  const lines = e.label.split('\n')
  lines.forEach((ln, k) => ctx.fillText(ln, lx, ly + (k - (lines.length - 1) / 2) * 11))
}

function frame(now) {
  const t = now / 1000
  drawSpace(t)
  ctx.clearRect(0, 0, W, H)
  for (const e of edges.value) {
    drawEdge(e, t)
  }
  animationId = requestAnimationFrame(frame)
}

function resize() {
  DPR = window.devicePixelRatio || 1
  W = canvas.clientWidth
  H = canvas.clientHeight
  canvas.width = W * DPR
  canvas.height = H * DPR
  ctx.setTransform(DPR, 0, 0, DPR, 0, 0)
  skyCanvas.width = W * DPR
  skyCanvas.height = H * DPR
  sctx.setTransform(DPR, 0, 0, DPR, 0, 0)
}

// ============================================================================
// Methods - Node Management
// ============================================================================

function addNode() {
  seq.value++
  const PALETTE = [C.teal, C.pink, C.lime, C.orange, C.purple, C.blue]
  const color = PALETTE[(seq.value - 1) % PALETTE.length]
  const id = 'svc' + seq.value

  nodes.value.push({
    id,
    glyph: '⚙️',
    title: 'Service ' + seq.value,
    sub: '10.0.0.' + (20 + seq.value),
    width: 185,
    core: false,
    kind: 'host',
    colorMode: 'status',
    status: 'ok',
    online: true,
    pulse: true,
    pos: [0.5, 0.5],
    descLines: ['worker node', 'queue consumer'],
    metrics: { summary: 'ready', latency: 6 + Math.random() * 8, base: 'ready' },
    accent: color,
    lines: [`${(6 + Math.random() * 8).toFixed(1)}ms latency`, 'worker node', 'ready'],
  })

  edges.value.push({
    from: nodes.value[0].id,
    to: id,
    color,
    label: `HTTP /task\n(worker ${seq.value})`,
    speed: 0.45,
    count: 3,
    curve: (seq.value % 2 ? 1 : -1) * 0.1,
    gate: id,
  })
}

function removeNode() {
  const dyn = nodes.value.filter((n) => !n.core)
  if (!dyn.length) return
  const victim = dyn[dyn.length - 1]
  nodes.value = nodes.value.filter((n) => n !== victim)
  edges.value = edges.value.filter((e) => e.from !== victim.id && e.to !== victim.id)
}

function relayoutDynamic() {
  const dyn = nodes.value.filter((n) => !n.core && !n.moved)
  dyn.forEach((n, i) => {
    n.pos = autoPos(i, dyn.length, nodes.value)
  })
}

// ============================================================================
// Methods - Preset Loading
// ============================================================================

function loadPreset(preset) {
  liveActive.value = false
  if (liveTimer.value) clearInterval(liveTimer.value)

  seq.value = 0
  if (preset === 'degraded') {
    const m = makeDegraded()
    nodes.value = m.nodes
    edges.value = m.edges
  } else {
    const m = makeSample()
    nodes.value = m.nodes
    edges.value = m.edges
  }

  presetActive.value = preset
}

// ============================================================================
// Methods - Live Feed
// ============================================================================

function toggleLiveFeed() {
  if (liveActive.value) {
    if (liveTimer.value) clearInterval(liveTimer.value)
    liveActive.value = false
  } else {
    liveActive.value = true
    liveTimer.value = setInterval(simulateTick, 1200)
  }
}

function simulateTick() {
  for (const n of nodes.value) {
    if (n.kind === 'vps') {
      const m = n.metrics
      if (Math.random() < 0.7) m.calls += Math.floor(Math.random() * 3)
      m.tokens += Math.floor(Math.random() * 12000)
      m.active = clamp(Math.round(jitter(m.total - 1, 2)), 36, m.total)
      if (Math.random() < 0.06) m.incidents = m.incidents > 0 ? 0 : 1
      n.status = m.incidents > 0 ? 'alert' : m.active < m.total ? 'warn' : 'ok'
    } else if (n.kind === 'host') {
      const m = n.metrics
      if (Math.random() < 0.04) n.online = !n.online
      if (!n.online) {
        n.status = 'down'
        n.pulse = false
        m.summary = 'unreachable'
        m.latency = null
      } else {
        m.latency = clamp(jitter(m.latency ?? 6, 4), 1, 80)
        n.status = m.latency > 35 ? 'degraded' : 'ok'
        n.pulse = true
        m.summary = n.status === 'degraded' ? 'degraded' : m.base
      }
    }
  }
}

// ============================================================================
// Methods - Network Scanning
// ============================================================================

async function scanLAN(silent = false) {
  scanning.value = true
  try {
    const response = await axios.get(`${API_BASE}/api/hosts`)
    const data = response.data

    seq.value = 0
    nodes.value = []
    edges.value = []

    const hubHost = data.hosts?.find((h) => h.isGateway) || data.hosts?.find((h) => h.isSelf) || data.hosts?.[0]
    const ring = data.hosts?.filter((h) => h !== hubHost) || []

    if (hubHost) {
      nodes.value.push({
        id: 'self',
        glyph: hubHost.isGateway ? '🌐' : '💻',
        core: true,
        colorMode: 'fixed',
        color: hubHost.isGateway ? C.blue : C.green,
        online: true,
        pulse: true,
        title: hubHost.isGateway ? 'Gateway' : 'This PC',
        sub: hubHost.ip,
        width: 200,
        pos: [0.5, 0.52],
        ip: hubHost.ip,
        mac: hubHost.mac || '',
        lines: [hubHost.name || '—', hubHost.mac || '', data.subnet || ''].filter(Boolean),
      })
    }

    ring.forEach((h, i) => {
      const a = (-Math.PI / 2 + (2 * Math.PI * i) / Math.max(ring.length, 1)) % (2 * Math.PI)
      const pos = [
        clamp(0.5 + Math.cos(a) * 0.36, 0.05, 0.95),
        clamp(0.52 + Math.sin(a) * 0.4, 0.08, 0.93),
      ]
      const id = 'ip-' + h.ip

      nodes.value.push({
        id,
        glyph: h.glyph || '🖥️',
        core: false,
        moved: true,
        colorMode: 'fixed',
        color: h.isSelf ? C.green : C.teal,
        online: true,
        pulse: h.isSelf,
        title: h.name ? h.name.split('.')[0] : h.ip,
        sub: h.ip,
        width: 180,
        pos,
        ip: h.ip,
        mac: h.mac || '',
        lines: [h.mac || 'no ARP', h.name || (h.isSelf ? 'this machine' : 'online')].filter(Boolean),
      })

      edges.value.push({
        from: 'self',
        to: id,
        color: h.isSelf ? C.green : C.teal,
        label: h.ip.split('.').slice(-1)[0],
        speed: 0.35,
        count: 2,
        curve: 0,
        gate: id,
      })
    })

    presetActive.value = ''
  } catch (error) {
    if (!silent) alert('Failed to scan LAN: ' + error.message + '\n\nMake sure the backend is running: docker-compose up')
    console.error(error)
  } finally {
    scanning.value = false
  }
}

// ============================================================================
// Methods - Docker Topology (Machine -> Container -> Image)
// ============================================================================

// Spread N nodes vertically within a fixed-x column (one tier of the graph)
function tierPos(x, i, n) {
  if (n <= 1) return [x, 0.5]
  const top = 0.1, bottom = 0.92
  return [x, top + (bottom - top) * (i / (n - 1))]
}

// Map a Docker container state to one of the live status colors
function containerStatus(state) {
  if (state === 'running') return 'ok'
  if (state === 'paused') return 'warn'
  if (state === 'restarting') return 'degraded'
  return 'down' // exited / created / dead
}

// Human-readable byte size
function fmtBytes(b) {
  if (!b) return ''
  const u = ['B', 'KB', 'MB', 'GB', 'TB']
  let i = 0, n = b
  while (n >= 1024 && i < u.length - 1) { n /= 1024; i++ }
  return (i === 0 ? n : n.toFixed(n >= 10 ? 0 : 1)) + ' ' + u[i]
}

async function loadDockerTopology(silent = false) {
  scanning.value = true
  try {
    const { data } = await axios.get(`${API_BASE}/api/topology`)

    seq.value = 0
    nodes.value = []
    edges.value = []

    // Tier 1 — Machine (host)
    const m = data.machine || {}
    nodes.value.push({
      id: 'machine',
      glyph: '🖥️',
      title: m.name || 'Docker Host',
      sub: 'machine',
      width: 220,
      pos: [0.13, 0.5],
      core: true,
      colorMode: 'fixed',
      color: C.blue,
      online: true,
      pulse: true,
      lines: [
        m.os || 'docker host',
        `${m.containers ?? 0} containers · ${m.images ?? 0} images`,
        m.ncpu ? `${m.ncpu} CPU · ${fmtBytes(m.mem)} RAM` : '',
      ].filter(Boolean),
    })

    // Tier 2 — Containers
    const cs = data.containers || []
    cs.forEach((c, i) => {
      const running = c.status === 'running'
      nodes.value.push({
        id: c.id,
        glyph: '📦',
        title: c.name,
        sub: 'container',
        width: 200,
        pos: tierPos(0.5, i, cs.length),
        core: false,
        colorMode: 'status',
        status: containerStatus(c.status),
        online: running,
        pulse: running,
        lines: [c.image, c.status, c.ports].filter(Boolean),
      })
    })

    // Tier 3 — Images
    const imgs = data.images || []
    imgs.forEach((img, i) => {
      const short = img.name && img.name.includes('/') ? img.name.split('/').pop() : img.name
      nodes.value.push({
        id: img.id,
        glyph: '💿',
        title: short || 'image',
        sub: 'image',
        width: 190,
        pos: tierPos(0.87, i, imgs.length),
        core: false,
        colorMode: 'fixed',
        color: C.purple,
        online: true,
        pulse: false,
        lines: [img.name, fmtBytes(img.size)].filter(Boolean),
      })
    })

      // Edges — machine→container (runs) and container→image (image)
      ; (data.edges || []).forEach((e) => {
        const isImg = e.kind === 'image'
        edges.value.push({
          from: e.from,
          to: e.to,
          color: isImg ? C.teal : C.blue,
          label: e.kind,
          speed: isImg ? 0.3 : 0.45,
          count: 2,
          curve: isImg ? 0.5 : 0,
          gate: isImg ? e.from : e.to,
        })
      })

    presetActive.value = 'docker'
  } catch (error) {
    if (!silent) alert('Failed to load Docker topology: ' + error.message + '\n\nMake sure the backend can reach the Docker socket.')
    console.error(error)
  } finally {
    scanning.value = false
  }
}

// ============================================================================
// Methods - Actions
// ============================================================================

function handleCanvasClick(e) {
  // Don't select if clicking on nodes
  if (e.target.closest('#nodes')) return
  selectedNode.value = null
}

function selectNode(node) {
  selectedNode.value = node
  actionText.value = 'Hi'
  actionResult.value = ''
}

async function executeAction(type) {
  if (!selectedNode.value) return

  actionResult.value = `... sending ${type}`
  actionResultStyle.value = { color: 'rgba(255,255,255,.6)' }

  try {
    const response = await axios.post(`${API_BASE}/api/action`, {
      ip: selectedNode.value.ip,
      mac: selectedNode.value.mac,
      type,
      text: actionText.value,
      via: 'agent',
    })

    if (response.data.ok) {
      actionResult.value = `✓ ${type} sent successfully`
      actionResultStyle.value = { color: 'rgb(89,242,140)' }
    } else {
      actionResult.value = '✗ ' + (response.data.error || 'Failed')
      actionResultStyle.value = { color: 'rgb(255,120,120)' }
    }
  } catch (error) {
    actionResult.value = '✗ ' + error.message + ' — Is the backend running?'
    actionResultStyle.value = { color: 'rgb(255,120,120)' }
  }
}

// ============================================================================
// Lifecycle
// ============================================================================

onMounted(() => {
  canvas = document.getElementById('edges')
  ctx = canvas.getContext('2d')
  skyCanvas = document.getElementById('space')
  sctx = skyCanvas.getContext('2d')

  seedStars()
  resize()
  loadDockerTopology(true)

  window.addEventListener('resize', resize)
  animationId = requestAnimationFrame(frame)
})

onUnmounted(() => {
  window.removeEventListener('resize', resize)
  if (animationId) cancelAnimationFrame(animationId)
  if (liveTimer.value) clearInterval(liveTimer.value)
})
</script>
