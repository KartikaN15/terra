import { Handle, Position } from "@xyflow/react";

export default function MilestoneNode({ data }: any) {
  return (
    <div className="bg-violet-500 text-white rounded-full px-4 py-2 shadow-md text-xs font-bold">
      {data.label || "Milestone"}
      <Handle type="target" position={Position.Top} className="!bg-violet-300" />
      <Handle type="source" position={Position.Bottom} className="!bg-violet-300" />
    </div>
  );
}
