import { useState } from "react";
import { api, type ActivityEvent } from "../api";
import { X, Plus } from "@phosphor-icons/react";

const PHASE_OPTIONS = [
  "DEVELOPMENT",
  "PRE_PRODUCTION",
  "PRODUCTION",
  "POST_PRODUCTION",
  "DISTRIBUTION",
];

const CATEGORY_OPTIONS = [
  "ENERGY",
  "TRANSPORT",
  "ACCOMMODATION",
  "MATERIALS",
  "WASTE",
  "WATER",
  "CATERING",
  "POST_VFX",
];

const UNIT_OPTIONS = [
  "LITRES", "KWH", "KM", "MILES", "KG", "HOURS", "GBP", "USD", "TONNES", "M3", "NIGHTS",
];

const SOURCE_OPTIONS = [
  "MANUAL_ENTRY", "CSV_UPLOAD", "IOT_STREAM", "INVOICE_OCR", "API_INTEGRATION", "BENCHMARK",
];

// Simple scope mapping helper for UX
function guessScope(subcategory: string): string {
  const s = subcategory.toLowerCase();
  if (s.includes("diesel") || s.includes("petrol") || s.includes("gas") || s.includes("hvo") || s.includes("propane")) return "SCOPE_1";
  if (s.includes("grid_electricity") || s.includes("purchased_heat") || s.includes("purchased_steam")) return "SCOPE_2";
  return "SCOPE_3";
}

interface Props {
  productionId: string;
  onClose: () => void;
  onCreated: (event: ActivityEvent) => void;
}

export default function AddEventModal({ productionId, onClose, onCreated }: Props) {
  const [form, setForm] = useState({
    phase: "PRODUCTION",
    category: "ENERGY",
    subcategory: "diesel_generator",
    value: "",
    unit: "LITRES",
    source_type: "MANUAL_ENTRY",
    source_reference: "",
    grid_region: "UK",
    recorded_at: new Date().toISOString().slice(0, 16),
    notes: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const scope = guessScope(form.subcategory);
      const payload = {
        production_id: productionId,
        phase: form.phase,
        scope,
        category: form.category,
        subcategory: form.subcategory,
        value: Number(form.value),
        unit: form.unit,
        source_type: form.source_type,
        source_reference: form.source_reference || undefined,
        grid_region: form.grid_region || undefined,
        recorded_at: new Date(form.recorded_at).toISOString(),
        recorded_by: "00000000-0000-0000-0000-000000000001",
        notes: form.notes || undefined,
      };
      const evt = await api.createEvent(payload);
      onCreated(evt);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to log event");
    } finally {
      setLoading(false);
    }
  };

  const inputCls =
    "w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 focus:bg-white focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 outline-none transition";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between sticky top-0 bg-white/95 backdrop-blur">
          <h3 className="font-semibold text-slate-800">Log Activity / Bill</h3>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="text-red-700 bg-red-50 border border-red-100 text-sm p-3 rounded-lg">
              {error}
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Phase
              </label>
              <select
                value={form.phase}
                onChange={(e) => handleChange("phase", e.target.value)}
                className={inputCls}
              >
                {PHASE_OPTIONS.map((p) => (
                  <option key={p} value={p}>{p.replace(/_/g, " ")}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Category
              </label>
              <select
                value={form.category}
                onChange={(e) => handleChange("category", e.target.value)}
                className={inputCls}
              >
                {CATEGORY_OPTIONS.map((c) => (
                  <option key={c} value={c}>{c.replace(/_/g, " ")}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
              Subcategory
            </label>
            <input
              required
              value={form.subcategory}
              onChange={(e) => handleChange("subcategory", e.target.value)}
              className={inputCls}
              placeholder="e.g. diesel_generator, short_haul_flight, hotel"
            />
            <p className="text-[11px] text-slate-400 mt-1">
              This determines the emission factor and auto-scope.
            </p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Value *
              </label>
              <input
                required
                type="number"
                step="any"
                min={0}
                value={form.value}
                onChange={(e) => handleChange("value", e.target.value)}
                className={inputCls}
                placeholder="150.5"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Unit
              </label>
              <select
                value={form.unit}
                onChange={(e) => handleChange("unit", e.target.value)}
                className={inputCls}
              >
                {UNIT_OPTIONS.map((u) => (
                  <option key={u} value={u}>{u}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Source Type
              </label>
              <select
                value={form.source_type}
                onChange={(e) => handleChange("source_type", e.target.value)}
                className={inputCls}
              >
                {SOURCE_OPTIONS.map((s) => (
                  <option key={s} value={s}>{s.replace(/_/g, " ")}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Source Reference
              </label>
              <input
                value={form.source_reference}
                onChange={(e) => handleChange("source_reference", e.target.value)}
                className={inputCls}
                placeholder="Invoice #001"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Grid Region
              </label>
              <input
                value={form.grid_region}
                onChange={(e) => handleChange("grid_region", e.target.value)}
                className={inputCls}
                placeholder="UK"
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Recorded At *
              </label>
              <input
                required
                type="datetime-local"
                value={form.recorded_at}
                onChange={(e) => handleChange("recorded_at", e.target.value)}
                className={inputCls}
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
              Notes
            </label>
            <textarea
              rows={2}
              value={form.notes}
              onChange={(e) => handleChange("notes", e.target.value)}
              className={inputCls}
              placeholder="Optional context..."
            />
          </div>

          <div className="pt-2 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2.5 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 border border-slate-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !form.value || !form.subcategory}
              className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 inline-flex items-center gap-2"
            >
              {loading ? (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Plus weight="bold" className="w-4 h-4" />
              )}
              Log Event
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
