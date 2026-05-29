import { Handle, Position } from "@xyflow/react";

export default function EpisodeNode({ id: _id, data }: { id: string; data: { title?: string; episodeNumber?: number; totalEmissions?: number } }) {
  return (
    <div className="bg-blue-500 text-white rounded-xl px-4 py-2 shadow-md min-w-[140px]">
      <div className="text-xs font-bold">{data.title || `Episode ${data.episodeNumber}`}</div>
      <div className="text-[10px] opacity-80">
        {data.totalEmissions ? `${Number(data.totalEmissions).toFixed(1)} kg` : "0 kg"}
      </div>
      <Handle type="target" position={Position.Top} className="!bg-blue-300" />
      <Handle type="source" position={Position.Bottom} className="!bg-blue-300" />
    </div>
  );
}
