import { Handle, Position } from "@xyflow/react";

const categoryColors: Record<string, string> = {
  Energy: "bg-amber-400",
  Travel: "bg-blue-400",
  Living: "bg-violet-400",
  Waste: "bg-emerald-400",
  Water: "bg-cyan-400",
  "VFX/Post": "bg-indigo-400",
};

export default function ActivityNode({ id, data }: any) {
  const color = categoryColors[data.category || "Energy"] || "bg-slate-400";
  return (
    <div className="bg-white border border-slate-200 rounded-xl px-3 py-2 shadow-sm min-w-[120px]">
      <div className={`w-2 h-2 rounded-full ${color} mb-1`} />
      <div className="text-[11px] font-semibold text-slate-700 truncate">{data.label || "Activity"}</div>
      <div className="text-[10px] text-slate-400">
        {data.value} {data.unit}
      </div>
      <div className="text-[10px] text-emerald-600 font-semibold">
        {data.kgco2e ? `${Number(data.kgco2e).toFixed(1)} kg` : "—"}
      </div>
      <Handle type="target" position={Position.Top} className="!bg-slate-300" />
    </div>
  );
}
