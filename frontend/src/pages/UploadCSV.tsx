import { useState, useRef } from "react";
import { api } from "../api";
import { useToast } from "../contexts/ToastContext";
import {
  CheckCircle,
  CircleNotch as Loader2,
  FileCsv,
  Info,
  X,
} from "@phosphor-icons/react";
import courier from "../assets/illustrations/upload-courier.png";
import sprout from "../assets/illustrations/empty-sprout.png";

export default function UploadCSV() {
  const [file, setFile] = useState<File | null>(null);
  const [dragging, setDragging] = useState(false);
  const [result, setResult] = useState<{
    filename: string;
    total_rows: number;
    created: number;
    errors: any[];
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const toast = useToast();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) { toast.warning("No file selected", "Choose a CSV file to upload."); return; }
    setLoading(true);
    setResult(null);
    try {
      const res = await api.uploadCSV(file);
      setResult(res);
      if (res.errors?.length > 0) {
        toast.warning(`Imported with ${res.errors.length} row error${res.errors.length > 1 ? "s" : ""}`, `${res.created} of ${res.total_rows} rows imported.`);
      } else {
        toast.success("Import complete", `${res.created} activity events created.`);
      }
    } catch (err: any) {
      toast.error("Upload failed", err.message || "Could not import the file.");
    } finally {
      setLoading(false);
    }
  };

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files?.[0];
    if (f) setFile(f);
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Drop zone */}
        <form
          onSubmit={handleSubmit}
          className="lg:col-span-2 terra-card p-6 space-y-5"
        >
          <div
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => {
              e.preventDefault();
              setDragging(true);
            }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            className={`relative border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all ${
              dragging
                ? "border-emerald-500 bg-emerald-50 scale-[1.01]"
                : file
                ? "border-emerald-400 bg-emerald-50/60"
                : "border-slate-300 bg-slate-50/40 hover:border-emerald-300 hover:bg-emerald-50/30"
            }`}
          >
            <div className="flex flex-col items-center gap-3">
              {file ? (
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                  <FileCsv weight="duotone" className="w-8 h-8 text-white" />
                </div>
              ) : (
                <img
                  src={courier}
                  alt=""
                  className="w-48 h-36 object-contain illus-shadow select-none"
                />
              )}
              {file ? (
                <>
                  <div className="font-semibold text-slate-800">
                    {file.name}
                  </div>
                  <div className="text-xs text-slate-500">
                    {(file.size / 1024).toFixed(1)} KB · ready to import
                  </div>
                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      setFile(null);
                      setResult(null);
                    }}
                    className="mt-1 inline-flex items-center gap-1 text-xs text-slate-500 hover:text-red-600"
                  >
                    <X className="w-3 h-3" /> Remove
                  </button>
                </>
              ) : (
                <>
                  <div className="font-semibold text-slate-800">
                    Drop your CSV here
                  </div>
                  <div className="text-sm text-slate-500">
                    or{" "}
                    <span className="text-emerald-700 font-medium">
                      click to browse
                    </span>{" "}
                      — up to 10 MB
                  </div>
                </>
              )}
            </div>
            <input
              ref={inputRef}
              type="file"
              accept=".csv"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
          </div>

          <button
            type="submit"
            disabled={!file || loading}
            className="w-full bg-emerald-600 text-white py-3 rounded-xl text-sm font-semibold hover:bg-emerald-700 disabled:opacity-40 disabled:cursor-not-allowed inline-flex items-center justify-center gap-2 shadow-sm"
          >
            {loading && <Loader2 className="animate-spin w-4 h-4" />}
            {loading ? "Importing…" : "Import events"}
          </button>

          {result && (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-emerald-700 bg-emerald-50 border border-emerald-100 p-3 rounded-lg text-sm">
                <CheckCircle
                  weight="duotone"
                  className="w-5 h-5 shrink-0"
                />
                <span>
                  Uploaded <strong>{result.filename}</strong>:{" "}
                  <strong>{result.created}</strong> of {result.total_rows} rows
                  created.
                </span>
              </div>
              {result.errors.length > 0 && (
                <div className="terra-card border border-red-100 overflow-hidden">
                  <div className="bg-red-50 px-4 py-2 text-xs font-semibold text-red-800">
                    {result.errors.length} row error
                    {result.errors.length === 1 ? "" : "s"}
                  </div>
                  <ul className="max-h-48 overflow-auto divide-y divide-red-50">
                    {result.errors.map((err, i) => (
                      <li
                        key={i}
                        className="px-4 py-2 text-xs text-red-700 flex gap-2"
                      >
                        <span className="font-mono text-red-400">
                          Row {err.row}
                        </span>
                        <span>{err.message}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </form>

        {/* Sidebar info */}
        <div className="space-y-4">
          <div className="terra-card p-5">
            <div className="flex items-center gap-2 mb-3">
              <Info weight="duotone" className="w-5 h-5 text-emerald-600" />
              <h3 className="font-semibold text-slate-800">Required columns</h3>
            </div>
            <ul className="space-y-1.5 text-xs text-slate-600">
              {[
                "production_id",
                "phase",
                "category",
                "subcategory",
                "value",
                "unit",
                "source_type",
                "recorded_at",
                "recorded_by",
              ].map((c) => (
                <li key={c} className="flex items-center gap-2">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                  <code className="bg-slate-50 px-1.5 py-0.5 rounded font-mono text-[11px] text-slate-700">
                    {c}
                  </code>
                </li>
              ))}
            </ul>
          </div>

          <div className="terra-card p-5 bg-gradient-to-br from-emerald-50 to-amber-50 border border-emerald-100 relative overflow-hidden">
            <img
              src={sprout}
              alt=""
              className="absolute -right-4 -bottom-4 w-28 pointer-events-none select-none illus-shadow-soft"
            />
            <h3 className="relative font-semibold text-emerald-900 text-sm">
              Pro tip 🌱
            </h3>
            <p className="text-xs text-emerald-800/80 mt-1 leading-relaxed">
              Leave <code className="bg-white/60 px-1 rounded">scope</code> and{" "}
              <code className="bg-white/60 px-1 rounded">kgco2e</code> empty —
              Terra's classifier will fill them in and flag low-confidence rows
              for review.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
