import React, {useState, useEffect, useRef} from 'react'
import Head from 'next/head'

// Ported config
const CITY_EDGES = [
  ['RAWALPINDI', 'ISLAMABAD', 13],
  ['ISLAMABAD', 'HARIPUR', 33],
  ['RAWALPINDI', 'JHELUM', 111],
  ['JHELUM', 'GUJRAT', 62],
  ['JHELUM', 'SARGODHA', 95],
  ['GUJRAT', 'GUJRANWALA', 49],
  ['GUJRAT', 'SARGODHA', 110],
  ['GUJRANWALA', 'SIALKOT', 50],
  ['GUJRANWALA', 'SHEIKHUPURA', 50],
  ['SHEIKHUPURA', 'LAHORE', 35],
  ['SHEIKHUPURA', 'FAISALABAD', 95],
  ['FAISALABAD', 'SARGODHA', 93],
  ['FAISALABAD', 'JHANG', 80],
  ['JHANG', 'SHORKOT', 50],
  ['FAISALABAD', 'TOBATEKSINGH', 50],
  ['TOBATEKSINGH', 'MULTAN', 130],
  ['LAHORE', 'OKARA', 129],
  ['OKARA', 'SAHIWAL', 40],
  ['SAHIWAL', 'KHANEWAL', 50],
  ['KHANEWAL', 'MULTAN', 50],
  ['SAHIWAL', 'MULTAN', 110],
  ['MULTAN', 'BAHAWALPUR', 95]
]

const CHARGING_STATIONS = [
  'JHELUM','GUJRAT','GUJRANWALA','SHEIKHUPURA','LAHORE','FAISALABAD',
  'SARGODHA','OKARA','SAHIWAL','TOBATEKSINGH','MULTAN'
]

const KWH_PER_KM = 0.2
const CHARGING_COST_PER_KWH = 30

const POSITIONS = {
  RAWALPINDI:    [0.5, 10],
  ISLAMABAD:     [0.8, 10.3],
  HARIPUR:       [0.3, 11],
  JHELUM:        [1.5, 8.8],
  GUJRAT:        [2.2, 8.2],
  SARGODHA:      [1.0, 7.0],
  GUJRANWALA:    [2.6, 7.2],
  SIALKOT:       [3.2, 7.8],
  SHEIKHUPURA:   [2.8, 6.2],
  LAHORE:        [3.4, 5.5],
  FAISALABAD:    [1.6, 5.5],
  JHANG:         [0.8, 5.8],
  SHORKOT:       [0.6, 4.8],
  TOBATEKSINGH:  [1.8, 4.5],
  OKARA:         [2.8, 4.0],
  SAHIWAL:       [2.2, 3.2],
  KHANEWAL:      [1.6, 2.4],
  MULTAN:        [1.0, 1.8],
  BAHAWALPUR:    [1.8, 0.8]
}

function buildGraph() {
  const g = {}
  CITY_EDGES.forEach(([u,v,w]) => {
    if (!g[u]) g[u] = {}
    if (!g[v]) g[v] = {}
    g[u][v] = w
    g[v][u] = w
  })
  return g
}

function dijkstra(graph, start, end) {
  const pq = [[0, start, [start]]]
  const visited = new Set()
  while (pq.length) {
    pq.sort((a,b)=>a[0]-b[0])
    const [cost,node,path] = pq.shift()
    if (visited.has(node)) continue
    visited.add(node)
    if (node === end) return [cost, path]
    const neighbors = graph[node] || {}
    for (const [n, w] of Object.entries(neighbors)) {
      if (!visited.has(n)) pq.push([cost + w, n, path.concat(n)])
    }
  }
  return [Infinity, []]
}

