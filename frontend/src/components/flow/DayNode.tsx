import { Handle, Position } from "@xyflow/react";
import { Plus } from "@phosphor-icons/react";

export default function DayNode({ id, data }: any) {
  return (
    <div className="bg-white border border-slate-200 rounded-xl px-4 py-3 shadow-sm min-w-[140px]">
      <div className="text-xs font-bold text-slate-700">Day {data.dayNumber}</div>
      <div className="text-[10px] text-slate-400">{data.date}</div>
      <div className="text-[10px] text-emerald-600 font-semibold mt-0.5">
        {data.totalEmissions ? `${Number(data.totalEmissions).toFixed(1)} kg` : "0 kg"}
      </div>
      {data.onAddActivity && (
        <button
          onClick={() => data.onAddActivity(id)}
          className="mt-2 w-full flex items-center justify-center gap-1 text-[10px] bg-slate-50 hover:bg-emerald-50 text-slate-500 hover:text-emerald-600 py-1 rounded transition"
        >
          <Plus weight="bold" className="w-3 h-3" /> Activity
        </button>
      )}
      <Handle type="target" position={Position.Top} className="!bg-slate-300" />
      <Handle type="source" position={Position.Bottom} className="!bg-slate-300" />
    </div>
  );
}
