import { useEffect, useState, useRef } from "react";
import { api, type Production } from "../api";
import {
  CircleNotch as Loader2,
  UploadSimple,
  FileText,
  CheckCircle,
  XCircle,
  WarningCircle,
  Lightning,
  CaretDown,
  FileCsv,
  FileImage,
  FilePdf,
  ArrowRight,
} from "@phosphor-icons/react";
import emptySprout from "../assets/illustrations/empty-sprout.png";

interface DocItem {
  doc_id: string;
  production_id: string;
  doc_type: string;
  filename: string;
  ocr_status: string;
  review_status: string;
  extracted_confidence: number | null;
  extracted_data: any;
  uploaded_at: string;
  linked_event_ids: string[] | null;
}

const DOC_TYPE_LABELS: Record<string, string> = {
  FUEL_RECEIPT: "Fuel Receipt",
  ELECTRICITY_BILL: "Electricity Bill",
  TRAVEL_MANIFEST: "Travel Manifest",
  CATERING_INVOICE: "Catering Invoice",
  WASTE_TICKET: "Waste Ticket",
  HOTEL_INVOICE: "Hotel Invoice",
  EPD: "EPD",
  OTHER: "Other",
};

const STATUS_STYLES: Record<string, string> = {
  PENDING: "bg-slate-100 text-slate-600",
  EXTRACTED: "bg-blue-50 text-blue-700",
  REVIEW_REQUIRED: "bg-amber-50 text-amber-700",
  APPROVED: "bg-emerald-50 text-emerald-700",
  REJECTED: "bg-red-50 text-red-700",
};

function DocIcon({ mimeType, className }: { mimeType?: string; className?: string }) {
  if (mimeType?.includes("pdf")) return <FilePdf className={className} />;
  if (mimeType?.includes("image")) return <FileImage className={className} />;
  if (mimeType?.includes("csv")) return <FileCsv className={className} />;
  return <FileText className={className} />;
}

// ---------------------------------------------------------------------------
// Synthetic OCR extraction (frontend-only demo)
// ---------------------------------------------------------------------------
// The backend OCR is a stub that returns no items. Until it's wired up, we
// synthesize realistic extracted activity items on the client so the upload →
// extract → review flow demos end-to-end. Values are seeded from the doc id so
// they're stable across reloads (a given document always "extracts" the same).

interface SynthItemSpec {
  category: string;
  subcategory: string;
  unit: string;
  min: number;
  max: number;
}

const SYNTH_TEMPLATES: Record<string, { confidence: [number, number]; items: SynthItemSpec[] }> = {
  FUEL_RECEIPT: {
    confidence: [0.88, 0.96],
    items: [{ category: "ENERGY", subcategory: "diesel_generator", unit: "LITRES", min: 120, max: 680 }],
  },
  ELECTRICITY_BILL: {
    confidence: [0.9, 0.97],
    items: [{ category: "ENERGY", subcategory: "grid_electricity", unit: "KWH", min: 800, max: 5200 }],
  },
  TRAVEL_MANIFEST: {
    confidence: [0.82, 0.93],
    items: [
      { category: "TRANSPORT", subcategory: "short_haul_flight", unit: "KM", min: 450, max: 1500 },
      { category: "TRANSPORT", subcategory: "medium_car_diesel", unit: "KM", min: 60, max: 420 },
    ],
  },
  CATERING_INVOICE: {
    confidence: [0.84, 0.94],
    items: [{ category: "CATERING", subcategory: "meals_mixed", unit: "MEALS", min: 30, max: 220 }],
  },
  WASTE_TICKET: {
    confidence: [0.85, 0.95],
    items: [
      { category: "WASTE", subcategory: "landfill_general", unit: "KG", min: 80, max: 900 },
      { category: "WASTE", subcategory: "recycling_mixed", unit: "KG", min: 40, max: 500 },
    ],
  },
  HOTEL_INVOICE: {
    confidence: [0.87, 0.95],
    items: [{ category: "ACCOMMODATION", subcategory: "hotel_night", unit: "NIGHTS", min: 4, max: 40 }],
  },
};

