import { Handle, Position } from "@xyflow/react";

export default function ProductionNode({ data }: any) {
  return (
    <div className="bg-emerald-600 text-white rounded-xl px-5 py-3 shadow-lg min-w-[180px]">
      <div className="text-sm font-bold">{data.title || "Untitled"}</div>
      <div className="text-[10px] opacity-80 mt-0.5">
        {data.type} · {data.shoot_days || 0} days · {data.episodes || 1} ep
      </div>
      <Handle type="source" position={Position.Bottom} className="!bg-emerald-400" />
    </div>
  );
}
