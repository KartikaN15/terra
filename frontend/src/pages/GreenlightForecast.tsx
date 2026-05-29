import { useState } from "react";
import { api, type GreenlightForecast } from "../api";
import { TrendUp, Sparkle } from "@phosphor-icons/react";
import { useToast } from "../contexts/ToastContext";
import crystalBall from "../assets/illustrations/crystal-ball.png";

export default function GreenlightForecast() {
  const [form, setForm] = useState({
    project_type: "FEATURE",
    scale_band: "_1M_TO_5M",
    duration: 30,
    headcount: 50,
    complexity: "LOW",
    output_units: 1,
    output_size: 90,
    region: "UK",
  });
  const [result, setResult] = useState<GreenlightForecast | null>(null);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  const runForecast = async () => {
    setLoading(true);
    try {
      const res = await api.forecastGreenlight(form);
      setResult(res);
      toast.success(
        "Forecast ready",
        `Predicted ${res.predicted_total_tco2e.toFixed(1)} tCO₂e`
      );
    } catch (err: any) {
      toast.error("Forecast failed", err.message || "Could not generate the forecast.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="terra-hero p-6 relative overflow-hidden">
        <div className="relative z-10 max-w-md">
          <div className="inline-flex items-center gap-2 bg-white/15 backdrop-blur px-3 py-1 rounded-full text-xs font-medium">
            <Sparkle weight="fill" className="w-3 h-3" /> ML Powered
          </div>
          <h1 className="text-2xl font-bold mt-3">Greenlight Forecast</h1>
          <p className="text-sm text-white/80 mt-1">
            Predict total emissions before you start shooting.
          </p>
        </div>
        <img src={crystalBall} alt="" className="absolute right-4 bottom-0 w-32 illus-shadow-soft" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 terra-card p-5">
          <h3 className="text-sm font-bold text-slate-800 mb-4">Project details</h3>
          <div className="space-y-3">
            {[
              { label: "Type", key: "project_type", type: "select", options: ["FEATURE", "TV_SERIES", "COMMERCIAL", "DOCUMENTARY"] },
              { label: "Budget band", key: "scale_band", type: "select", options: ["_100K_TO_500K", "_500K_TO_1M", "_1M_TO_5M", "_5M_TO_10M", "_10M_PLUS"] },
              { label: "Duration (days)", key: "duration", type: "number" },
              { label: "Headcount", key: "headcount", type: "number" },
              { label: "VFX complexity", key: "complexity", type: "select", options: ["LOW", "MEDIUM", "HIGH", "EXTREME"] },
              { label: "Output units", key: "output_units", type: "number" },
              { label: "Runtime (min)", key: "output_size", type: "number" },
              { label: "Region", key: "region", type: "select", options: ["UK", "US", "EU", "Global"] },
            ].map((field) => (
              <div key={field.key}>
                <label className="text-xs font-medium text-slate-500">{field.label}</label>
                {field.type === "select" ? (
                  <select
                    className="w-full mt-1 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm"
                    value={(form as any)[field.key]}
                    onChange={(e) => setForm({ ...form, [field.key]: e.target.value })}
                  >
                    {field.options?.map((o) => (
                      <option key={o} value={o}>
                        {o}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type="number"
                    className="w-full mt-1 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm"
                    value={(form as any)[field.key]}
                    onChange={(e) => setForm({ ...form, [field.key]: Number(e.target.value) })}
                  />
                )}
              </div>
            ))}
          </div>
          <button
            onClick={runForecast}
            disabled={loading}
            className="mt-4 w-full bg-emerald-600 text-white py-2.5 rounded-lg text-sm font-semibold hover:bg-emerald-700 disabled:opacity-50 flex items-center justify-center gap-2"
          >
            {loading ? (
              <TrendUp className="animate-spin w-4 h-4" />
            ) : (
              <TrendUp weight="bold" className="w-4 h-4" />
            )}
            {loading ? "Forecasting…" : "Run forecast"}
          </button>
        </div>

        <div className="lg:col-span-2 terra-card p-5">
          {result ? (
            <div className="space-y-4">
              <div className="flex items-center gap-2 mb-2">
                <TrendUp weight="duotone" className="w-5 h-5 text-emerald-600" />
                <h3 className="text-sm font-bold text-slate-800">Forecast result</h3>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-50 rounded-xl p-4 text-center">
                  <div className="text-xs text-slate-400">Predicted total</div>
                  <div className="text-xl font-bold text-slate-800">
                    {result.predicted_total_tco2e.toFixed(1)} tCO₂e
                  </div>
                </div>
                <div className="bg-slate-50 rounded-xl p-4 text-center">
                  <div className="text-xs text-slate-400">Confidence</div>
                  <div className="text-xl font-bold text-slate-800">
                    {(result.confidence * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="bg-slate-50 rounded-xl p-4 text-center">
                  <div className="text-xs text-slate-400">Top driver</div>
                  <div className="text-sm font-bold text-slate-800 truncate">{result.top_driver}</div>
                </div>
              </div>
              <div className="bg-emerald-50 rounded-xl p-4">
                <div className="text-xs text-emerald-700 font-medium mb-1">Prediction interval</div>
                <div className="text-sm text-emerald-800">
                  {result.interval_lower_tco2e.toFixed(1)} — {result.interval_upper_tco2e.toFixed(1)} tCO₂e
                </div>
              </div>
              <div className="text-[10px] text-slate-400">Model: {result.model_version}</div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-400 py-12">
              <img src={crystalBall} alt="" className="w-24 opacity-30 mb-4" />
              <p className="text-sm">Your forecast will appear here</p>
              <p className="text-xs mt-1">
                Fill in the project details and hit <em>Run forecast</em>. We'll
                predict emissions before you shoot.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
