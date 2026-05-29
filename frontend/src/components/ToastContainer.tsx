import { useEffect, useState } from "react";
import { CheckCircle, XCircle, Warning, Info, X } from "@phosphor-icons/react";
import { useToast, type Toast } from "../contexts/ToastContext";

const STYLES = {
  success: { progress: "bg-emerald-400", icon: CheckCircle, iconCls: "text-emerald-500" },
  error:   { progress: "bg-red-400",     icon: XCircle,     iconCls: "text-red-500"     },
  warning: { progress: "bg-amber-400",   icon: Warning,     iconCls: "text-amber-500"   },
  info:    { progress: "bg-blue-400",    icon: Info,        iconCls: "text-blue-500"    },
};

function ToastItem({ toast, onDismiss }: { toast: Toast; onDismiss: () => void }) {
  const [visible, setVisible] = useState(false);
  const style = STYLES[toast.type];
  const Icon = style.icon;

  // mount animation
  useEffect(() => {
    const raf = requestAnimationFrame(() => setVisible(true));
    return () => cancelAnimationFrame(raf);
  }, []);

return (
    <div
      className={`relative flex items-start gap-3 bg-white rounded-xl shadow-lg border border-slate-100 p-4 pr-10 min-w-[300px] max-w-sm overflow-hidden transition-all duration-300 ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
      }`}
    >

      <Icon weight="fill" size={20} className={`${style.iconCls} flex-shrink-0 mt-0.5`} />

      <div className="flex-1 min-w-0">
        <p className="text-sm font-bold text-slate-800 leading-snug">{toast.title}</p>
        {toast.message && (
          <p className="text-xs text-slate-500 mt-0.5 leading-relaxed">{toast.message}</p>
        )}
      </div>

      <button
        onClick={onDismiss}
        className="absolute top-3 right-3 text-slate-300 hover:text-slate-500 transition-colors"
      >
        <X size={14} weight="bold" />
      </button>

    </div>
  );
}

export default function ToastContainer() {
  const { toasts, dismiss } = useToast();

  return (
    <div className="fixed bottom-6 right-6 z-[10000] flex flex-col gap-2 items-end pointer-events-none">
      {toasts.map((t) => (
        <div key={t.id} className="pointer-events-auto">
          <ToastItem toast={t} onDismiss={() => dismiss(t.id)} />
        </div>
      ))}
    </div>
  );
}
