import { createContext, useContext, useState, useCallback, useRef } from "react";

export interface ConfirmOptions {
  title: string;
  message?: string;
  confirmLabel?: string;
  cancelLabel?: string;
  danger?: boolean; // red confirm button
}

interface ConfirmContextValue {
  confirm: (opts: ConfirmOptions) => Promise<boolean>;
}

const ConfirmContext = createContext<ConfirmContextValue | null>(null);

export function useConfirm() {
  const ctx = useContext(ConfirmContext);
  if (!ctx) throw new Error("useConfirm must be used within ConfirmProvider");
  return ctx;
}

interface PendingConfirm extends ConfirmOptions {
  resolve: (value: boolean) => void;
}

export function ConfirmProvider({ children }: { children: React.ReactNode }) {
  const [pending, setPending] = useState<PendingConfirm | null>(null);
  const resolveRef = useRef<((v: boolean) => void) | null>(null);

  const confirm = useCallback((opts: ConfirmOptions): Promise<boolean> => {
    return new Promise((resolve) => {
      resolveRef.current = resolve;
      setPending({ ...opts, resolve });
    });
  }, []);

  const respond = (value: boolean) => {
    resolveRef.current?.(value);
    resolveRef.current = null;
    setPending(null);
  };

  return (
    <ConfirmContext.Provider value={{ confirm }}>
      {children}
      {pending && (
        <div
          className="fixed inset-0 z-[9999] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm"
          onMouseDown={(e) => { if (e.target === e.currentTarget) respond(false); }}
        >
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm mx-4 overflow-hidden border border-slate-100 animate-in fade-in zoom-in-95 duration-150">
            <div className="px-6 pt-6 pb-4">
              <h3 className="text-base font-bold text-slate-800 mb-1">{pending.title}</h3>
              {pending.message && (
                <p className="text-sm text-slate-500 leading-relaxed">{pending.message}</p>
              )}
            </div>
            <div className="flex gap-3 px-6 pb-6">
              <button
                onClick={() => respond(false)}
                className="flex-1 py-2.5 rounded-xl text-sm font-bold text-slate-500 bg-slate-50 hover:bg-slate-100 border border-slate-200 transition-all"
              >
                {pending.cancelLabel ?? "Cancel"}
              </button>
              <button
                onClick={() => respond(true)}
                className={`flex-1 py-2.5 rounded-xl text-sm font-bold text-white transition-all shadow-lg ${
                  pending.danger
                    ? "bg-red-500 hover:bg-red-600 shadow-red-100"
                    : "bg-emerald-600 hover:bg-emerald-700 shadow-emerald-100"
                }`}
              >
                {pending.confirmLabel ?? "Confirm"}
              </button>
            </div>
          </div>
        </div>
      )}
    </ConfirmContext.Provider>
  );
}
