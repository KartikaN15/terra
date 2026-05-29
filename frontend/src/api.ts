import type {
  Production,
  ProductionSummary,
  ActivityEvent,
  GreenlightForecast,
  NotificationItem,
  EmissionFactor,
  Document,
  Recommendation,
  MLHealth,
} from "./types";

const API_BASE = "/api/v1";

function getToken() {
  return localStorage.getItem("token");
}

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const token = getToken();
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    let detail: string;
    try {
      const parsed = JSON.parse(text);
      detail = parsed.detail || JSON.stringify(parsed);
    } catch {
      detail = text || `HTTP ${res.status}`;
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

async function fetchFormData<T>(url: string, form: FormData): Promise<T> {
  const token = getToken();
  const res = await fetch(url, {
    method: "POST",
    body: form,
    ...(token ? { headers: { Authorization: `Bearer ${token}` } } : {}),
  });
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    let detail: string;
    try {
      const parsed = JSON.parse(text);
      detail = parsed.detail || JSON.stringify(parsed);
    } catch {
      detail = text || `HTTP ${res.status}`;
    }
    throw new Error(detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  // Productions
  getProductions: () => fetchJSON<Production[]>(`${API_BASE}/productions`),
  getProduction: (id: string) => fetchJSON<Production>(`${API_BASE}/productions/${id}`),
  getSummary: (id: string) => fetchJSON<ProductionSummary>(`${API_BASE}/productions/${id}/summary`),
  createProduction: (data: Partial<Production>) =>
    fetchJSON<Production>(`${API_BASE}/productions`, { method: "POST", body: JSON.stringify(data) }),
  updateProduction: (id: string, data: Partial<Production>) =>
    fetchJSON<Production>(`${API_BASE}/productions/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteProduction: (id: string) =>
    fetchJSON<{ deleted: boolean }>(`${API_BASE}/productions/${id}`, { method: "DELETE" }),
  recalculateAllEvents: (productionId: string) =>
    fetchJSON<{
      production_id: string;
      events_total: number;
      events_updated: number;
      events_unchanged: number;
      events_failed: any[];
      delta_tco2e: number;
    }>(`${API_BASE}/productions/${productionId}/recalculate-all`, { method: "POST" }),
  getRecommendations: (productionId: string) =>
    fetchJSON<{
      production_id: string;
      recommendations: Recommendation[];
      total_potential_saving_tco2e: number;
    }>(`${API_BASE}/productions/${productionId}/recommendations`),
  getPlanner: (productionId: string) =>
    fetchJSON<{ production_id: string; planner_state: any }>(`${API_BASE}/productions/${productionId}/planner`),
  savePlanner: (productionId: string, state: { nodes: any[]; edges: any[]; lastDayId?: string | null }) =>
    fetchJSON<{ production_id: string; saved: boolean; node_count: number; edge_count: number }>(
      `${API_BASE}/productions/${productionId}/planner`,
      { method: "POST", body: JSON.stringify(state) }
    ),
  // Events
  getEvents: (productionId: string, skip = 0, limit = 500) =>
    fetchJSON<ActivityEvent[]>(`${API_BASE}/events/production/${productionId}?skip=${skip}&limit=${limit}`),
  createEvent: (data: Record<string, any>) =>
    fetchJSON<ActivityEvent>(`${API_BASE}/events`, { method: "POST", body: JSON.stringify(data) }),
  updateEvent: (eventId: string, data: Record<string, any>) =>
    fetchJSON<ActivityEvent>(`${API_BASE}/events/${eventId}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteEvent: (eventId: string) =>
    fetchJSON<{ deleted: boolean }>(`${API_BASE}/events/${eventId}`, { method: "DELETE" }),
  recalculateEvent: (eventId: string) =>
    fetchJSON<ActivityEvent>(`${API_BASE}/events/${eventId}/recalculate`, { method: "POST" }),
  uploadCSV: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return fetchFormData<{ filename: string; total_rows: number; created: number; errors: any[] }>(
      `${API_BASE}/events/bulk-upload`,
      form
    );
  },

  // Factors
  getFactors: (params?: {
    category?: string;
    region?: string;
    subcategory?: string;
    search?: string;
    limit?: number;
  }) => {
    const query = new URLSearchParams(params as any).toString();
    return fetchJSON<EmissionFactor[]>(`${API_BASE}/factors?${query}`);
  },
  lookupFactor: (category: string, subcategory: string, region = "UK", standard?: string) =>
    fetchJSON<{ found: boolean; factor?: EmissionFactor }>(
      `${API_BASE}/factors/lookup?category=${encodeURIComponent(category)}&subcategory=${encodeURIComponent(subcategory)}&region=${encodeURIComponent(region)}${standard ? `&standard=${standard}` : ""}`
    ),

  // Documents
  uploadDocument: (productionId: string, docType: string, file: File) => {
    const form = new FormData();
    form.append("file", file);
    return fetchFormData<Document>(
      `${API_BASE}/documents/upload?production_id=${encodeURIComponent(productionId)}&doc_type=${encodeURIComponent(docType)}`,
      form
    );
  },
  getDocuments: (productionId: string) =>
    fetchJSON<Document[]>(`${API_BASE}/documents/production/${productionId}`),
  extractDocument: (docId: string) =>
    fetchJSON<{ doc_id: string; ocr_status: string; extracted_data: any; extracted_confidence: number | null; review_status: string }>(
      `${API_BASE}/documents/${docId}/extract`,
      { method: "POST" }
    ),
  approveDocument: (docId: string) =>
    fetchJSON<{ approved: boolean; created_events: number; event_ids: string[] }>(
      `${API_BASE}/documents/${docId}/approve`,
      { method: "POST" }
    ),
  rejectDocument: (docId: string) =>
    fetchJSON<{ rejected: boolean }>(`${API_BASE}/documents/${docId}/reject`, { method: "POST" }),
  pendingReview: () => fetchJSON<Document[]>(`${API_BASE}/documents/pending-review`),

  // ML
  forecastGreenlight: (metadata: any) =>
    fetchJSON<GreenlightForecast>(`${API_BASE}/ml/forecast/greenlight`, {
      method: "POST",
      body: JSON.stringify({ project_id: "forecast-" + Date.now(), metadata }),
    }),
  trainModels: (kinds?: string[]) =>
    fetchJSON<{ status: string; kinds: string[] }>(`${API_BASE}/ml/train`, {
      method: "POST",
      body: JSON.stringify(kinds ? { kinds } : {}),
    }),
  getMLHealth: () => fetchJSON<MLHealth>(`${API_BASE}/ml/health`),
  detectAnomalies: (payload: { project_id: string; time_series: any[]; window_days: number; sensitivity: number }) =>
    fetchJSON<any>(`${API_BASE}/ml/anomalies/detect`, { method: "POST", body: JSON.stringify(payload) }),

  // AI
  getReductionPlan: (productionId: string) =>
    fetchJSON<any>(`${API_BASE}/ai/productions/${productionId}/reduction-plan`, { method: "POST" }),
  parseFreeTextEvent: (text: string, defaultRegion = "UK") =>
    fetchJSON<any>(`${API_BASE}/ai/parse-event`, {
      method: "POST",
      body: JSON.stringify({ text, default_region: defaultRegion }),
    }),
  explainAnomaly: (eventId: string, baseline_kgco2e: number, multiple_of_baseline: number, peer_context?: string) =>
    fetchJSON<any>(`${API_BASE}/ai/explain-anomaly`, {
      method: "POST",
      body: JSON.stringify({ event_id: eventId, baseline_kgco2e, multiple_of_baseline, peer_context }),
    }),
  chat: (messages: { role: string; content: string }[], contextProductionId?: string | null) =>
    fetchJSON<any>(`${API_BASE}/ai/chat`, {
      method: "POST",
      body: JSON.stringify({ messages, context_production_id: contextProductionId }),
    }),

  // Reports
  downloadAlbertCSV: (productionId: string) => {
    const token = getToken();
    const url = `${API_BASE}/reports/albert-export/${productionId}`;
    if (token) {
      window.open(`${url}?token=${encodeURIComponent(token)}`, "_blank");
    } else {
      window.open(url, "_blank");
    }
  },
};

export const apiNotifications = {
  list: (limit = 50, offset = 0) =>
    fetchJSON<{ total: number; unread_count: number; items: NotificationItem[] }>(
      `${API_BASE}/notifications?limit=${limit}&offset=${offset}`
    ),
  unreadCount: () =>
    fetchJSON<{ unread_count: number }>(`${API_BASE}/notifications/unread-count`),
  markRead: (id: string) =>
    fetchJSON<NotificationItem>(`${API_BASE}/notifications/${id}/read`, { method: "POST" }),
  markAllRead: () =>
    fetchJSON<{ success: boolean }>(`${API_BASE}/notifications/read-all`, { method: "POST" }),
  delete: (id: string) =>
    fetchJSON<{ deleted: boolean }>(`${API_BASE}/notifications/${id}`, { method: "DELETE" }),
};

export type {
  Production,
  ProductionSummary,
  ActivityEvent,
  GreenlightForecast,
  NotificationItem,
  EmissionFactor,
  Document,
  Recommendation,
  MLHealth,
};
