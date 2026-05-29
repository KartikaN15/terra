import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import { Lightning, WarningCircle, ArrowClockwise } from "@phosphor-icons/react";
import { useToast } from "../contexts/ToastContext";
import anomalyDetective from "../assets/illustrations/anomaly-detective.png";

interface AnomalyItem {
  timestamp: string;
  observed_kgco2e: number;
  expected_kgco2e: number;
  deviation_percent: number;
  severity: string;
  reason: string;
  z_score: number | null;
}

interface DetectResponse {
  project_id: string;
  anomalies: AnomalyItem[];
  window_days: number;
}

export default function Anomalies() {
  const [searchParams] = useSearchParams();
  const productionId = searchParams.get("production") || "";
  const [anomalies, setAnomalies] = useState<AnomalyItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const toast = useToast();

  const detect = async () => {
    if (!productionId) {
      setError("Select a production to analyse");
      return;
    }
    setLoading(true);
    setError("");
    try {
      // Fetch events and build time series
      const events = await api.getEvents(productionId, 0, 500);
      const daily: Record<string, number> = {};
      events.forEach((e) => {
        const day = e.recorded_at.split("T")[0];
        daily[day] = (daily[day] || 0) + Number(e.kgco2e);
      });
      const timeSeries = Object.entries(daily)
        .sort(([a], [b]) => a.localeCompare(b))
        .map(([timestamp, kgco2e]) => ({ timestamp, kgco2e }));

      if (timeSeries.length < 14) {
        setError(
          `Need at least 14 days of activity data to run anomaly detection. Only ${timeSeries.length} days found. Log more events and try again.`
        );
        setLoading(false);
        return;
      }

      const data: DetectResponse = await api.detectAnomalies({
        project_id: productionId,
        time_series: timeSeries,
        window_days: 7,
        sensitivity: 0.05,
      });
      setAnomalies(data.anomalies);
      if (data.anomalies.length === 0) {
        toast.success("No anomalies found", "Your production emissions look consistent.");
      } else {
        toast.success(`${data.anomalies.length} anomalies detected`, "Review the flagged days below.");
      }
    } catch (err: any) {
      setError(err.message || "Failed to run anomaly detection");
      toast.error("Detection failed", err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="terra-hero p-6 relative overflow-hidden">
        <div className="relative z-10 max-w-md">
          <div className="inline-flex items-center gap-2 bg-white/15 backdrop-blur px-3 py-1 rounded-full text-xs font-medium">
            <Lightning weight="fill" className="w-3 h-3" /> ML Powered
          </div>
          <h1 className="text-2xl font-bold mt-3">Anomaly Detection</h1>
          <p className="text-sm text-white/80 mt-1">
            Spot unusual emission spikes across your production timeline.
          </p>
        </div>
        <img src={anomalyDetective} alt="" className="absolute right-4 bottom-0 w-32 illus-shadow-soft" />
      </div>

      <div className="terra-card p-5">
        <div className="flex items-center gap-3 mb-4">
          <button
            onClick={detect}
            disabled={loading}
            className="inline-flex items-center gap-2 bg-emerald-600 text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50"
          >
            {loading ? (
              <ArrowClockwise className="animate-spin w-4 h-4" />
            ) : (
              <Lightning weight="fill" className="w-4 h-4" />
            )}
            Run Detection
          </button>
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-amber-50 text-amber-700 text-sm flex items-start gap-2">
            <WarningCircle weight="fill" className="w-4 h-4 shrink-0 mt-0.5" />
            {error}
          </div>
        )}

        {anomalies.length > 0 && (
          <div className="space-y-2 mt-4">
            <h3 className="text-sm font-semibold text-slate-700">Flagged anomalies</h3>
            {anomalies.map((a, idx) => (
              <div
                key={idx}
                className={`p-3 rounded-lg border flex items-center justify-between ${
                  a.severity === "HIGH"
                    ? "bg-rose-50 border-rose-100"
                    : a.severity === "MEDIUM"
                    ? "bg-amber-50 border-amber-100"
                    : "bg-slate-50 border-slate-100"
                }`}
              >
                <div>
                  <div className="text-xs font-bold text-slate-700">{a.timestamp}</div>
                  <div className="text-[11px] text-slate-500">
                    Observed: {a.observed_kgco2e.toFixed(0)} kg · Expected: {a.expected_kgco2e.toFixed(0)} kg
                  </div>
                  {a.reason && <div className="text-[11px] text-slate-400 mt-0.5">{a.reason}</div>}
                </div>
                <div className="text-right">
                  <div className={`text-sm font-bold ${a.deviation_percent > 0 ? "text-rose-600" : "text-emerald-600"}`}>
                    {a.deviation_percent > 0 ? "+" : ""}
                    {a.deviation_percent.toFixed(0)}%
                  </div>
                  {a.z_score !== null && (
                    <span className="ml-2 text-[10px] text-slate-400">(z = {a.z_score})</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {!error && anomalies.length === 0 && !loading && (
          <div className="text-sm text-slate-400 py-8 text-center">
            Run detection to see results.
          </div>
        )}
      </div>

      {!productionId && (
        <div className="text-sm text-slate-400 text-center py-4">
          Anomaly detection requires at least 14 days of logged activity data.
        </div>
      )}
    </div>
  );
}
