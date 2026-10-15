import React, { useEffect, useState, useMemo } from 'react';
import axios from 'axios';
import { 
  Navigation, Activity, 
  AlertTriangle, CheckCircle2, XCircle, RotateCcw, 
  UserPlus, MapPin, Search
} from 'lucide-react';

// Tactical Emergency Presets for 1-Click Operations Testing (Clean Aerospace / EMS Call-Codes)
const EMERGENCY_PRESETS = [
  {
    code: "POL-01",
    label: "Highway Polytrauma",
    type: "SEVERE_TRAUMA",
    severity: "CRITICAL",
    spo2: 85,
    hr: 122,
    consciousness: "UNRESPONSIVE",
    location: "PEELAMEDU"
  },
  {
    code: "CRD-02",
    label: "STEMI / Cardiac",
    type: "CARDIAC_ARREST",
    severity: "CRITICAL",
    spo2: 88,
    hr: 142,
    consciousness: "ALTERED",
    location: "RS_PURAM"
  },
  {
    code: "STR-03",
    label: "Stroke Golden Hour",
    type: "STROKE",
    severity: "CRITICAL",
    spo2: 94,
    hr: 88,
    consciousness: "ALTERED",
    location: "GANDHIPURAM"
  },
  {
    code: "BRN-04",
    label: "Severe Burn Crisis",
    type: "BURN",
    severity: "CRITICAL",
    spo2: 93,
    hr: 114,
    consciousness: "ALERT",
    location: "SAIBABA_COLONY"
  },
  {
    code: "ORT-05",
    label: "Compound Fracture",
    type: "FRACTURE",
    severity: "HIGH",
    spo2: 98,
    hr: 90,
    consciousness: "ALERT",
    location: "SUNDARAPURAM"
  },
  {
    code: "URO-06",
    label: "Renal / Urology",
    type: "UROLOGY_EMERGENCY",
    severity: "HIGH",
    spo2: 98,
    hr: 82,
    consciousness: "ALERT",
    location: "PEELAMEDU"
  },
  {
    code: "OPH-07",
    label: "Ocular Trauma",
    type: "EYE_TRAUMA",
    severity: "HIGH",
    spo2: 99,
    hr: 76,
    consciousness: "ALERT",
    location: "GANDHIPURAM"
  }
];

