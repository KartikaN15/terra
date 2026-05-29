import { useState } from "react";
import { api, type Production } from "../api";
import { X, Plus, CalendarPlus } from "@phosphor-icons/react";
import { useNavigate } from "react-router-dom";

const STATUS_OPTIONS = [
  "DEVELOPMENT",
  "PRE_PRODUCTION",
  "PRODUCTION",
  "POST_PRODUCTION",
  "DISTRIBUTION",
  "COMPLETED",
];

const GENRE_OPTIONS = [
  "ACTION", "COMEDY", "DRAMA", "HORROR", "REALITY", "ANIMATION",
  "DOCUMENTARY", "SCI_FI", "CRIME", "WESTERN", "ROMANCE", "THRILLER",
];

const BUDGET_OPTIONS = [
  "UNDER_1M", "_1M_TO_5M", "_5M_TO_10M", "_10M_TO_50M", "OVER_50M",
];

const VFX_OPTIONS = ["NONE", "LOW", "MEDIUM", "HIGH", "EXTREME"];

interface Props {
  onClose: () => void;
  onCreated: (prod: Production) => void;
}

export default function NewProductionModal({ onClose, onCreated }: Props) {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    title: "",
    type: "FEATURE",
    genre: "DRAMA",
    budget_band: "_1M_TO_5M",
    runtime_min: 90,
    episodes: 1,
    shoot_days: 30,
    locations: "",
    cast_count: 8,
    crew_count: 45,
    vfx_intensity: "LOW",
    status: "DEVELOPMENT",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (field: string, value: string | number) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleDesignerPlan = async () => {
    setLoading(true);
    setError("");
    try {
      const payload = {
        ...form,
        locations: form.locations
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        runtime_min: Number(form.runtime_min) || undefined,
        episodes: Number(form.episodes) || 1,
        shoot_days: Number(form.shoot_days) || undefined,
        cast_count: Number(form.cast_count) || undefined,
        crew_count: Number(form.crew_count) || undefined,
      };
      const prod = await api.createProduction(payload);
      navigate("/productions/new/designer", { state: { initialForm: prod } });
    } catch (err: any) {
      setError(err.message || "Failed to create production");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const payload = {
        ...form,
        locations: form.locations
          .split(",")
          .map((s) => s.trim())
          .filter(Boolean),
        runtime_min: Number(form.runtime_min) || undefined,
        episodes: Number(form.episodes) || 1,
        shoot_days: Number(form.shoot_days) || undefined,
        cast_count: Number(form.cast_count) || undefined,
        crew_count: Number(form.crew_count) || undefined,
      };
      const prod = await api.createProduction(payload);
      onCreated(prod);
      onClose();
    } catch (err: any) {
      setError(err.message || "Failed to create production");
    } finally {
      setLoading(false);
    }
  };

  const inputCls =
    "w-full bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 focus:bg-white focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 outline-none transition";

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between sticky top-0 bg-white/95 backdrop-blur">
          <h3 className="font-semibold text-slate-800">New Production</h3>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400 hover:text-slate-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {error && (
            <div className="text-red-700 bg-red-50 border border-red-100 text-sm p-3 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
              Title *
            </label>
            <input
              required
              value={form.title}
              onChange={(e) => handleChange("title", e.target.value)}
              className={inputCls}
              placeholder="e.g. The Midnight Heist"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Type
              </label>
              <select
                value={form.type}
                onChange={(e) => handleChange("type", e.target.value)}
                className={inputCls}
              >
                <option value="FEATURE">Film</option>
                <option value="TV_SERIES">Series</option>
                <option value="MINI_SERIES">Mini-series</option>
                <option value="DOCUMENTARY">Documentary</option>
                <option value="COMMERCIAL">Commercial</option>
                <option value="SHORT">Short film</option>
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Genre
              </label>
              <select
                value={form.genre}
                onChange={(e) => handleChange("genre", e.target.value)}
                className={inputCls}
              >
                {GENRE_OPTIONS.map((g) => (
                  <option key={g} value={g}>
                    {g.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Budget Band
              </label>
              <select
                value={form.budget_band}
                onChange={(e) => handleChange("budget_band", e.target.value)}
                className={inputCls}
              >
                {BUDGET_OPTIONS.map((b) => (
                  <option key={b} value={b}>
                    {b.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Status
              </label>
              <select
                value={form.status}
                onChange={(e) => handleChange("status", e.target.value)}
                className={inputCls}
              >
                {STATUS_OPTIONS.map((s) => (
                  <option key={s} value={s}>
                    {s.replace(/_/g, " ")}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Shoot Days
              </label>
              <input
                type="number"
                min={1}
                value={form.shoot_days}
                onChange={(e) => handleChange("shoot_days", Number(e.target.value))}
                className={inputCls}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Runtime (min)
              </label>
              <input
                type="number"
                min={1}
                value={form.runtime_min}
                onChange={(e) => handleChange("runtime_min", Number(e.target.value))}
                className={inputCls}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Episodes
              </label>
              <input
                type="number"
                min={1}
                value={form.episodes}
                onChange={(e) => handleChange("episodes", Number(e.target.value))}
                className={inputCls}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Cast Count
              </label>
              <input
                type="number"
                min={0}
                value={form.cast_count}
                onChange={(e) => handleChange("cast_count", Number(e.target.value))}
                className={inputCls}
              />
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Crew Count
              </label>
              <input
                type="number"
                min={0}
                value={form.crew_count}
                onChange={(e) => handleChange("crew_count", Number(e.target.value))}
                className={inputCls}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                VFX Intensity
              </label>
              <select
                value={form.vfx_intensity}
                onChange={(e) => handleChange("vfx_intensity", e.target.value)}
                className={inputCls}
              >
                {VFX_OPTIONS.map((v) => (
                  <option key={v} value={v}>
                    {v}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-xs font-semibold text-slate-600 mb-1.5 uppercase tracking-wider">
                Locations
              </label>
              <input
                value={form.locations}
                onChange={(e) => handleChange("locations", e.target.value)}
                className={inputCls}
                placeholder="London, Prague"
              />
            </div>
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
              type="button"
              onClick={handleDesignerPlan}
              disabled={loading || !form.title.trim()}
              className="px-4 py-2.5 rounded-lg text-sm font-medium text-emerald-700 bg-emerald-50 hover:bg-emerald-100 border border-emerald-100 inline-flex items-center gap-2 disabled:opacity-40"
            >
              {loading ? (
                <span className="w-4 h-4 border-2 border-emerald-600/30 border-t-emerald-600 rounded-full animate-spin" />
              ) : (
                <CalendarPlus weight="bold" className="w-4 h-4" />
              )}
              Plan in Visual Designer
            </button>
            <button
              type="submit"
              disabled={loading || !form.title.trim()}
              className="px-5 py-2.5 rounded-lg text-sm font-semibold text-white bg-emerald-600 hover:bg-emerald-700 disabled:opacity-40 inline-flex items-center gap-2 shadow-sm shadow-emerald-200"
            >
              {loading ? (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <Plus weight="bold" className="w-4 h-4" />
              )}
              Create Production
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
