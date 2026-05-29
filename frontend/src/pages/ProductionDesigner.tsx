import { useState, useCallback, useRef, useEffect, useMemo } from "react";
import { useLocation, useParams } from "react-router-dom";
import {
  ReactFlow,
  addEdge,
  Background,
  BackgroundVariant,
  Controls,
  Panel,
  useNodesState,
  useEdgesState,
  useReactFlow,
  ReactFlowProvider,
  type Connection,
  type Edge,
  type Node,
  MarkerType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import {
  CalendarPlus,
  FloppyDisk,
  Trash,
  X,
  Check,
  Lightbulb,
  Leaf,
  FilmStrip,
  DownloadSimple,
  CornersOut,
} from "@phosphor-icons/react";
import { api } from "../api";
import type { ActivityEvent } from "../types";
import { useToast } from "../contexts/ToastContext";
import taskList from "../assets/diary-planner/task-list.png";
import goalTracking from "../assets/diary-planner/goal-tracking.png";
import notesSketch from "../assets/diary-planner/notes-sketch.png";
import habitTracker from "../assets/diary-planner/habit-tracker.png";
import reflectionJournal from "../assets/diary-planner/reflection-journal.png";
import dashboardHeroPlanet from "../assets/diary-planner/dashboard-hero-planet.png";
import productionsFilmSet from "../assets/diary-planner/productions-film-set.png";
import ProductionNode from "../components/flow/ProductionNode";
import DayNode from "../components/flow/DayNode";
import ActivityNode from "../components/flow/ActivityNode";
import EpisodeNode from "../components/flow/EpisodeNode";

type PlannerNodeData = {
  title?: string;
  shoot_days?: number;
  type?: string;
  episodes?: number;
  dayNumber?: number;
  episodeNumber?: number;
  date?: string;
  phase?: string;
  totalEmissions?: string | number;
  onAddActivity?: (id: string) => void;
  category?: string;
  value?: string | number;
  unit?: string;
  kgco2e?: string | number;
  label?: string;
  alternative?: { name: string; saving: string };
  details?: any;
};

const nodeTypes = {
  productionNode: ProductionNode,
  dayNode: DayNode,
  activityNode: ActivityNode,
  episodeNode: EpisodeNode,
};

const templates = [
  { category: "Energy", label: "Grid power", value: 100, unit: "kWh", alt: { name: "Renewable tariff", saving: "~50%" } },
  { category: "Travel", label: "Crew shuttle", value: 50, unit: "km", alt: { name: "EV shuttle", saving: "~60%" } },
  { category: "Living", label: "Hotel nights", value: 20, unit: "nights", alt: { name: "Green Key hotel", saving: "~30%" } },
  { category: "Waste", label: "Mixed waste", value: 100, unit: "kg", alt: { name: "Zero-waste plan", saving: "~40%" } },
];

function calcCarbon(label: string, details?: any): number {
  if (!details) return 45;
  const rooms = Number(details.rooms) || 1;
  const nights = Number(details.nights) || 1;
  if (label.includes("hotel") || label.includes("Hotel")) return rooms * nights * 25;
  return 45;
}

function PlannerCanvas() {
  const location = useLocation();
  const { id } = useParams<{ id: string }>();
  const { screenToFlowPosition } = useReactFlow();
  const [existingProd, setExistingProd] = useState<any>(null);
  const [loadingProd, setLoadingProd] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (id) {
      setLoadingProd(true);
      api.getProduction(id)
        .then((p) => setExistingProd(p))
        .catch((e) => toast.error("Failed to load production", e.message))
        .finally(() => setLoadingProd(false));
    }
  }, [id, toast]);

  const initialForm = existingProd || location.state?.initialForm;
  const prodType = initialForm?.type || "FEATURE";
  const isSeries = prodType === "TV_SERIES" || (initialForm?.episodes || 1) > 1;
  const [carbonBudget, setCarbonBudget] = useState(0);

  const [nodes, setNodes, onNodesChange] = useNodesState<Node<PlannerNodeData>>([
    {
      id: "root",
      type: "productionNode",
      position: { x: 400, y: 50 },
      data: { title: initialForm?.title || "Untitled", shoot_days: initialForm?.shoot_days || 0, type: prodType, episodes: initialForm?.episodes || 1 },
    },
  ]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [lastDayId, setLastDayId] = useState<string | null>(null);
  const [editingNode, setEditingNode] = useState<Node<PlannerNodeData> | null>(null);
  const [editForm, setEditForm] = useState<PlannerNodeData>({});
  const [isFullscreen, setIsFullscreen] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  const stats = useMemo(() => {
    const acts = nodes.filter((n) => n.type === "activityNode");
    const total = acts.reduce((sum, n) => sum + (Number(n.data.kgco2e) || 0), 0);
    const byCat: Record<string, number> = {};
    acts.forEach((n) => {
      const cat = n.data.category || "Other";
      byCat[cat] = (byCat[cat] || 0) + (Number(n.data.kgco2e) || 0);
    });
    return { total, byCat, count: acts.length };
  }, [nodes]);

  useEffect(() => {
    const prodId = initialForm?.production_id;
    if (!prodId) return;
    setNodes([
      {
        id: "root",
        type: "productionNode",
        position: { x: 400, y: 50 },
        data: { title: initialForm?.title || "Untitled", shoot_days: initialForm?.shoot_days || 0, type: prodType, episodes: initialForm?.episodes || 1 },
      },
    ]);
    setEdges([]);
    setLastDayId(null);
    loadPlanner().then(async (restored) => {
      if (restored) return;

      // No saved layout — try to populate from actual activity events
      try {
        const events = await api.getEvents(prodId);
        if (events && events.length > 0) {
          const byDate: Record<string, ActivityEvent[]> = {};
          events.forEach((ev) => {
            const date = ev.recorded_at.split("T")[0];
            if (!byDate[date]) byDate[date] = [];
            byDate[date].push(ev);
          });

          const sortedDates = Object.keys(byDate).sort();
          const newNodes: Node<PlannerNodeData>[] = [];
          const newEdges: Edge[] = [];

          sortedDates.forEach((date, idx) => {
            const dayId = `day-${idx + 1}`;
            const dayX = 100 + idx * 260;
            const dayY = 260;

            newNodes.push({
              id: dayId,
              type: "dayNode",
              position: { x: dayX, y: dayY },
              data: { dayNumber: idx + 1, date, totalEmissions: 0 },
            });
            newEdges.push({
              id: `e-root-${dayId}`,
              source: "root",
              target: dayId,
              animated: true,
              markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" },
              style: { stroke: "#10b981", strokeWidth: 2 },
            });

            byDate[date].forEach((ev, actIdx) => {
              const actId = `act-${ev.event_id}`;
              newNodes.push({
                id: actId,
                type: "activityNode",
                position: {
                  x: dayX + (actIdx % 2 === 0 ? -30 : 30),
                  y: dayY + 180 + actIdx * 80,
                },
                data: {
                  category: ev.category,
                  label: ev.subcategory,
                  value: Number(ev.value),
                  unit: ev.unit,
                  kgco2e: Number(ev.kgco2e).toFixed(1),
                  phase: ev.phase,
                },
              });
              newEdges.push({
                id: `e-${dayId}-${actId}`,
                source: dayId,
                target: actId,
                markerEnd: { type: MarkerType.ArrowClosed, color: "#94a3b8" },
                style: { stroke: "#94a3b8", strokeWidth: 1.5 },
              });
            });
          });

          setNodes((nds) => [...nds, ...newNodes]);
          setEdges((eds) => [...eds, ...newEdges]);
          const lastDay = newNodes.filter((n) => n.type === "dayNode").pop();
          if (lastDay) setLastDayId(lastDay.id);
          return;
        }
      } catch {
        // Fall through to empty bootstrap
      }

      // Fallback: bootstrap empty day nodes from initialForm
      const newNodes: Node<PlannerNodeData>[] = [];
      const newEdges: Edge[] = [];
      if (isSeries && initialForm.episodes > 1) {
        const epCount = Math.min(initialForm.episodes, 12);
        const daysPerEp = Math.max(1, Math.floor((initialForm.shoot_days || 5) / epCount));
        for (let ep = 1; ep <= epCount; ep++) {
          const epId = `ep-${ep}`;
          newNodes.push({ id: epId, type: "episodeNode", position: { x: 100 + (ep - 1) * 300, y: 200 }, data: { episodeNumber: ep, title: `Episode ${ep}`, totalEmissions: 0 } });
          newEdges.push({ id: `e-root-${epId}`, source: "root", target: epId, animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" }, style: { stroke: "#3b82f6", strokeWidth: 2 } });
          for (let d = 1; d <= Math.min(daysPerEp, 5); d++) {
            const globalDay = (ep - 1) * daysPerEp + d;
            const dayId = `day-${globalDay}`;
            newNodes.push({ id: dayId, type: "dayNode", position: { x: 100 + (ep - 1) * 300 + (d - 1) * 200, y: 380 }, data: { dayNumber: globalDay, date: new Date(Date.now() + (globalDay - 1) * 86400000).toISOString().split('T')[0], totalEmissions: 0 } });
            newEdges.push({ id: `e-${epId}-${dayId}`, source: epId, target: dayId, animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" }, style: { stroke: "#10b981", strokeWidth: 2 } });
          }
        }
      } else {
        const count = Math.min(initialForm.shoot_days || 0, 14);
        for (let i = 1; i <= count; i++) {
          const dayId = `day-${i}`;
          newNodes.push({ id: dayId, type: "dayNode", position: { x: 100 + (i - 1) * 260, y: 260 }, data: { dayNumber: i, date: new Date(Date.now() + (i - 1) * 86400000).toISOString().split('T')[0], totalEmissions: 0 } });
          newEdges.push({ id: `e-root-${dayId}`, source: "root", target: dayId, animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" }, style: { stroke: "#10b981", strokeWidth: 2 } });
        }
      }
      if (newNodes.length > 0) {
        setNodes((nds) => [...nds, ...newNodes]);
        setEdges((eds) => [...eds, ...newEdges]);
        const lastDay = newNodes.filter((n) => n.type === "dayNode").pop();
        if (lastDay) setLastDayId(lastDay.id);
      }
    });
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialForm?.production_id]);

  const addActivity = useCallback((dayId: string, customData?: PlannerNodeData) => {
    const activityId = `act-${Date.now()}-${Math.random().toString(36).substr(2, 5)}`;
    const dayNode = nodes.find((n) => n.id === dayId);
    if (!dayNode) return;
    const childCount = edges.filter((e) => e.source === dayId).length;
    const newNode: Node<PlannerNodeData> = {
      id: activityId,
      type: "activityNode",
      position: { x: dayNode.position.x + (childCount % 2 === 0 ? -30 : 30), y: dayNode.position.y + 180 + childCount * 80 },
      data: customData || { category: "Energy", label: "Grid power", value: 100, unit: "kWh", kgco2e: 45.0 },
    };
    const newEdge: Edge = { id: `e-${dayId}-${activityId}`, source: dayId, target: activityId, markerEnd: { type: MarkerType.ArrowClosed, color: "#94a3b8" }, style: { stroke: "#94a3b8", strokeWidth: 1.5 } };
    setNodes((nds) => [...nds, newNode]);
    setEdges((eds) => [...eds, newEdge]);
  }, [nodes, edges, setNodes, setEdges]);

  const addDay = () => {
    const dayCount = nodes.filter((n) => n.type === "dayNode").length + 1;
    const dayId = `day-${dayCount}`;
    const episodeNodes = nodes.filter((n) => n.type === "episodeNode");
    const parentId = isSeries && episodeNodes.length > 0 ? episodeNodes[episodeNodes.length - 1].id : "root";
    const parentNode = nodes.find((n) => n.id === parentId);
    const siblingDays = edges.filter((e) => e.source === parentId).length;
    setNodes((nds) => [...nds, { id: dayId, type: "dayNode", position: { x: (parentNode?.position.x || 100) + siblingDays * 260, y: (parentNode?.position.y || 50) + 180 }, data: { dayNumber: dayCount, date: new Date(Date.now() + (dayCount - 1) * 86400000).toISOString().split('T')[0], totalEmissions: 0 } }]);
    setEdges((eds) => [...eds, { id: `e-${parentId}-${dayId}`, source: parentId, target: dayId, animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" }, style: { stroke: "#10b981", strokeWidth: 2 } }]);
    setLastDayId(dayId);
  };

  const addEpisode = () => {
    const epCount = nodes.filter((n) => n.type === "episodeNode").length + 1;
    const epId = `ep-${epCount}`;
    setNodes((nds) => [...nds, { id: epId, type: "episodeNode", position: { x: 100 + (epCount - 1) * 300, y: 200 }, data: { episodeNumber: epCount, title: `Episode ${epCount}`, totalEmissions: 0 } }]);
    setEdges((eds) => [...eds, { id: `e-root-${epId}`, source: "root", target: epId, animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: "#3b82f6" }, style: { stroke: "#3b82f6", strokeWidth: 2 } }]);
  };

  const addTemplateToCanvas = useCallback((template: any, preferDayId?: string): string => {
    let dayId = preferDayId || lastDayId;
    if (!dayId) {
      const dayCount = 1;
      dayId = `day-auto-${Date.now()}`;
      const rootNode = nodes.find((n) => n.id === "root");
      setNodes((nds) => [...nds, { id: dayId!, type: "dayNode", position: { x: (rootNode?.position.x || 400) - 100, y: (rootNode?.position.y || 50) + 210 }, data: { dayNumber: dayCount, date: new Date().toISOString().split('T')[0], totalEmissions: 0 } }]);
      setEdges((eds) => [...eds, { id: `e-root-${dayId}`, source: "root", target: dayId!, animated: true, markerEnd: { type: MarkerType.ArrowClosed, color: "#10b981" }, style: { stroke: "#10b981", strokeWidth: 2 } }]);
      setLastDayId(dayId);
    }
    addActivity(dayId!, { category: template.category, label: template.label, value: template.value, unit: template.unit, kgco2e: calcCarbon(template.label).toFixed(1), alternative: template.alt });
    return dayId!;
  }, [lastDayId, nodes, addActivity, setNodes, setEdges]);

  const onConnect = useCallback((params: Connection) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const savePlanner = useCallback(async () => {
    if (!initialForm?.production_id) { toast.error("Save failed", "No production ID."); return; }
    try {
      await api.savePlanner(initialForm.production_id, { nodes: nodes.map((n) => ({ id: n.id, type: n.type, position: n.position, data: n.data })), edges: edges.map((e) => ({ id: e.id, source: e.source, target: e.target })), lastDayId });
      toast.success("Planner saved", "Layout saved to server.");
    } catch { toast.error("Save failed", "Could not save planner state."); }
  }, [nodes, edges, lastDayId, initialForm, toast]);

  const loadPlanner = useCallback(async () => {
    if (!initialForm?.production_id) return false;
    try {
      const res = await api.getPlanner(initialForm.production_id);
      const payload = res.planner_state;
      if (!payload) return false;
      if (payload.nodes && Array.isArray(payload.nodes)) setNodes(payload.nodes.map((n: any) => ({ ...n, draggable: true })));
      if (payload.edges && Array.isArray(payload.edges)) setEdges(payload.edges);
      if (payload.lastDayId) setLastDayId(payload.lastDayId);
      return true;
    } catch { return false; }
  }, [initialForm, setNodes, setEdges]);

  const exportCSV = () => {
    const acts = nodes.filter((n) => n.type === "activityNode");
    if (acts.length === 0) { toast.warning("Nothing to export", "Add activities first."); return; }
    const rows = [["day_id", "category", "label", "kgco2e", "details"].join(","), ...acts.map((n) => [edges.find((e) => e.target === n.id)?.source || "", n.data.category || "", n.data.label || "", n.data.kgco2e || "", JSON.stringify(n.data.details || {}).replace(/"/g, '""')].map((v) => `"${v}"`).join(","))];
    const blob = new Blob([rows.join("\n")], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${initialForm?.title || "planner"}-activities.csv`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("CSV exported", `${acts.length} activities downloaded.`);
  };

  const onNodeDoubleClick = useCallback((_event: any, node: Node<PlannerNodeData>) => {
    setEditingNode(node);
    setEditForm({ ...node.data });
  }, []);

  const saveEdit = () => {
    if (!editingNode) return;
    setNodes((nds) => nds.map((n) => (n.id === editingNode.id ? { ...n, data: { ...editForm } } : n)));
    setEditingNode(null);
  };

  const DRAG_KEY = "text/plain";
  const DRAG_PREFIX = "terra-template::";

  const onDragOver = useCallback((event: React.DragEvent | DragEvent) => {
    if ((event as any).dataTransfer?.types?.includes?.(DRAG_KEY)) { event.preventDefault(); (event as any).dataTransfer.dropEffect = "move"; }
  }, []);

  const dropRef = useRef({ nodes, lastDayId, screenToFlowPosition, addTemplateToCanvas, toast });
  useEffect(() => { dropRef.current = { nodes, lastDayId, screenToFlowPosition, addTemplateToCanvas, toast }; });

  const handleNativeDrop = useCallback((event: DragEvent) => {
    event.preventDefault();
    const raw = event.dataTransfer?.getData(DRAG_KEY) ?? "";
    if (!raw.startsWith(DRAG_PREFIX)) return;
    let template: any;
    try { template = JSON.parse(raw.slice(DRAG_PREFIX.length)); } catch { return; }
    const { nodes: nds, lastDayId: lid, screenToFlowPosition: s2f, addTemplateToCanvas: addT, toast: t } = dropRef.current;
    const pos = s2f({ x: event.clientX, y: event.clientY });
    const targetDay = nds.find((n) => n.type === "dayNode" && Math.abs(n.position.x - pos.x) < 240 && Math.abs(n.position.y - pos.y) < 160);
    addT(template, targetDay?.id || lid || undefined);
    t.success(`${template.label} added`);
  }, []);

  const flowWrapperRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = flowWrapperRef.current;
    if (!el) return;
    el.addEventListener("dragover", onDragOver as EventListener);
    el.addEventListener("drop", handleNativeDrop);
    return () => { el.removeEventListener("dragover", onDragOver as EventListener); el.removeEventListener("drop", handleNativeDrop); };
  }, [onDragOver, handleNativeDrop]);

  if (loadingProd) {
    return (
      <div className="flex items-center justify-center h-[60vh]">
        <div className="animate-spin w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full" />
      </div>
    );
  }

  return (
    <div ref={containerRef} className={`flex bg-white overflow-hidden border border-slate-200 relative transition-all ${isFullscreen ? "fixed inset-0 z-[9990] rounded-none border-0" : "rounded-2xl h-[calc(100vh-120px)] w-full"}`}>
      <div className="w-72 bg-white border-r border-slate-100 flex flex-col z-20">
        <div className="px-5 pt-5 pb-4 border-b border-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 bg-emerald-50 rounded-xl text-emerald-600"><Leaf size={20} weight="fill" /></div>
            <div>
              <div className="font-bold text-slate-800 text-[15px]">Planner</div>
              <div className="text-[11px] text-slate-400">{initialForm?.title || "New production"}</div>
            </div>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
          <div>
            <div className="text-[11px] font-bold text-slate-400 tracking-wider uppercase mb-2">Templates</div>
            <div className="space-y-2">
              {templates.map((t) => (
                <div key={t.label} draggable onDragStart={(e) => e.dataTransfer.setData(DRAG_KEY, DRAG_PREFIX + JSON.stringify(t))} className="cursor-grab active:cursor-grabbing bg-slate-50 hover:bg-emerald-50 border border-slate-100 hover:border-emerald-200 rounded-xl p-3 transition group">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-slate-700">{t.label}</span>
                    <span className="text-[10px] text-slate-400">{t.value} {t.unit}</span>
                  </div>
                  {t.alt && <div className="text-[10px] text-emerald-600 mt-1 opacity-0 group-hover:opacity-100 transition">Alt: {t.alt.name} ({t.alt.saving})</div>}
                </div>
              ))}
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <img src={taskList} alt="" className="w-full h-16 object-cover rounded-lg" />
            <img src={goalTracking} alt="" className="w-full h-16 object-cover rounded-lg" />
            <img src={notesSketch} alt="" className="w-full h-16 object-cover rounded-lg" />
            <img src={habitTracker} alt="" className="w-full h-16 object-cover rounded-lg" />
            <img src={reflectionJournal} alt="" className="w-full h-16 object-cover rounded-lg" />
            <img src={productionsFilmSet} alt="" className="w-full h-16 object-cover rounded-lg" />
          </div>

          <div>
            <div className="text-[11px] font-bold text-slate-400 tracking-wider uppercase mb-2">Actions</div>
            <div className="space-y-2">
              <button onClick={addDay} className="w-full flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-50 hover:bg-emerald-50 text-slate-600 hover:text-emerald-700 text-xs font-medium transition"><CalendarPlus size={14} /> Add day</button>
              {isSeries && <button onClick={addEpisode} className="w-full flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-50 hover:bg-emerald-50 text-slate-600 hover:text-emerald-700 text-xs font-medium transition"><FilmStrip size={14} /> Add episode</button>}
              <button onClick={exportCSV} className="w-full flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-50 hover:bg-emerald-50 text-slate-600 hover:text-emerald-700 text-xs font-medium transition"><DownloadSimple size={14} /> Export CSV</button>
              <button onClick={() => { setNodes([nodes[0]]); setEdges([]); setLastDayId(null); toast.success("Planner cleared"); }} className="w-full flex items-center gap-2 px-3 py-2 rounded-xl bg-slate-50 hover:bg-rose-50 text-slate-600 hover:text-rose-700 text-xs font-medium transition"><Trash size={12} /> Clear planner</button>
            </div>
          </div>
        </div>

        <div className="px-5 py-4 border-t border-slate-50">
          <div className="text-[11px] font-bold text-slate-400 tracking-wider uppercase mb-2">Carbon budget</div>
          <input type="number" value={carbonBudget} onChange={(e) => setCarbonBudget(Number(e.target.value))} placeholder="tCO₂e budget" className="w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-xs" />
          <div className="mt-2 h-2 bg-slate-100 rounded-full overflow-hidden">
            <div className="h-full bg-emerald-500 rounded-full transition-all" style={{ width: `${Math.min(100, carbonBudget > 0 ? (stats.total / 1000 / carbonBudget) * 100 : 0)}%` }} />
          </div>
          <div className="flex justify-between text-[10px] text-slate-400 mt-1">
            <span>{(stats.total / 1000).toFixed(2)} tCO₂e</span>
            <span>{stats.count} activities</span>
          </div>
        </div>
      </div>

      <div className="flex-1 relative" ref={flowWrapperRef}>
        <ReactFlow nodes={nodes} edges={edges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} onNodeDoubleClick={onNodeDoubleClick} nodeTypes={nodeTypes} fitView>
          <Background variant={BackgroundVariant.Dots} gap={16} size={1} color="#e2e8f0" />
          <Controls />
          <Panel position="top-right">
            <div className="flex gap-2">
              <button onClick={() => setIsFullscreen((f) => !f)} className="p-2 bg-white border border-slate-200 rounded-lg shadow-sm hover:bg-slate-50 text-slate-500"><CornersOut size={16} /></button>
              <button onClick={savePlanner} className="px-5 py-2.5 bg-white text-emerald-700 border border-emerald-200 rounded-xl font-bold shadow-md hover:bg-emerald-50 flex items-center gap-2 transition-all text-xs active:scale-95"><FloppyDisk size={14} /> Save</button>
            </div>
          </Panel>
        </ReactFlow>
      </div>

      {editingNode && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-black/30 backdrop-blur-sm" onClick={() => setEditingNode(null)}>
          <div className="bg-white rounded-2xl shadow-2xl w-96 p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-bold text-slate-800">Edit activity</h3>
              <button onClick={() => setEditingNode(null)} className="text-slate-400 hover:text-slate-600"><X size={18} /></button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-medium text-slate-500">Label</label>
                <input value={editForm.label || ""} onChange={(e) => setEditForm({ ...editForm, label: e.target.value })} className="w-full mt-1 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm" />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs font-medium text-slate-500">Value</label>
                  <input type="number" value={editForm.value || ""} onChange={(e) => setEditForm({ ...editForm, value: Number(e.target.value) })} className="w-full mt-1 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm" />
                </div>
                <div>
                  <label className="text-xs font-medium text-slate-500">Unit</label>
                  <input value={editForm.unit || ""} onChange={(e) => setEditForm({ ...editForm, unit: e.target.value })} className="w-full mt-1 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm" />
                </div>
              </div>
              <div>
                <label className="text-xs font-medium text-slate-500">kgCO₂e</label>
                <input type="number" value={editForm.kgco2e || ""} onChange={(e) => setEditForm({ ...editForm, kgco2e: Number(e.target.value) })} className="w-full mt-1 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm" />
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-5">
              <button onClick={() => setEditingNode(null)} className="px-4 py-2 rounded-lg text-xs font-medium text-slate-500 hover:bg-slate-50">Cancel</button>
              <button onClick={saveEdit} className="px-4 py-2 rounded-lg text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 flex items-center gap-1.5"><Check size={14} /> Save</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default function ProductionDesigner() {
  return (
    <ReactFlowProvider>
      <PlannerCanvas />
    </ReactFlowProvider>
  );
}