export default function App() {
  const [state, setState] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isUpdating, setIsUpdating] = useState<boolean>(false);
  const [showPatientForm, setShowPatientForm] = useState<boolean>(false);
  
  // Tactical Filters & Search States
  const [hospitalSearch, setHospitalSearch] = useState<string>('');
  const [hospitalTab, setHospitalTab] = useState<'all' | 'feasible' | 'rejected'>('all');
  const [selectedHospitalMap, setSelectedHospitalMap] = useState<any>(null);
  const [currentTime, setCurrentTime] = useState<string>('');

  // New Patient Form State
  const [patientData, setPatientData] = useState({
    emergency_type: 'SEVERE_TRAUMA',
    severity: 'CRITICAL',
    spo2: 88,
    pickup_location: 'GANDHIPURAM',
    heart_rate: 85,
    consciousness: 'ALERT'
  });

  // Digital Live Clock
  useEffect(() => {
    const updateClock = () => {
      const now = new Date();
      setCurrentTime(now.toLocaleTimeString('en-US', { hour12: false }) + ' IST');
    };
    updateClock();
    const interval = setInterval(updateClock, 1000);
    return () => clearInterval(interval);
  }, []);

  const fetchState = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/state');
      setState(res.data);
    } catch (err) {
      console.error('Failed to fetch emergency state:', err);
    } finally {
      setLoading(false);
      setIsUpdating(false);
    }
  };

  useEffect(() => {
    fetchState();
  }, []);

  const triggerEvent = async (eventType: string) => {
    setIsUpdating(true);
    try {
      await axios.post('http://localhost:8000/api/trigger_event', { event_type: eventType });
      setTimeout(fetchState, 500);
    } catch (err) {
      console.error(err);
      setIsUpdating(false);
    }
  };

  const dispatchPreset = async (preset: typeof EMERGENCY_PRESETS[0]) => {
    setIsUpdating(true);
    const payload = {
      emergency_type: preset.type,
      severity: preset.severity,
      spo2: preset.spo2,
      pickup_location: preset.location,
      heart_rate: preset.hr,
      consciousness: preset.consciousness
    };
    try {
      await axios.post('http://localhost:8000/api/new_patient', payload);
      setTimeout(fetchState, 500);
    } catch (err) {
      console.error(err);
      setIsUpdating(false);
    }
  };

  const submitNewPatient = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsUpdating(true);
    setShowPatientForm(false);
    try {
      await axios.post('http://localhost:8000/api/new_patient', patientData);
      setTimeout(fetchState, 500);
    } catch (err) {
      console.error(err);
      setIsUpdating(false);
    }
  };

  // Filtered Hospital List for Hospital Capability Agent
  const filteredHospitals = useMemo(() => {
    if (!state?.agent2_hospital?.all_evaluations) return [];
    let list = state.agent2_hospital.all_evaluations;

    if (hospitalTab === 'feasible') {
      list = list.filter((h: any) => h.feasible);
    } else if (hospitalTab === 'rejected') {
      list = list.filter((h: any) => !h.feasible);
    }

    if (hospitalSearch.trim()) {
      const query = hospitalSearch.toLowerCase();
      list = list.filter((h: any) => 
        h.name.toLowerCase().includes(query) ||
        (h.specialists && h.specialists.some((s: string) => s.toLowerCase().includes(query)))
      );
    }
    return list;
  }, [state, hospitalTab, hospitalSearch]);

  // Coordinate Projection for Tactical Interactive Radar Map
  // Coimbatore Lat: 10.95 to 11.15, Lon: 76.92 to 77.06
  const mapWidth = 600;
  const mapHeight = 320;
  const mapPadding = 35;
  const minLat = 10.95;
  const maxLat = 11.15;
  const minLon = 76.92;
  const maxLon = 77.06;

  const projectCoords = (lat: number, lon: number) => {
    const x = mapPadding + ((lon - minLon) / (maxLon - minLon)) * (mapWidth - 2 * mapPadding);
    const y = mapHeight - (mapPadding + ((lat - minLat) / (maxLat - minLat)) * (mapHeight - 2 * mapPadding));
    return { x: Math.max(15, Math.min(mapWidth - 15, x)), y: Math.max(15, Math.min(mapHeight - 15, y)) };
  };

  if (loading || !state) {
    return (
      <div className="min-h-screen bg-[#060b13] flex flex-col items-center justify-center text-cyan-400 font-mono">
        <div className="relative mb-6">
          <div className="w-20 h-20 rounded-full border-2 border-cyan-500/30 animate-ping absolute inset-0"></div>
          <div className="w-20 h-20 rounded-full border border-cyan-500 flex items-center justify-center bg-cyan-950/40">
            <Activity className="w-10 h-10 animate-pulse text-cyan-400" />
          </div>
        </div>
        <div className="text-xl font-black tracking-widest uppercase">INTIME DISPATCH CAD CONNECTING...</div>
        <p className="text-xs text-slate-500 mt-2 font-mono">Synchronizing Multi-Agent Telemetry Stream</p>
      </div>
    );
  }

  const patientCoords = projectCoords(state.patient.latitude, state.patient.longitude);
  const assignedHospitalObj = state.agent2_hospital.all_evaluations.find(
    (h: any) => h.hospital_id === state.agent4_coordination.assigned_hospital
  );
  const assignedCoords = assignedHospitalObj ? projectCoords(assignedHospitalObj.latitude, assignedHospitalObj.longitude) : null;

  return (
    <div className="min-h-screen bg-[#060b13] text-slate-300 font-sans p-4 lg:p-6 bg-radar-grid relative selection:bg-cyan-500/30">
      
      {/* =========================================================================
          COMMAND CENTER TOP HUD HEADER
         ========================================================================= */}
      <header className="mb-6 bg-slate-900/90 border border-slate-800/80 rounded-2xl p-4 lg:p-5 backdrop-blur-xl shadow-[0_4px_30px_rgba(0,0,0,0.5)]">
        <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-4">
          
          {/* Logo & Operational Status */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="p-3 bg-slate-950 border border-cyan-500/40 rounded-xl shadow-lg shadow-cyan-500/10">
                <Activity className="w-7 h-7 text-cyan-400" />
              </div>
              <span className="absolute -top-1 -right-1 flex h-3.5 w-3.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-emerald-500 border-2 border-slate-900"></span>
              </span>
            </div>

            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-black tracking-tight text-white flex items-center gap-2">
                  InTime <span className="text-cyan-400 font-mono text-xs px-2 py-0.5 rounded bg-cyan-950/80 border border-cyan-800">CAD DISPATCH v2.4</span>
                </h1>
                <span className="hidden sm:inline-flex items-center gap-1.5 text-[11px] font-mono uppercase bg-emerald-950/60 border border-emerald-500/40 text-emerald-400 px-2.5 py-0.5 rounded-full font-semibold">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  Telemetry Stream Active
                </span>
              </div>
              <p className="text-xs text-slate-400 uppercase tracking-widest font-semibold flex items-center gap-2 mt-0.5">
                <span>Emergency Ambulance Command & Care Coordination</span>
                <span className="text-slate-600">•</span>
                <span className="text-cyan-400/90 font-mono">{currentTime}</span>
              </p>
            </div>
          </div>

          {/* Tactical Command Control Actions */}
          <div className="flex flex-wrap items-center gap-2.5">
            <button
              onClick={() => setShowPatientForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-mono font-bold text-xs uppercase tracking-wider transition-all shadow-lg shadow-blue-600/20 active:scale-95"
            >
              <UserPlus className="w-4 h-4" /> Manual Dispatch
            </button>

            <button
              onClick={() => triggerEvent('HOSPITAL_FULL')}
              className="flex items-center gap-2 px-3.5 py-2 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 rounded-lg border border-amber-500/30 font-mono font-bold text-xs uppercase tracking-wider transition-all active:scale-95"
              title="Simulates ICU overflow on the currently selected hospital to test replanning"
            >
              <AlertTriangle className="w-4 h-4 text-amber-400" /> Simulate ICU Full
            </button>

            <button
              onClick={() => triggerEvent('ROAD_CLOSED')}
              className="flex items-center gap-2 px-3.5 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg border border-red-500/30 font-mono font-bold text-xs uppercase tracking-wider transition-all active:scale-95"
              title="Simulates an accident or route block along the primary transit corridor"
            >
              <AlertTriangle className="w-4 h-4 text-red-400" /> Simulate Road Block
            </button>

            <button
              onClick={() => triggerEvent('RESET')}
              className="flex items-center gap-2 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg border border-slate-700 font-mono font-bold text-xs uppercase tracking-wider transition-all active:scale-95"
            >
              <RotateCcw className="w-4 h-4" /> Reset Mission
            </button>
          </div>
        </div>

        {/* Tactical Scenario Quick Injector */}
        <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          <span className="text-[10px] uppercase font-mono font-bold text-slate-500 tracking-wider shrink-0">
            Presets:
          </span>
          <div className="flex gap-2 shrink-0">
            {EMERGENCY_PRESETS.map((p, idx) => (
              <button
                key={idx}
                onClick={() => dispatchPreset(p)}
                className="px-3 py-1.5 rounded-lg border border-slate-800 bg-[#050913] hover:bg-slate-800/90 hover:border-slate-700 text-slate-300 hover:text-white transition-all font-mono text-xs flex items-center gap-2 shadow-sm active:scale-95"
              >
                <span className="text-[10px] text-cyan-400 font-bold tracking-wider">{p.code}</span>
                <span>{p.label}</span>
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* =========================================================================
          LIVE DISRUPTION / SYSTEM EVENT ALERTS
         ========================================================================= */}
      {state.events && state.events.length > 0 && (
        <div className="mb-6 p-4 bg-red-950/30 border border-red-500/40 rounded-xl flex items-start gap-3 backdrop-blur-md animate-in fade-in">
          <div className="p-2 bg-red-500/20 rounded-lg text-red-400 shrink-0">
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <div className="text-xs font-mono uppercase font-bold text-red-400 tracking-wider mb-1 flex items-center justify-between">
              <span>Field Disruption Detected (Re-Routing Engine Engaged)</span>
              <span className="text-red-500 font-bold">{state.events.length} Active Events</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-1.5">
              {state.events.map((e: any, idx: number) => (
                <div key={idx} className="text-xs text-red-200/90 bg-red-950/40 border border-red-900/50 p-2 rounded flex items-center gap-2 font-mono">
                  <span className="w-1.5 h-1.5 rounded-full bg-red-400 shrink-0"></span>
                  <span className="text-red-400 font-bold">[{e.time}]</span>
                  <span className="truncate">{e.desc}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* =========================================================================
          TACTICAL REGIONAL RADAR & TELEMETRY SECTION
         ========================================================================= */}
      <section className="mb-6 grid grid-cols-1 xl:grid-cols-12 gap-6">
        
        {/* Radar Map Visualizer (7 Cols) */}
        <div className="xl:col-span-7 bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-col justify-between shadow-xl relative overflow-hidden backdrop-blur-md">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-slate-200">
                Coimbatore Regional CAD Dispatch Radar
              </h3>
            </div>
            <div className="flex items-center gap-3 text-[11px] font-mono">
              <span className="flex items-center gap-1.5 text-red-400">
                <span className="w-2 h-2 rounded-full bg-red-500 animate-ping"></span> Patient
              </span>
              <span className="flex items-center gap-1.5 text-emerald-400">
                <span className="w-2 h-2 rounded-full bg-emerald-400"></span> Destination
              </span>
              <span className="flex items-center gap-1.5 text-cyan-400">
                <span className="w-2 h-2 rounded-full bg-cyan-400"></span> Feasible
              </span>
            </div>
          </div>

          {/* Interactive SVG Radar Container */}
          <div className="w-full bg-[#050913] border border-cyan-950/60 rounded-xl relative overflow-hidden flex items-center justify-center p-2 min-h-[300px]">
            <svg 
              viewBox={`0 0 ${mapWidth} ${mapHeight}`} 
              className="w-full h-auto select-none"
            >
              <defs>
                <filter id="glowEffect" x="-20%" y="-20%" width="140%" height="140%">
                  <feGaussianBlur stdDeviation="3" result="blur" />
                  <feMerge>
                    <feMergeNode in="blur" />
                    <feMergeNode in="SourceGraphic" />
                  </feMerge>
                </filter>
              </defs>

              {/* Range Rings */}
              <circle cx={patientCoords.x} cy={patientCoords.y} r="45" fill="none" stroke="#0891b2" strokeWidth="1" strokeDasharray="3 3" opacity="0.25" />
              <circle cx={patientCoords.x} cy={patientCoords.y} r="95" fill="none" stroke="#0891b2" strokeWidth="1" strokeDasharray="3 3" opacity="0.2" />
              <circle cx={patientCoords.x} cy={patientCoords.y} r="150" fill="none" stroke="#0891b2" strokeWidth="1" strokeDasharray="3 3" opacity="0.15" />
              
              {/* Coordinate Crosshairs */}
              <line x1={patientCoords.x} y1="0" x2={patientCoords.x} y2={mapHeight} stroke="#0e7490" strokeWidth="0.8" strokeDasharray="4 4" opacity="0.2" />
              <line x1="0" y1={patientCoords.y} x2={mapWidth} y2={patientCoords.y} stroke="#0e7490" strokeWidth="0.8" strokeDasharray="4 4" opacity="0.2" />

              {/* Active Route Vector Line connecting Patient -> Assigned Hospital */}
              {assignedCoords && (
                <g>
                  <line 
                    x1={patientCoords.x} 
                    y1={patientCoords.y} 
                    x2={assignedCoords.x} 
                    y2={assignedCoords.y} 
                    stroke="#10b981" 
                    strokeWidth="2.5" 
                    strokeDasharray="6 4" 
                    className="animate-pulse"
                    filter="url(#glowEffect)"
                  />
                  {/* Midpoint Distance Badge */}
                  <rect 
                    x={(patientCoords.x + assignedCoords.x) / 2 - 25} 
                    y={(patientCoords.y + assignedCoords.y) / 2 - 10} 
                    width="50" 
                    height="18" 
                    rx="4" 
                    fill="#064e3b" 
                    stroke="#10b981" 
                    strokeWidth="1"
                  />
                  <text 
                    x={(patientCoords.x + assignedCoords.x) / 2} 
                    y={(patientCoords.y + assignedCoords.y) / 2 + 3} 
                    fill="#6ee7b7" 
                    fontSize="9" 
                    fontFamily="monospace" 
                    fontWeight="bold" 
                    textAnchor="middle"
                  >
                    {state.agent4_coordination.distance_km}km
                  </text>
                </g>
              )}

              {/* All Hospital Pins */}
              {state.agent2_hospital.all_evaluations.map((h: any, idx: number) => {
                const pt = projectCoords(h.latitude, h.longitude);
                const isAssigned = h.hospital_id === state.agent4_coordination.assigned_hospital;
                const isFeasible = h.feasible;

                if (isAssigned) {
                  return (
                    <g key={idx} className="cursor-pointer" onClick={() => setSelectedHospitalMap(h)}>
                      <circle cx={pt.x} cy={pt.y} r="14" fill="#10b981" opacity="0.2" className="animate-ping" />
                      <circle cx={pt.x} cy={pt.y} r="7" fill="#10b981" stroke="#ffffff" strokeWidth="2" filter="url(#glowEffect)" />
                      <rect x={pt.x - 45} y={pt.y - 25} width="90" height="15" rx="3" fill="#022c22" stroke="#10b981" strokeWidth="1" />
                      <text x={pt.x} y={pt.y - 14} fill="#a7f3d0" fontSize="8" fontFamily="monospace" fontWeight="bold" textAnchor="middle">
                        DEST: {h.name.substring(0, 14)}..
                      </text>
                    </g>
                  );
                }

                if (isFeasible) {
                  return (
                    <g key={idx} className="cursor-pointer" onClick={() => setSelectedHospitalMap(h)}>
                      <circle cx={pt.x} cy={pt.y} r="3.5" fill="#06b6d4" stroke="#083344" strokeWidth="1" className="hover:scale-150 transition-transform" />
                      <title>{h.name} (Feasible)</title>
                    </g>
                  );
                }

                return (
                  <circle 
                    key={idx} 
                    cx={pt.x} 
                    cy={pt.y} 
                    r="2" 
                    fill="#475569" 
                    opacity="0.35" 
                    className="hover:opacity-100 cursor-pointer"
                    onClick={() => setSelectedHospitalMap(h)}
                  >
                    <title>{h.name} (Rejected)</title>
                  </circle>
                );
              })}

              {/* Patient Pickup Beacon Marker */}
              <g>
                <circle cx={patientCoords.x} cy={patientCoords.y} r="16" fill="#ef4444" opacity="0.25" className="animate-ping" />
                <circle cx={patientCoords.x} cy={patientCoords.y} r="7" fill="#ef4444" stroke="#ffffff" strokeWidth="2" filter="url(#glowEffect)" />
                <rect x={patientCoords.x - 45} y={patientCoords.y + 12} width="90" height="16" rx="3" fill="#450a0a" stroke="#ef4444" strokeWidth="1" />
                <text x={patientCoords.x} y={patientCoords.y + 24} fill="#fca5a5" fontSize="8" fontFamily="monospace" fontWeight="bold" textAnchor="middle">
                  ORIGIN: {state.patient.pickup_name.substring(0, 11)}..
                </text>
              </g>
            </svg>
          </div>

          {/* Selected Hospital HUD Modal / Detail Bar */}
          <div className="mt-2 text-xs font-mono text-slate-400 flex items-center justify-between px-1">
            <span>Coimbatore Geographic Range: 11.0°N / 76.9°E</span>
            {selectedHospitalMap ? (
              <span className="text-cyan-300">
                Selected: <strong>{selectedHospitalMap.name}</strong> • ICU: {selectedHospitalMap.current_icu} • ER: {Math.round(selectedHospitalMap.er_occupancy * 100)}%
              </span>
            ) : (
              <span className="text-slate-500 italic">Click any facility node on radar to inspect live telemetry</span>
            )}
          </div>
        </div>

        {/* Live Command Decision Hero Card (5 Cols) */}
        <div className="xl:col-span-5 bg-gradient-to-br from-slate-900 via-slate-900/90 to-fuchsia-950/20 border border-fuchsia-900/40 rounded-2xl p-5 shadow-2xl flex flex-col justify-between backdrop-blur-md relative overflow-hidden">
          <div className="absolute top-0 right-0 w-48 h-48 bg-fuchsia-600/5 rounded-full blur-3xl pointer-events-none"></div>

          <div>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2 text-xs font-mono uppercase font-bold text-fuchsia-400">
                <span className="w-2.5 h-2.5 rounded-full bg-fuchsia-400 animate-pulse"></span>
                Optimal Dispatch Vector (Care Coordination Engine)
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950/80 border border-emerald-500/30 text-emerald-300 font-bold">
                MATCH LOCKED
              </span>
            </div>

            <div className="text-2xl lg:text-3xl font-black text-white mb-4 tracking-tight drop-shadow-md">
              {state.agent4_coordination.assigned_hospital_name}
            </div>

            {/* Triad Metric Dashboard */}
            <div className="grid grid-cols-3 gap-2.5 mb-4">
              <div className="bg-slate-950/70 border border-slate-800 p-3 rounded-xl">
                <div className="text-[10px] font-mono uppercase text-slate-500 font-bold mb-1">Transit ETA</div>
                <div className="text-xl font-black text-fuchsia-400 font-mono">
                  {state.agent4_coordination.eta} <span className="text-xs font-normal text-slate-400">min</span>
                </div>
              </div>

              <div className="bg-slate-950/70 border border-slate-800 p-3 rounded-xl">
                <div className="text-[10px] font-mono uppercase text-slate-500 font-bold mb-1">Road Distance</div>
                <div className="text-xl font-black text-cyan-400 font-mono">
                  {state.agent4_coordination.distance_km} <span className="text-xs font-normal text-slate-400">km</span>
                </div>
              </div>

              <div className="bg-slate-950/70 border border-slate-800 p-3 rounded-xl">
                <div className="text-[10px] font-mono uppercase text-slate-500 font-bold mb-1">Loss Score</div>
                <div className="text-xl font-black text-slate-200 font-mono">
                  {state.agent4_coordination.score}
                </div>
              </div>
            </div>

            {/* Allocation Reasoning */}
            <div className="bg-slate-950/80 border border-slate-800 p-3 rounded-xl text-xs text-slate-300 leading-relaxed mb-4">
              <div className="text-[10px] font-mono uppercase text-fuchsia-400 font-bold mb-1 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5" /> Multi-Agent Cost Function
              </div>
              <p>{state.agent4_coordination.reason}</p>
            </div>
          </div>

          {/* Top Ranked Alternatives */}
          {state.agent4_coordination.alternatives && state.agent4_coordination.alternatives.length > 0 && (
            <div className="pt-3 border-t border-slate-800">
              <div className="text-[10px] font-mono uppercase text-slate-500 font-bold mb-2">
                Secondary Failover Contingencies
              </div>
              <div className="space-y-1.5">
                {state.agent4_coordination.alternatives.slice(0, 2).map((alt: any, idx: number) => (
                  <div key={idx} className="bg-slate-950/60 border border-slate-800/80 px-3 py-1.5 rounded-lg flex items-center justify-between text-xs">
                    <span className="font-medium text-slate-300 truncate max-w-[210px]">{alt.name}</span>
                    <span className="text-slate-400 font-mono text-[11px]">
                      {alt.eta}m ({alt.distance_km}km) • Score {alt.score}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* =========================================================================
          4-AGENT ARCHITECTURE GRID (Clean Professional Agent Designations)
         ========================================================================= */}
      <div className={`grid grid-cols-1 lg:grid-cols-2 gap-6 transition-opacity duration-300 ${isUpdating ? 'opacity-50' : 'opacity-100'}`}>
        
        {/* ==============================================================
            AGENT 1: Triage AI Agent
           ============================================================== */}
        <div className="bg-slate-900/90 border border-slate-800 hover:border-cyan-500/40 rounded-2xl p-5 shadow-xl transition-all flex flex-col justify-between backdrop-blur-md relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-500"></div>

          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-white tracking-tight">Triage AI Agent</h2>
                <p className="text-[11px] font-mono text-cyan-400 uppercase tracking-wider">Clinical Intake & Acuity Extraction</p>
              </div>
              <span className="text-xs font-mono font-bold text-slate-400 px-2.5 py-1 rounded bg-slate-950 border border-slate-800">
                CASE #{state.patient.id}
              </span>
            </div>

            {/* Live Patient Telemetry HUD */}
            <div className="bg-[#050913] border border-slate-800 p-4 rounded-xl mb-4">
              <div className="flex items-center justify-between mb-3 pb-2.5 border-b border-slate-800/80">
                <div className="flex items-center gap-2 text-xs font-semibold text-cyan-300">
                  <MapPin className="w-4 h-4 text-cyan-400 shrink-0" />
                  <span>Pickup: <strong className="text-white">{state.patient.pickup_name}</strong></span>
                </div>
                <span className="text-[11px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  NODE: {state.patient.pickup_node}
                </span>
              </div>

              {/* Vitals Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5 mb-3">
                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                  <div className="text-[10px] font-mono text-slate-500 uppercase">Emergency</div>
                  <div className="font-bold text-slate-200 text-xs truncate mt-0.5">{state.patient.emergency_type}</div>
                </div>

                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                  <div className="text-[10px] font-mono text-slate-500 uppercase">Severity</div>
                  <div className={`font-bold text-xs mt-0.5 ${state.patient.severity === 'CRITICAL' ? 'text-red-400' : 'text-amber-400'}`}>
                    {state.patient.severity}
                  </div>
                </div>

                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                  <div className="text-[10px] font-mono text-slate-500 uppercase">SpO2 Sat</div>
                  <div className={`font-bold text-xs mt-0.5 ${state.patient.spo2 < 90 ? 'text-red-400' : 'text-emerald-400'}`}>
                    {state.patient.spo2}%
                  </div>
                </div>

                <div className="bg-slate-900/80 p-2.5 rounded-lg border border-slate-800">
                  <div className="text-[10px] font-mono text-slate-500 uppercase">Heart Rate</div>
                  <div className="font-bold text-xs text-cyan-400 mt-0.5">{state.patient.heart_rate || 80} BPM</div>
                </div>
              </div>

              {/* Simulated Cardiac Telemetry Indicator */}
              <div className="mt-2 bg-slate-950 border border-cyan-950/80 p-2 rounded-lg flex items-center justify-between text-xs font-mono">
                <span className="text-slate-500 flex items-center gap-1.5">
                  <Activity className="w-3.5 h-3.5 text-cyan-400 animate-pulse" /> Telemetry:
                </span>
                <span className="text-cyan-400 font-bold">
                  {state.patient.heart_rate > 110 ? 'SINUS TACHYCARDIA' : state.patient.heart_rate < 55 ? 'SINUS BRADYCARDIA' : 'NORMAL SINUS RHYTHM'}
                </span>
                <span className="text-slate-500">GCS: <strong className="text-white">{state.patient.consciousness || 'ALERT'}</strong></span>
              </div>
            </div>

            {/* Extracted Clinical Needs Badges */}
            <div className="mb-4">
              <div className="text-[11px] font-mono uppercase text-slate-500 font-bold mb-2">
                Clinical Requirement Matrix:
              </div>
              <div className="flex flex-wrap gap-2">
                <span className="px-2.5 py-1 rounded bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-bold font-mono">
                  Priority: {state.agent1_triage.priority}
                </span>
                <span className="px-2.5 py-1 rounded bg-amber-500/10 border border-amber-500/30 text-amber-400 text-xs font-bold font-mono">
                  {state.agent1_triage.time_sensitivity}
                </span>
                {state.agent1_triage.specialist && (
                  <span className="px-2.5 py-1 rounded bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-bold font-mono">
                    Specialist: {state.agent1_triage.specialist}
                  </span>
                )}
                {state.agent1_triage.icu_required && (
                  <span className="px-2.5 py-1 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 text-xs font-bold font-mono">
                    ICU Required
                  </span>
                )}
                {state.agent1_triage.trauma_required && (
                  <span className="px-2.5 py-1 rounded bg-orange-500/10 border border-orange-500/30 text-orange-400 text-xs font-bold font-mono">
                    Trauma Center Req
                  </span>
                )}
                {state.agent1_triage.ct_scan_required && (
                  <span className="px-2.5 py-1 rounded bg-blue-500/10 border border-blue-500/30 text-blue-300 text-xs font-bold font-mono">
                    24/7 CT Scan Req
                  </span>
                )}
                {state.agent1_triage.oxygen_required && (
                  <span className="px-2.5 py-1 rounded bg-teal-500/10 border border-teal-500/30 text-teal-300 text-xs font-bold font-mono">
                    High-Flow O2
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Agent Reasoning Box */}
          <div className="bg-[#050913] border border-cyan-900/40 rounded-xl p-3 text-xs text-slate-300">
            <div className="text-[10px] font-mono uppercase text-cyan-400 font-bold mb-1 flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5" /> Clinical Triage Inference Rationale
            </div>
            <p className="leading-relaxed">{state.agent1_triage.explanation}</p>
          </div>
        </div>

        {/* ==============================================================
            AGENT 2: Hospital Capability Agent
           ============================================================== */}
        <div className="bg-slate-900/90 border border-slate-800 hover:border-emerald-500/40 rounded-2xl p-5 shadow-xl transition-all flex flex-col justify-between backdrop-blur-md relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-emerald-500 to-teal-500"></div>

          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-white tracking-tight">Hospital Capability Agent</h2>
                <p className="text-[11px] font-mono text-emerald-400 uppercase tracking-wider">
                  Constraint Satisfaction & Capacity Verification
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-emerald-400 px-2.5 py-1 rounded bg-emerald-950/60 border border-emerald-500/30">
                {state.agent2_hospital.feasible_hospitals.length} / {state.agent2_hospital.all_evaluations.length} MATCHED
              </span>
            </div>

            {/* Search & Tabs Controls */}
            <div className="flex flex-col sm:flex-row gap-2 mb-3">
              <div className="relative flex-1">
                <Search className="w-3.5 h-3.5 absolute left-3 top-3 text-slate-500" />
                <input
                  type="text"
                  placeholder="Filter 50 hospitals by name or specialty..."
                  value={hospitalSearch}
                  onChange={e => setHospitalSearch(e.target.value)}
                  className="w-full bg-[#050913] border border-slate-800 rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-200 outline-none focus:border-emerald-500 font-mono"
                />
              </div>
              <div className="flex rounded-lg bg-[#050913] p-1 border border-slate-800 text-[11px] font-mono">
                <button
                  onClick={() => setHospitalTab('all')}
                  className={`px-2.5 py-1 rounded ${hospitalTab === 'all' ? 'bg-slate-800 text-white font-bold' : 'text-slate-400 hover:text-white'}`}
                >
                  All ({state.agent2_hospital.all_evaluations.length})
                </button>
                <button
                  onClick={() => setHospitalTab('feasible')}
                  className={`px-2.5 py-1 rounded ${hospitalTab === 'feasible' ? 'bg-emerald-900/60 text-emerald-300 font-bold' : 'text-slate-400 hover:text-emerald-400'}`}
                >
                  Feasible ({state.agent2_hospital.feasible_hospitals.length})
                </button>
                <button
                  onClick={() => setHospitalTab('rejected')}
                  className={`px-2.5 py-1 rounded ${hospitalTab === 'rejected' ? 'bg-red-900/60 text-red-300 font-bold' : 'text-slate-400 hover:text-red-400'}`}
                >
                  Rejected ({state.agent2_hospital.rejected_hospitals.length})
                </button>
              </div>
            </div>

            {/* Hospital Evaluation Cards Scrollable Feed */}
            <div className="space-y-2.5 max-h-[300px] overflow-y-auto pr-1">
              {filteredHospitals.map((h: any, idx: number) => (
                <div 
                  key={idx} 
                  className={`p-3 rounded-xl border transition-all ${
                    h.feasible 
                      ? 'bg-emerald-950/20 border-emerald-900/40 hover:border-emerald-500/50' 
                      : 'bg-[#050913] border-slate-800/80 opacity-70 hover:opacity-100'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2 mb-1.5">
                    <div>
                      <div className={`font-semibold text-xs ${h.feasible ? 'text-emerald-300 font-bold' : 'text-slate-300'}`}>
                        {h.name}
                      </div>
                      <div className="text-[10px] font-mono text-slate-500">
                        ICU Free: <strong className={h.current_icu > 0 ? 'text-emerald-400' : 'text-red-400'}>{h.current_icu} beds</strong> • ER Saturation: {Math.round(h.er_occupancy * 100)}%
                      </div>
                    </div>
                    {h.feasible ? (
                      <span className="flex items-center gap-1 px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 text-[10px] font-mono font-bold">
                        <CheckCircle2 className="w-3 h-3" /> MATCH
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 rounded bg-red-500/10 text-red-400 border border-red-500/20 text-[10px] font-mono font-bold">
                        REJECTED
                      </span>
                    )}
                  </div>

                  {/* Constraint Checklist / Reason */}
                  <div className="text-[11px] font-mono text-slate-400 mt-1 flex flex-col gap-0.5">
                    {h.rejection_reasons.map((r: string, r_idx: number) => (
                      <div key={r_idx} className="flex items-start gap-1.5">
                        <span className={`text-[10px] font-mono font-bold ${h.feasible ? 'text-emerald-400' : 'text-red-400'}`}>
                          {h.feasible ? '[PASS]' : '[FAIL]'}
                        </span>
                        <span className={h.feasible ? 'text-slate-300' : 'text-red-300/80'}>{r}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ==============================================================
            AGENT 3: Mobility & Routing Agent
           ============================================================== */}
        <div className="bg-slate-900/90 border border-slate-800 hover:border-amber-500/40 rounded-2xl p-5 shadow-xl transition-all flex flex-col justify-between backdrop-blur-md relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-amber-500 to-orange-500"></div>

          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-white tracking-tight">Mobility & Routing Agent</h2>
                <p className="text-[11px] font-mono text-amber-400 uppercase tracking-wider">
                  A* Heuristic Graph Search (Coimbatore Road Network)
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-amber-400 px-2.5 py-1 rounded bg-amber-950/60 border border-amber-500/30">
                {state.agent3_mobility.length} A* ROUTES SOLVED
              </span>
            </div>

            <div className="bg-[#050913] p-3 rounded-xl border border-slate-800 mb-3 text-xs font-mono flex items-center justify-between text-slate-400">
              <span>Origin: <strong className="text-white">{state.patient.pickup_name}</strong></span>
              <span>Heuristic: <strong className="text-cyan-400">Admissible Haversine h(n)</strong></span>
            </div>

            {/* Candidate Route Cards */}
            <div className="space-y-2.5 max-h-[300px] overflow-y-auto pr-1">
              {state.agent3_mobility.map((r: any, idx: number) => (
                <div key={idx} className="bg-[#050913] border border-slate-800 p-3 rounded-xl hover:border-slate-700 transition-colors">
                  <div className="flex items-center justify-between mb-1.5">
                    <div className="font-semibold text-slate-200 text-xs flex items-center gap-1.5">
                      <Navigation className="w-3 h-3 text-slate-500" />
                      <span>{r.name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`font-mono font-bold text-sm ${r.route_status === 'DELAYED' ? 'text-amber-400' : 'text-emerald-400'}`}>
                        {r.actual_eta_min} min
                      </span>
                      {r.route_status === 'DELAYED' && (
                        <span className="text-[10px] font-mono text-slate-500 line-through">{r.base_eta_min}m</span>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                    <span>Transit Distance: <strong className="text-slate-200">{r.distance_km} km</strong></span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${r.route_status === 'DELAYED' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-emerald-500/10 text-emerald-400'}`}>
                      {r.route_status}
                    </span>
                  </div>

                  {r.search_metrics && (
                    <div className="mt-1 text-[10px] font-mono text-cyan-400/90 flex items-center justify-between">
                      <span>Path: {r.search_metrics.path_nodes}</span>
                      <span>Expanded: {r.search_metrics.nodes_expanded} nodes</span>
                    </div>
                  )}

                  <div className="mt-1.5 text-[11px] font-mono text-slate-500 border-t border-slate-800/80 pt-1">
                    {r.reason}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* ==============================================================
            AGENT 4: Care Coordination Agent
           ============================================================== */}
        <div className="bg-slate-900/90 border border-slate-800 hover:border-fuchsia-500/40 rounded-2xl p-5 shadow-xl transition-all flex flex-col justify-between backdrop-blur-md relative overflow-hidden">
          <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-fuchsia-500 to-purple-500"></div>

          <div>
            <div className="flex items-center justify-between mb-4">
              <div>
                <h2 className="text-lg font-bold text-white tracking-tight">Care Coordination Agent</h2>
                <p className="text-[11px] font-mono text-fuchsia-400 uppercase tracking-wider">
                  Multi-Objective Optimization & Failover Resolution
                </p>
              </div>
              <span className="text-xs font-mono font-bold text-fuchsia-400 px-2.5 py-1 rounded bg-fuchsia-950/60 border border-fuchsia-500/30">
                DISPATCH VERIFIED
              </span>
            </div>

            <div className="bg-[#050913] p-4 rounded-xl border border-slate-800 mb-4">
              <div className="text-[10px] font-mono uppercase text-slate-500 font-bold mb-1">Assigned Medical Facility</div>
              <div className="text-xl font-black text-white">{state.agent4_coordination.assigned_hospital_name}</div>
              
              <div className="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-800 text-xs font-mono">
                <div>
                  <span className="text-slate-500 text-[10px] block">ETA</span>
                  <span className="font-bold text-fuchsia-400 text-sm">{state.agent4_coordination.eta} min</span>
                </div>
                <div>
                  <span className="text-slate-500 text-[10px] block">DISTANCE</span>
                  <span className="font-bold text-cyan-400 text-sm">{state.agent4_coordination.distance_km} km</span>
                </div>
                <div>
                  <span className="text-slate-500 text-[10px] block">SCORE</span>
                  <span className="font-bold text-slate-200 text-sm">{state.agent4_coordination.score}</span>
                </div>
              </div>
            </div>

            <div className="bg-[#050913] border border-fuchsia-900/40 p-3.5 rounded-xl text-xs text-slate-300 mb-3">
              <div className="text-[10px] font-mono uppercase text-fuchsia-400 font-bold mb-1.5 flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5" /> Multi-Agent Cost Function
              </div>
              <p className="leading-relaxed">{state.agent4_coordination.reason}</p>
            </div>
          </div>

          {/* Failover Readiness Pill */}
          <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl flex items-center justify-between text-xs font-mono">
            <span className="text-slate-400">Failover Readiness:</span>
            <span className="text-emerald-400 font-bold flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              {state.agent4_coordination.alternatives?.length || 0} Standby Routes Armed
            </span>
          </div>
        </div>

      </div>

      {/* =========================================================================
          MODAL: EMERGENCY INTAKE DISPATCH FORM
         ========================================================================= */}
      {showPatientForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 backdrop-blur-md p-4 animate-in fade-in">
          <form 
            onSubmit={submitNewPatient} 
            className="bg-[#0b121e] border border-cyan-500/40 p-6 rounded-2xl shadow-2xl w-full max-w-xl animate-in zoom-in-95 duration-200"
          >
            <div className="flex justify-between items-center mb-6 pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2.5">
                <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
                  <UserPlus className="w-5 h-5" />
                </div>
                <div>
                  <h2 className="text-lg font-bold text-white tracking-tight">Emergency Incident Dispatch Intake</h2>
                  <p className="text-[10px] font-mono uppercase text-cyan-400">Coimbatore Ambulance Coordination System</p>
                </div>
              </div>
              <button 
                type="button" 
                onClick={() => setShowPatientForm(false)} 
                className="text-slate-400 hover:text-white transition-colors"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                  Emergency Medical Protocol
                </label>
                <select 
                  value={patientData.emergency_type} 
                  onChange={e => setPatientData({...patientData, emergency_type: e.target.value})} 
                  className="w-full bg-[#050913] border border-slate-800 rounded-lg p-3 text-slate-200 outline-none focus:border-cyan-500 font-mono text-xs"
                >
                  <option value="SEVERE_TRAUMA">Severe Polytrauma (Road Traffic Collision / Crush Injury)</option>
                  <option value="CARDIAC_ARREST">Acute STEMI / Cardiac Arrest (Cath Lab / Telemetry Protocol)</option>
                  <option value="STROKE">Acute Ischemic Stroke (Golden Hour CT / Neuro-ICU Pathway)</option>
                  <option value="BURN">Severe Burn Injury (High TBSA / Inhalation Trauma)</option>
                  <option value="FRACTURE">Compound / Unstable Bone Fracture (Orthopedic Reduction)</option>
                  <option value="RESPIRATORY_DISTRESS">Acute Respiratory Failure (Ventilator / Hypoxia Protocol)</option>
                  <option value="UROLOGY_EMERGENCY">Acute Kidney / Urological Emergency</option>
                  <option value="EYE_TRAUMA">Ocular Trauma / Acute Chemical Injury</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                  Pickup Location (Coimbatore Metropolitan Zone)
                </label>
                <select 
                  value={patientData.pickup_location} 
                  onChange={e => setPatientData({...patientData, pickup_location: e.target.value})} 
                  className="w-full bg-[#050913] border border-slate-800 rounded-lg p-3 text-cyan-300 outline-none focus:border-cyan-500 font-mono font-semibold text-xs"
                >
                  {state.pickup_locations?.map((loc: any) => (
                    <option key={loc.id} value={loc.id}>{loc.name}</option>
                  ))}
                </select>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                    Acuity / Severity
                  </label>
                  <select 
                    value={patientData.severity} 
                    onChange={e => setPatientData({...patientData, severity: e.target.value})} 
                    className="w-full bg-[#050913] border border-slate-800 rounded-lg p-3 text-slate-200 outline-none focus:border-cyan-500 font-mono text-xs"
                  >
                    <option value="CRITICAL">Critical (Immediate Life-Threat)</option>
                    <option value="HIGH">High (Emergent)</option>
                    <option value="MODERATE">Moderate (Urgent)</option>
                    <option value="LOW">Low (Non-Urgent)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                    Consciousness (GCS)
                  </label>
                  <select 
                    value={patientData.consciousness} 
                    onChange={e => setPatientData({...patientData, consciousness: e.target.value})} 
                    className="w-full bg-[#050913] border border-slate-800 rounded-lg p-3 text-slate-200 outline-none focus:border-cyan-500 font-mono text-xs"
                  >
                    <option value="ALERT">Alert (GCS 15)</option>
                    <option value="ALTERED">Altered (GCS 9-14)</option>
                    <option value="UNRESPONSIVE">Unresponsive (GCS &lt; 8)</option>
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                    SpO2 Saturation (%)
                  </label>
                  <input 
                    type="number" min="50" max="100" 
                    value={patientData.spo2} 
                    onChange={e => setPatientData({...patientData, spo2: parseInt(e.target.value) || 90})} 
                    className="w-full bg-[#050913] border border-slate-800 rounded-lg p-3 text-slate-200 outline-none focus:border-cyan-500 font-mono text-xs" 
                  />
                </div>
                <div>
                  <label className="block text-xs font-mono font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                    Heart Rate (BPM)
                  </label>
                  <input 
                    type="number" min="30" max="220" 
                    value={patientData.heart_rate} 
                    onChange={e => setPatientData({...patientData, heart_rate: parseInt(e.target.value) || 80})} 
                    className="w-full bg-[#050913] border border-slate-800 rounded-lg p-3 text-slate-200 outline-none focus:border-cyan-500 font-mono text-xs" 
                  />
                </div>
              </div>
            </div>
            
            <div className="flex gap-3">
              <button 
                type="button" 
                onClick={() => setShowPatientForm(false)} 
                className="w-1/3 bg-slate-800 hover:bg-slate-700 text-slate-300 font-mono font-bold py-3 px-4 rounded-xl text-xs uppercase"
              >
                Cancel
              </button>
              <button 
                type="submit" 
                className="w-2/3 bg-blue-600 hover:bg-blue-500 text-white font-mono font-bold py-3 px-4 rounded-xl text-xs uppercase tracking-wider shadow-lg shadow-blue-600/30 transition-all active:scale-95"
              >
                Authorize Dispatch
              </button>
            </div>
          </form>
        </div>
      )}

    </div>
  );
}
