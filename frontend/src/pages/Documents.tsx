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

  const loadDocs = async (pid: string) => {
    try {
      const data = await api.getDocuments(pid);
      setDocs(data);
    } catch (e: any) {
      setError(e.message);
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
      await loadDocs(selectedId);
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
          {docs.map((doc) => (
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
                    <div className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-2">
                      Extracted items
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