function evAwareRoute(graph, start, end, batteryCapacity) {
  const pq = [[0, batteryCapacity, start, [start]]]
  const visited = new Set()
  while (pq.length) {
    pq.sort((a,b)=>a[0]-b[0])
    const [cost, battery, node, path] = pq.shift()
    const state = node + '|' + battery
    if (visited.has(state)) continue
    visited.add(state)
    if (node === end) {
      const stops = path.filter(n => CHARGING_STATIONS.includes(n))
      return {distance_km: cost, path, final_battery_km: battery, charging_stops: stops, is_feasible:true}
    }
    const neighbors = graph[node] || {}
    for (const [n, w] of Object.entries(neighbors)) {
      const edge_dist = w
      if (edge_dist > battery) continue
      let new_battery = battery - edge_dist
      if (CHARGING_STATIONS.includes(n)) new_battery = batteryCapacity
      pq.push([cost + edge_dist, new_battery, n, path.concat(n)])
    }
  }
  return {distance_km: Infinity, path: [], is_feasible:false}
}

function estimateChargingCost(result, batteryCapacity) {
  let total = 0
  result.charging_stops.forEach(stop => {
    const energy = batteryCapacity * KWH_PER_KM
    total += energy * CHARGING_COST_PER_KWH
  })
  return total
}

