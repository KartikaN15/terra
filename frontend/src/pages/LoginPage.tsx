import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import {
  Leaf,
  Eye,
  EyeSlash,
  Envelope,
  Lock,
  User,
  ArrowRight,
  WarningCircle,
} from "@phosphor-icons/react";


export default function LoginPage() {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const auth = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      if (mode === "login") {
        await auth.login(email, password);
      } else {
        await auth.register(email, password, fullName || undefined);
      }
      navigate("/");
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const inputCls =
    "w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 pl-11 text-sm text-slate-800 placeholder:text-slate-400 focus:bg-white focus:border-emerald-400 focus:ring-4 focus:ring-emerald-100/50 outline-none transition";

  return (
    <div className="min-h-screen flex">
      {/* Left panel   — illustration (hidden on mobile) */}
      <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden bg-gradient-to-br from-[#F5FBF7] via-[#EDF9F1] to-[#E0F7EA]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(16,185,129,0.06),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(245,158,11,0.05),transparent_50%)]" />
        {/* Soft decorative blob */}
        <div className="absolute -top-20 -right-20 w-80 h-80 bg-emerald-200/30 rounded-full blur-3xl" />
        <div className="absolute -bottom-20 -left-20 w-80 h-80 bg-amber-200/20 rounded-full blur-3xl" />

        <div className="relative z-10 flex flex-col justify-between p-12 w-full">
          <div className="flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-emerald-100 flex items-center justify-center">
              <Leaf weight="fill" className="w-5 h-5 text-emerald-600" />
            </div>
            <span className="font-semibold text-emerald-800 text-xl tracking-tight">Terra</span>
          </div>

          <div className="flex-1 flex items-center justify-center">
            <div className="relative">
              <img
                src={mode === "login" ? "/illustrations/terra-at-work.png" : "/illustrations/terra-growing.png"}
                alt={mode === "login" ? "Terra mascot working" : "Terra mascot growing"}
                className="w-[28rem] h-auto object-contain rounded-2xl shadow-xl"
              />
              <div className="absolute -bottom-3 left-1/2 -translate-x-1/2 bg-white/80 backdrop-blur-md rounded-2xl px-6 py-3 border border-emerald-100/60 shadow-sm">
                <p className="text-emerald-800 text-sm font-medium text-center">
                  {mode === "login"
                    ? "Welcome back to greener productions"
                    : "Start tracking your carbon footprint today"}
                </p>
              </div>
            </div>
          </div>

          <div className="text-center">
            <p className="text-emerald-600/60 text-xs">Sustainable production tracking powered by Terra</p>
          </div>
        </div>
      </div>

      {/* Right panel   — form */}
      <div className="w-full lg:w-1/2 flex flex-col justify-center items-center p-6 sm:p-12 bg-white">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center justify-center gap-2 mb-8">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center">
              <Leaf weight="fill" className="w-5 h-5 text-white" />
            </div>
            <span className="font-semibold text-slate-800 text-xl tracking-tight">Terra</span>
          </div>

          <h1 className="text-2xl font-semibold text-slate-900">
            {mode === "login" ? "Welcome back" : "Create account"}
          </h1>
          <p className="mt-1 text-sm text-slate-500">
            {mode === "login"
              ? "Enter your details to access your workspace"
              : "Enter your details to get started"}
          </p>

          <form onSubmit={handleSubmit} className="mt-8 space-y-4">
            {error && (
              <div className="flex items-start gap-2 text-red-700 bg-red-50 border border-red-100 text-sm p-3 rounded-xl">
                <WarningCircle weight="duotone" className="w-5 h-5 mt-0.5 shrink-0" />
                {error}
              </div>
            )}

            {mode === "register" && (
              <div className="relative">
                <User className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Full name"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className={inputCls}
                />
              </div>
            )}

            <div className="relative">
              <Envelope className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type="email"
                placeholder="Email address"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={inputCls}
              />
            </div>

            <div className="relative">
              <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
              <input
                type={showPassword ? "text" : "password"}
                placeholder="Password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={`${inputCls} pr-10`}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                {showPassword ? (
                  <EyeSlash className="w-5 h-5" />
                ) : (
                  <Eye className="w-5 h-5" />
                )}
              </button>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-emerald-600 text-white py-3 rounded-xl text-sm font-semibold hover:bg-emerald-700 disabled:opacity-40 inline-flex items-center justify-center gap-2 shadow-sm shadow-emerald-600/20 transition"
            >
              {loading ? (
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>
                  {mode === "login" ? "Sign in" : "Create account"}
                  <ArrowRight weight="bold" className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center text-sm text-slate-500">
            {mode === "login" ? (
              <>
                Don&apos;t have an account?{" "}
                <button
                  onClick={() => { setMode("register"); setError(""); }}
                  className="text-emerald-600 font-semibold hover:text-emerald-700"
                >
                  Create account
                </button>
              </>
            ) : (
              <>
                Already have an account?{" "}
                <button
                  onClick={() => { setMode("login"); setError(""); }}
                  className="text-emerald-600 font-semibold hover:text-emerald-700"
                >
                  Sign in
                </button>
              </>
            )}
          </div>

          <div className="mt-8 pt-6 border-t border-slate-100 text-center">
            <Link
              to="/"
              className="text-xs text-slate-400 hover:text-emerald-600 transition"
            >
              Continue without signing in →
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
