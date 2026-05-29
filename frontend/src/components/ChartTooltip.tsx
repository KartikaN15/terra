interface TooltipPayload {
  name: string;
  value: number;
  color?: string;
}

interface Props {
  active?: boolean;
  payload?: TooltipPayload[];
  label?: string;
  unit?: string;
  formatter?: (v: number) => string;
}

export function ChartTooltip({ active, payload, label, unit = "tCO₂e", formatter }: Props) {
  if (!active || !payload?.length) return null;

  return (
    <div className="terra-card px-3 py-2.5 min-w-[120px] shadow-lg border border-slate-100">
      {label && (
        <div className="text-xs font-semibold text-slate-500 mb-1.5 uppercase tracking-wider">
          {label}
        </div>
      )}
      {payload.map((p, i) => (
        <div key={i} className="flex items-center gap-2">
          <span
            className="w-2 h-2 rounded-full shrink-0"
            style={{ background: p.color ?? "#10b981" }}
          />
          <span className="text-sm font-semibold text-slate-800">
            {formatter ? formatter(p.value) : p.value.toFixed(1)}
            <span className="text-xs text-slate-500 font-normal ml-1">{unit}</span>
          </span>
        </div>
      ))}
    </div>
  );
}

export function PieTooltip({ active, payload }: Props) {
  if (!active || !payload?.length) return null;
  const p = payload[0];
  return (
    <div className="terra-card px-3 py-2 shadow-lg border border-slate-100">
      <div className="flex items-center gap-2">
        <span
          className="w-2 h-2 rounded-full"
          style={{ background: p.color ?? "#10b981" }}
        />
        <span className="text-xs font-semibold text-slate-700">{p.name}</span>
      </div>
      <div className="text-lg font-bold text-slate-900 mt-0.5">
        {p.value}
        <span className="text-xs font-normal text-slate-400 ml-1">%</span>
      </div>
    </div>
  );
}