export default function Home() {
  const graph = buildGraph()
  const cities = Object.keys(graph).sort()
  const [start, setStart] = useState('RAWALPINDI')
  const [end, setEnd] = useState('SAHIWAL')
  const [battery, setBattery] = useState(150)
  const [result, setResult] = useState(null)
  const [plain, setPlain] = useState(null)
  const [animStep, setAnimStep] = useState(0)
  const intervalRef = useRef(null)

  useEffect(()=>()=> clearInterval(intervalRef.current), [])

  function planRoute() {
    const plainRes = dijkstra(graph, start, end)
    setPlain(plainRes)
    const r = evAwareRoute(graph, start, end, Number(battery))
    if (!r.is_feasible) {
      setResult({error: 'No feasible path within battery range'})
      return
    }
    r.cost = estimateChargingCost(r, Number(battery))
    setResult(r)
    // animate
    setAnimStep(0)
    clearInterval(intervalRef.current)
    let step = 1
    intervalRef.current = setInterval(()=>{
      setAnimStep(s=> Math.min(s+1, r.path.length))
      step++
      if (step>r.path.length) clearInterval(intervalRef.current)
    }, 700)
  }

  function nodeColor(n, path) {
    if (path && path.slice(0, animStep).includes(n)) return '#FF4B4B'
    if (CHARGING_STATIONS.includes(n)) return '#00FF7F'
    return '#00D9FF'
  }

  return (
    <div>
      <Head>
        <title>EV Charging Station Planner</title>
      </Head>
      <div style={{display:'flex', gap:24, padding:24, background:'#07121A', minHeight:'100vh'}}>
        <aside style={{width:320, background:'#0F1720', padding:18, borderRadius:10}}>
          <h2 style={{marginTop:0,color:'#FAFAFA'}}>⚡ EV Charging Station Planner</h2>
          <div style={{color:'#9AA0AC'}}>Dijkstra · Battery-Aware Routing · Prim's MST</div>
          <hr style={{borderColor:'#2A2F3C'}} />
          <div style={{marginTop:12}}>
            <label style={{color:'#C7D2DA'}}>Start City</label>
            <select value={start} onChange={e=>setStart(e.target.value)} style={{width:'100%',padding:8,marginTop:6}}>
              {cities.map(c=> <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div style={{marginTop:12}}>
            <label style={{color:'#C7D2DA'}}>Destination City</label>
            <select value={end} onChange={e=>setEnd(e.target.value)} style={{width:'100%',padding:8,marginTop:6}}>
              {cities.map(c=> <option key={c} value={c}>{c}</option>)}
            </select>
          </div>
          <div style={{marginTop:12}}>
            <label style={{color:'#C7D2DA'}}>Battery Range (km)</label>
            <input type="range" min={50} max={600} value={battery} onChange={e=>setBattery(e.target.value)} style={{width:'100%'}} />
            <div style={{textAlign:'right', color:'#FAFAFA'}}>{battery} km</div>
          </div>
          <button onClick={planRoute} style={{marginTop:12, width:'100%', padding:12, background:'linear-gradient(90deg,#00D9FF,#00FF7F)', border:'none', fontWeight:700}}>Plan Route</button>
        </aside>

        <main style={{flex:1}}>
          <div style={{display:'flex', gap:12, marginBottom:12}}>
            <div style={{flex:1, background:'#0F1720', padding:12, borderRadius:8}}>
              <div style={{color:'#9AA0AC'}}>Total Distance</div>
              <div style={{fontSize:20, color:'#FAFAFA'}}>{result ? `${result.distance_km} km` : '—'}</div>
            </div>
            <div style={{flex:1, background:'#0F1720', padding:12, borderRadius:8}}>
              <div style={{color:'#9AA0AC'}}>Battery at Arrival</div>
              <div style={{fontSize:20, color:'#FAFAFA'}}>{result ? `${result.final_battery_km} km` : '—'}</div>
            </div>
            <div style={{flex:1, background:'#0F1720', padding:12, borderRadius:8}}>
              <div style={{color:'#9AA0AC'}}>Charging Stops</div>
              <div style={{fontSize:20, color:'#FAFAFA'}}>{result ? `${result.charging_stops.length}` : '—'}</div>
            </div>
            <div style={{flex:1, background:'#0F1720', padding:12, borderRadius:8}}>
              <div style={{color:'#9AA0AC'}}>Charging Cost</div>
              <div style={{fontSize:20, color:'#FAFAFA'}}>{result ? `Rs. ${result.cost}` : '—'}</div>
            </div>
          </div>

          <div style={{display:'flex', gap:18}}>
            <div style={{flex:1, background:'#07121A', padding:12, borderRadius:8}}>
              <h3 style={{color:'#FAFAFA'}}>🗺️ Route Map</h3>
              <svg viewBox="0 0 4 12" style={{width:'100%', height:600, background:'#0E1117', borderRadius:8}}>
                {Object.entries(POSITIONS).map(([name, [x,y]])=>{
                  const px = (x/4)*100
                  const py = (12 - y)/12*100
                  const path = result ? result.path : []
                  return (
                    <g key={name} transform={`translate(${px}%, ${py}%)`}>
                      <circle r={8} fill={nodeColor(name, path)} stroke="#08121A" cx={0} cy={0}></circle>
                      <text x={12} y={4} fontSize={8} fill="#FAFAFA" fontWeight="700">{name}</text>
                    </g>
                  )
                })}
                {/* edges */}
                {CITY_EDGES.map(([u,v,w], i)=>{
                  const [ux,uy] = POSITIONS[u]
                  const [vx,vy] = POSITIONS[v]
                  const x1 = (ux/4)*100
                  const y1 = (12 - uy)/12*100
                  const x2 = (vx/4)*100
                  const y2 = (12 - vy)/12*100
                  const isPath = result && result.path && ((result.path.includes(u) && result.path.includes(v)) && Math.abs(result.path.indexOf(u)-result.path.indexOf(v))===1)
                  return <line key={i} x1={`${x1}%`} y1={`${y1}%`} x2={`${x2}%`} y2={`${y2}%`} stroke={isPath ? '#FF4B4B' : '#333333'} strokeWidth={isPath?3:1} />
                })}
              </svg>
            </div>

            <div style={{width:360, background:'#07121A', padding:12, borderRadius:8}}>
              <h3 style={{color:'#FAFAFA'}}>📍 Route Details</h3>
              <div style={{color:'#9AA0AC'}}>EV-Aware Path</div>
              <div style={{background:'#0F1720', padding:8, borderRadius:6, marginTop:8}}>{result ? result.path.join(' -> ') : '—'}</div>
              <div style={{color:'#9AA0AC', marginTop:10}}>Normal Dijkstra Path</div>
              <div style={{background:'#0F1720', padding:8, borderRadius:6, marginTop:8}}>{plain ? plain[1].join(' -> ') : '—'}</div>
              {result && result.charging_stops.length>0 && (
                <div style={{marginTop:10}}><strong>Charging Stops:</strong> {result.charging_stops.join(', ')}</div>
              )}
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}
