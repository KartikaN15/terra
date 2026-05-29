import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  Bell,
  Check,
  CheckCircle,
  WarningCircle,
  FileText,
  Lightbulb,
  TrendUp,
  Info,
  X,
  CircleNotch as Spinner,
} from "@phosphor-icons/react";
import { useNotifications } from "../contexts/NotificationContext";

const TYPE_META: Record<string, { icon: typeof Info; color: string; bg: string }> = {
  DOCUMENT_EXTRACTED: { icon: FileText, color: "text-blue-600", bg: "bg-blue-100" },
  ANOMALY_DETECTED: { icon: WarningCircle, color: "text-amber-600", bg: "bg-amber-100" },
  RECOMMENDATION: { icon: Lightbulb, color: "text-emerald-600", bg: "bg-emerald-100" },
  BUDGET_ALERT: { icon: TrendUp, color: "text-rose-600", bg: "bg-rose-100" },
  SYSTEM: { icon: Info, color: "text-slate-600", bg: "bg-slate-100" },
};

function formatTimeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const mins = Math.floor(diff / 60000);
  const hrs = Math.floor(mins / 60);
  const days = Math.floor(hrs / 24);
  if (mins < 1) return "Just now";
  if (mins < 60) return `${mins}m ago`;
  if (hrs < 24) return `${hrs}h ago`;
  return `${days}d ago`;
}

export default function NotificationCenter() {
  const [open, setOpen] = useState(false);
  const panelRef = useRef<HTMLDivElement>(null);
  const btnRef = useRef<HTMLButtonElement>(null);
  const { notifications, unreadCount, loading, refresh, markRead, markAllRead, remove } =
    useNotifications();

  useEffect(() => {
    function onClick(e: MouseEvent) {
      const target = e.target as Node;
      if (
        panelRef.current?.contains(target) ||
        btnRef.current?.contains(target)
      ) {
        return;
      }
      setOpen(false);
    }
    if (open) document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, [open]);

  useEffect(() => {
    if (open) refresh();
  }, [open, refresh]);

  return (
    <div className="relative">
      <button
        ref={btnRef}
        aria-label="Notifications"
        onClick={() => setOpen((v) => !v)}
        className="relative p-2 rounded-lg hover:bg-slate-100 transition"
      >
        <Bell weight={open ? "fill" : "duotone"} className="w-5 h-5 text-slate-600" />
        {unreadCount > 0 && (
          <span className="absolute top-1.5 right-1.5 min-w-[18px] h-[18px] px-1 bg-amber-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center ring-2 ring-white">
            {unreadCount > 9 ? "9+" : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div
          ref={panelRef}
          className="absolute right-0 mt-2 w-96 bg-white rounded-2xl shadow-xl border border-slate-100 overflow-hidden z-50"
        >
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-50">
            <h3 className="text-sm font-semibold text-slate-800">Notifications</h3>
            <div className="flex items-center gap-1">
              {unreadCount > 0 && (
                <button
                  onClick={() => markAllRead()}
                  className="flex items-center gap-1 px-2 py-1 text-xs font-medium text-emerald-600 hover:bg-emerald-50 rounded-md transition"
                  title="Mark all as read"
                >
                  <Check className="w-3.5 h-3.5" />
                  Mark all read
                </button>
              )}
            </div>
          </div>

          {/* List */}
          <div className="max-h-[420px] overflow-y-auto">
            {loading && notifications.length === 0 && (
              <div className="flex items-center justify-center py-10">
                <Spinner className="w-5 h-5 text-emerald-600 animate-spin" weight="bold" />
              </div>
            )}

            {!loading && notifications.length === 0 && (
              <div className="flex flex-col items-center justify-center py-10 text-center px-6">
                <div className="w-12 h-12 rounded-full bg-slate-50 flex items-center justify-center mb-3">
                  <Bell className="w-5 h-5 text-slate-300" />
                </div>
                <p className="text-sm font-medium text-slate-600">No notifications yet</p>
                <p className="text-xs text-slate-400 mt-1">
                  We'll notify you when documents are processed, anomalies are found, or recommendations are ready.
                </p>
              </div>
            )}

            {notifications.map((n) => {
              const meta = TYPE_META[n.type] || TYPE_META.SYSTEM;
              const Icon = meta.icon;
              return (
                <div
                  key={n.notification_id}
                  className={`group relative flex gap-3 px-4 py-3 hover:bg-slate-50 transition border-b border-slate-50 last:border-0 ${
                    !n.is_read ? "bg-emerald-50/30" : ""
                  }`}
                >
                  {/* Unread indicator */}
                  {!n.is_read && (
                    <div className="absolute left-0 top-4 w-1 h-1 rounded-full bg-emerald-500" />
                  )}

                  {/* Icon */}
                  <div
                    className={`mt-0.5 w-9 h-9 rounded-lg ${meta.bg} flex items-center justify-center shrink-0`}
                  >
                    <Icon className={`w-4 h-4 ${meta.color}`} weight="duotone" />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className={`text-sm leading-snug ${!n.is_read ? "font-medium text-slate-800" : "text-slate-600"}`}>
                        {n.title}
                      </p>
                      <span className="text-[10px] text-slate-400 shrink-0 mt-0.5">
                        {formatTimeAgo(n.created_at)}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 leading-relaxed mt-0.5 line-clamp-2">
                      {n.message}
                    </p>

                    {/* Actions */}
                    <div className="flex items-center gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      {!n.is_read && (
                        <button
                          onClick={() => markRead(n.notification_id)}
                          className="flex items-center gap-1 text-[10px] font-medium text-emerald-600 hover:text-emerald-700"
                        >
                          <CheckCircle className="w-3 h-3" />
                          Mark read
                        </button>
                      )}
                      {n.entity_type && n.entity_id && (
                        <Link
                          to={`/${n.entity_type}s/${n.entity_id}`}
                          onClick={() => setOpen(false)}
                          className="text-[10px] font-medium text-slate-500 hover:text-slate-700"
                        >
                          View
                        </Link>
                      )}
                      <button
                        onClick={() => remove(n.notification_id)}
                        className="ml-auto text-[10px] text-slate-400 hover:text-rose-500 transition"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="px-4 py-2.5 border-t border-slate-50 bg-slate-50/50">
              <p className="text-[10px] text-slate-400 text-center">
                {unreadCount > 0 ? `${unreadCount} unread` : "All caught up"}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