// Fallback rotation for documents that don't match a known type (so OTHER docs
// still demo a plausible extraction rather than coming up empty).
const SYNTH_FALLBACK_TYPES = ["FUEL_RECEIPT", "ELECTRICITY_BILL", "WASTE_TICKET"];

function seedFrom(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function makeRng(seed: number): () => number {
  let x = seed || 1;
  return () => {
    x = (Math.imul(x, 1103515245) + 12345) & 0x7fffffff;
    return x / 0x7fffffff;
  };
}

function syntheticExtraction(doc: DocItem): { doc_type: string; confidence: number; items: any[] } {
  const rng = makeRng(seedFrom(doc.doc_id || doc.filename));
  let effectiveType = doc.doc_type && doc.doc_type !== "OTHER" ? doc.doc_type : guessDocType(doc.filename);
  if (!SYNTH_TEMPLATES[effectiveType]) {
    effectiveType = SYNTH_FALLBACK_TYPES[seedFrom(doc.doc_id || doc.filename) % SYNTH_FALLBACK_TYPES.length];
  }
  const tpl = SYNTH_TEMPLATES[effectiveType];
  const [lo, hi] = tpl.confidence;
  const confidence = +(lo + rng() * (hi - lo)).toFixed(2);

  // Include the first item always; include optional extra items ~50% of the time.
  const items = tpl.items
    .filter((_, idx) => idx === 0 || rng() > 0.5)
    .map((spec) => ({
      category: spec.category,
      subcategory: spec.subcategory,
      unit: spec.unit,
      value: Math.round(spec.min + rng() * (spec.max - spec.min)),
    }));

  return { doc_type: effectiveType, confidence, items };
}

// Overlay synthetic extraction onto a document that has no real extracted items.
function withSynthetic(doc: DocItem): DocItem {
  if (doc.extracted_data?.items?.length > 0) return doc;
  const synth = syntheticExtraction(doc);
  return {
    ...doc,
    doc_type: doc.doc_type && doc.doc_type !== "OTHER" ? doc.doc_type : synth.doc_type,
    ocr_status: "EXTRACTED",
    extracted_confidence: synth.confidence,
    extracted_data: { items: synth.items, synthetic: true },
  };
}

export default function Documents() {
  const [productions, setProductions] = useState<Production[]>([]);
  const [selectedId, setSelectedId] = useState<string>("");
  const [docs, setDocs] = useState<DocItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [expandedDoc, setExpandedDoc] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    api.getProductions().then(setProductions).catch(() => {}).finally(() => setLoading(false));
  }, []);

  const loadDocs = async (pid: string): Promise<DocItem[]> => {
    try {
      const data = await api.getDocuments(pid);
      setDocs(data);
      return data;
    } catch (e: any) {
      setError(e.message);
      return [];
    }
  };

  const handleSelect = (pid: string) => {
    setSelectedId(pid);
    setDocs([]);
    setError("");
    if (pid) loadDocs(pid);
  };

  const handleFile = async (file: File) => {
    if (!selectedId) return;
    setUploading(true);
    setError("");
    try {
      const guessedType = guessDocType(file.name);
      await api.uploadDocument(selectedId, guessedType, file);
      const data = await loadDocs(selectedId);
      // Auto-expand the freshly uploaded doc so the (synthetic) extraction is
      // visible immediately, mirroring a real OCR result.
      const newest = [...data].sort((a, b) => b.uploaded_at.localeCompare(a.uploaded_at))[0];
      if (newest) setExpandedDoc(newest.doc_id);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setUploading(false);
    }
  };

  const extractDoc = async (docId: string) => {
    setError("");
    try {
      await api.extractDocument(docId);
      await loadDocs(selectedId);
      setExpandedDoc(docId);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const approveDoc = async (docId: string) => {
    setError("");
    try {
      await api.approveDocument(docId);
      await loadDocs(selectedId);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const rejectDoc = async (docId: string) => {
    setError("");
    try {
      await api.rejectDocument(docId);
      await loadDocs(selectedId);
    } catch (e: any) {
      setError(e.message);
    }
  };

  const selectedProd = productions.find((p) => p.production_id === selectedId);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="terra-card p-6">
        <h2 className="text-lg font-semibold text-slate-900">Document Upload & OCR</h2>
        <p className="mt-1 text-sm text-slate-500">
          Upload fuel receipts, electricity bills, travel manifests, and more. Terra
          extracts structured data and suggests activity events for your approval.
        </p>
      </div>

      {/* Production selector */}
      <div className="terra-card p-5">
        <label className="block text-xs font-semibold text-slate-600 mb-2 uppercase tracking-wider">
          Production
        </label>
        {loading ? (
          <Loader2 className="animate-spin w-4 h-4 text-emerald-500" />
        ) : (
          <select
            value={selectedId}
            onChange={(e) => handleSelect(e.target.value)}
            className="w-full max-w-md bg-slate-50 border border-slate-200 rounded-lg px-3 py-2.5 text-sm text-slate-800 focus:bg-white focus:border-emerald-400 focus:ring-2 focus:ring-emerald-100 outline-none transition"
          >
            <option value="">  — Select a production —</option>
            {productions.map((p) => (
              <option key={p.production_id} value={p.production_id}>
                {p.title}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* Upload zone */}
      {selectedId && (
        <div
          onClick={() => fileRef.current?.click()}
          onDragOver={(e) => e.preventDefault()}
          onDrop={(e) => {
            e.preventDefault();
            const f = e.dataTransfer.files?.[0];
            if (f) handleFile(f);
          }}
          className="terra-card p-8 text-center border-2 border-dashed border-emerald-200/60 bg-gradient-to-br from-emerald-50/40 to-transparent cursor-pointer hover:border-emerald-400 transition"
        >
          <UploadSimple weight="duotone" className="w-10 h-10 text-emerald-500 mx-auto" />
          <div className="mt-3 font-semibold text-slate-700 text-sm">
            {uploading ? "Uploading…" : "Drop a document here or click to browse"}
          </div>
          <div className="text-xs text-slate-500 mt-1">
            PDF, CSV, TXT, images   — up to 10 MB
          </div>
          <input
            ref={fileRef}
            type="file"
            className="hidden"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) handleFile(f);
            }}
          />
        </div>
      )}

      {error && (
        <div className="flex items-start gap-2 text-red-700 bg-red-50 border border-red-100 p-3 rounded-lg text-sm">
          <WarningCircle weight="duotone" className="w-5 h-5 mt-0.5 shrink-0" />
          {error}
        </div>
      )}

      {/* Document list */}
      {selectedId && docs.length > 0 && (
        <div className="space-y-3">
          {docs.map(withSynthetic).map((doc) => (
            <div
              key={doc.doc_id}
              className="terra-card overflow-hidden"
            >
              <div className="px-5 py-4 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center">
                    <DocIcon mimeType={doc.filename} className="w-5 h-5 text-emerald-600" />
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-800">{doc.filename}</div>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                        {DOC_TYPE_LABELS[doc.doc_type] || doc.doc_type}
                      </span>
                      <span
                        className={`text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded ${
                          STATUS_STYLES[doc.review_status] || STATUS_STYLES[doc.ocr_status]
                        }`}
                      >
                        {doc.review_status}
                      </span>
                      {doc.extracted_confidence !== null && (
                        <span className="text-[10px] text-slate-400">
                          {Math.round(doc.extracted_confidence * 100)}% confidence
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {doc.ocr_status === "PENDING" && (
                    <button
                      onClick={() => extractDoc(doc.doc_id)}
                      className="inline-flex items-center gap-1 bg-blue-600 text-white px-3 py-1.5 rounded-lg text-xs font-semibold hover:bg-blue-700"
                    >
                      <Lightning weight="fill" className="w-3 h-3" /> Extract
                    </button>
                  )}
                  {(doc.ocr_status === "EXTRACTED" || doc.ocr_status === "REVIEW_REQUIRED") &&
                    doc.review_status === "PENDING" && (
                      <>
                        <button
                          onClick={() => approveDoc(doc.doc_id)}
                          className="inline-flex items-center gap-1 bg-emerald-600 text-white px-3 py-1.5 rounded-lg text-xs font-semibold hover:bg-emerald-700"
                        >
                          <CheckCircle weight="fill" className="w-3 h-3" /> Approve
                        </button>
                        <button
                          onClick={() => rejectDoc(doc.doc_id)}
                          className="inline-flex items-center gap-1 bg-white text-slate-600 border border-slate-200 px-3 py-1.5 rounded-lg text-xs font-semibold hover:bg-slate-50"
                        >
                          <XCircle className="w-3 h-3" /> Reject
                        </button>
                      </>
                    )}
                  {doc.extracted_data && (
                    <button
                      onClick={() => setExpandedDoc(expandedDoc === doc.doc_id ? null : doc.doc_id)}
                      className="p-1.5 rounded-lg hover:bg-slate-100 text-slate-400"
                    >
                      <CaretDown
                        className={`w-4 h-4 transition-transform ${expandedDoc === doc.doc_id ? "rotate-180" : ""}`}
                      />
                    </button>
                  )}
                </div>
              </div>

              {/* Expanded extraction details */}
              {expandedDoc === doc.doc_id && doc.extracted_data && (
                <div className="px-5 pb-4 border-t border-slate-100">
                  <div className="mt-3">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                        Extracted items
                      </div>
                      {doc.extracted_data.synthetic && (
                        <span className="text-[9px] font-semibold uppercase tracking-wider text-amber-700 bg-amber-50 border border-amber-100 px-1.5 py-0.5 rounded">
                          demo data
                        </span>
                      )}
                    </div>
                    {doc.extracted_data.items?.length > 0 ? (
                      <div className="space-y-2">
                        {doc.extracted_data.items.map((item: any, idx: number) => (
                          <div
                            key={idx}
                            className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-100"
                          >
                            <div className="flex items-center gap-3">
                              <span className="text-xs font-bold uppercase text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">
                                {item.category}
                              </span>
                              <span className="text-sm text-slate-700">
                                {item.subcategory.replace(/_/g, " ")}
                              </span>
                              <span className="text-xs text-slate-500">
                                {item.value} {item.unit}
                              </span>
                            </div>
                            <ArrowRight className="w-3 h-3 text-slate-300" />
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-sm text-slate-500">
                        No items extracted. Try a different document or manual entry.
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {selectedId && docs.length === 0 && !uploading && (
        <div className="terra-card p-10 text-center border-2 border-dashed border-emerald-200/60 bg-gradient-to-br from-emerald-50/40 to-transparent">
          <img src={emptySprout} alt="" className="w-40 h-40 mx-auto object-contain illus-shadow" />
          <div className="mt-4 font-semibold text-slate-700 text-sm">
            No documents yet for {selectedProd?.title}
          </div>
          <div className="text-xs text-slate-500 mt-1 max-w-xs mx-auto">
            Upload fuel receipts, electricity bills, or travel manifests to extract
            activity events automatically.
          </div>
        </div>
      )}
    </div>
  );
}

function guessDocType(filename: string): string {
  const f = filename.toLowerCase();
  if (f.includes("fuel") || f.includes("diesel") || f.includes("hvo") || f.includes("petrol")) return "FUEL_RECEIPT";
  if (f.includes("electric") || f.includes("bill") || f.includes("kwh")) return "ELECTRICITY_BILL";
  if (f.includes("travel") || f.includes("flight") || f.includes("manifest")) return "TRAVEL_MANIFEST";
  if (f.includes("cater") || f.includes("food") || f.includes("menu")) return "CATERING_INVOICE";
  if (f.includes("waste") || f.includes("recycling") || f.includes("landfill")) return "WASTE_TICKET";
  if (f.includes("hotel") || f.includes("accommodation")) return "HOTEL_INVOICE";
  return "OTHER";
}
