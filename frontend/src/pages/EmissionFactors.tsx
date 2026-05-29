import { useEffect, useState } from "react";
import { 
  Database, 
  MagnifyingGlass, 
  Globe, 
  CaretDown, 
  Leaf,
  Airplane,
  Lightning,
  Trash,
  Drop,
  House,
  ForkKnife,
  Desktop,
  Info,
  DownloadSimple,
  X,
  CheckCircle,
  Calendar,
  Faders,
} from "@phosphor-icons/react";
import { api, type EmissionFactor } from "../api";
import heroImage from "../assets/illustrations/emission-factors-hero.png";

const CATEGORIES = [
  { id: "ENERGY", label: "Energy", icon: Lightning, color: "bg-amber-100 text-amber-700" },
  { id: "TRANSPORT", label: "Transport", icon: Airplane, color: "bg-blue-100 text-blue-700" },
  { id: "ACCOMMODATION", label: "Accommodation", icon: House, color: "bg-purple-100 text-purple-700" },
  { id: "MATERIALS", label: "Materials", icon: Database, color: "bg-slate-100 text-slate-700" },
  { id: "WASTE", label: "Waste", icon: Trash, color: "bg-emerald-100 text-emerald-700" },
  { id: "WATER", label: "Water", icon: Drop, color: "bg-cyan-100 text-cyan-700" },
  { id: "CATERING", label: "Catering", icon: ForkKnife, color: "bg-orange-100 text-orange-700" },
  { id: "POST_VFX", label: "Post/VFX", icon: Desktop, color: "bg-indigo-100 text-indigo-700" },
];

const REGIONS = ["Global", "UK", "US", "EU", "Germany", "France", "Canada"];

export default function EmissionFactors() {
  const [factors, setFactors] = useState<EmissionFactor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [search, setSearch] = useState("");
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [activeRegion, setActiveRegion] = useState<string | null>(null);
  const [selectedFactor, setSelectedFactor] = useState<EmissionFactor | null>(null);

  const stats = {
    total: factors.length,
    scope1: factors.filter(f => f.scope === 'SCOPE_1').length,
    scope2: factors.filter(f => f.scope === 'SCOPE_2').length,
    scope3: factors.filter(f => f.scope === 'SCOPE_3').length,
  };

  const handleExport = () => {
    const dataStr = JSON.stringify(filtered, null, 2);
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr);
    const exportFileDefaultName = 'terra-emission-factors.json';
    const linkElement = document.createElement('a');
    linkElement.setAttribute('href', dataUri);
    linkElement.setAttribute('download', exportFileDefaultName);
    linkElement.click();
  };

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        const data = await api.getFactors({ 
          category: activeCategory || undefined, 
          region: activeRegion || undefined,
          limit: 100 
        });
        setFactors(data);
        setError(null);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [activeCategory, activeRegion]);

  const filtered = factors.filter(f => 
    f.subcategory.toLowerCase().includes(search.toLowerCase()) ||
    f.activity_type.toLowerCase().includes(search.toLowerCase()) ||
    f.standard.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-700 via-emerald-600 to-teal-700 p-10 text-white shadow-2xl shadow-emerald-200/50">
        <div className="relative z-10 flex flex-col md:flex-row items-center gap-12">
          <div className="flex-1 text-center md:text-left space-y-6">
            <h1 className="text-4xl md:text-5xl font-extrabold mb-4 tracking-tight leading-tight">
              The Emission <span className="text-emerald-300">Factor Bible</span>
            </h1>
            <p className="text-emerald-50/90 text-lg max-w-xl leading-relaxed font-medium">
              Terra's calculation engine is powered by high-fidelity reference data from DEFRA, EPA, and BAFTA albert. Audit-ready, versioned, and globally compliant.
            </p>
          </div>
          <div className="w-56 h-56 md:w-72 md:h-72 shrink-0 relative">
            <div className="absolute inset-0 bg-emerald-400/20 rounded-full blur-[80px] animate-pulse" />
            <img 
              src={heroImage} 
              alt="" 
              className="relative z-10 w-full h-full object-contain drop-shadow-[0_20px_50px_rgba(0,0,0,0.3)]"
              onError={(e) => {
                e.currentTarget.src = "https://cdn-icons-png.flaticon.com/512/3233/3233512.png";
              }}
            />
          </div>
        </div>
        {/* Background decorative elements */}
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-white/5 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-96 h-96 bg-teal-400/10 rounded-full blur-[100px] pointer-events-none" />
      </div>

      {error && (
        <div className="flex items-center gap-3 p-4 bg-red-50 border border-red-100 rounded-2xl text-red-700 text-sm font-medium">
          <Info weight="fill" className="w-5 h-5" />
          {error}
        </div>
      )}

      {/* Control Center: Search & Filters */}
      <div className="terra-card p-1 bg-white/60 backdrop-blur-xl border border-white/40 shadow-xl overflow-hidden">
        <div className="p-5 space-y-6">
          <div className="flex flex-col lg:flex-row gap-5">
            {/* Search bar */}
            <div className="flex-1 relative group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <MagnifyingGlass className="w-5 h-5 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
              </div>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by activity, standard or keyword..."
                className="block w-full pl-12 pr-12 py-3.5 border border-slate-200/80 rounded-2xl text-sm placeholder:text-slate-400 focus:outline-none focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 transition-all bg-slate-50/50 hover:bg-white"
              />
              {search && (
                <button 
                  onClick={() => setSearch("")}
                  className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 hover:text-slate-600 transition-colors"
                >
                  <Trash size={16} />
                </button>
              )}
            </div>

            {/* Region Dropdown */}
            <div className="relative min-w-[200px] group">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Globe className="w-5 h-5 text-slate-400 group-focus-within:text-emerald-500 transition-colors" />
              </div>
              <select
                value={activeRegion || ""}
                onChange={(e) => setActiveRegion(e.target.value || null)}
                className="appearance-none block w-full pl-12 pr-12 py-3.5 border border-slate-200/80 rounded-2xl text-sm bg-slate-50/50 hover:bg-white focus:outline-none focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 transition-all cursor-pointer font-medium"
              >
                <option value="">All Regions</option>
                {REGIONS.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
              <div className="absolute inset-y-0 right-0 pr-4 flex items-center pointer-events-none text-slate-400">
                <CaretDown weight="bold" className="w-4 h-4" />
              </div>
            </div>
          </div>

          {/* Category Pills */}
          <div className="flex flex-wrap items-center gap-2.5">
            <span className="text-[11px] font-bold text-slate-400 tracking-wider mr-2 ml-1">Categories</span>
            <button
              onClick={() => setActiveCategory(null)}
              className={`px-5 py-2 rounded-xl text-xs font-bold transition-all duration-300 ${
                activeCategory === null 
                ? "bg-slate-900 text-white shadow-lg shadow-slate-200 translate-y-[-1px]" 
                : "bg-slate-100 text-slate-600 hover:bg-slate-200 active:scale-95"
              }`}
            >
              All Factors
            </button>
            {CATEGORIES.map(cat => (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                className={`flex items-center gap-2.5 px-5 py-2 rounded-xl text-xs font-bold transition-all duration-300 ${
                  activeCategory === cat.id 
                  ? "bg-emerald-600 text-white shadow-lg shadow-emerald-200 translate-y-[-1px]" 
                  : "bg-white border border-slate-100 text-slate-600 hover:border-emerald-200 hover:bg-emerald-50/30 active:scale-95"
                }`}
              >
                <cat.icon className={`w-4 h-4 ${activeCategory === cat.id ? "text-white" : "text-slate-400"}`} />
                {cat.label}
              </button>
            ))}
            {(activeCategory || activeRegion || search) && (
              <button
                onClick={() => {setActiveCategory(null); setActiveRegion(null); setSearch("");}}
                className="ml-auto text-[10px] font-bold text-rose-500 hover:text-rose-600 uppercase tracking-widest flex items-center gap-1.5 px-3 py-1.5 rounded-lg hover:bg-rose-50 transition-colors"
              >
                <X weight="bold" /> Clear All
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total Factors", value: stats.total, color: "text-slate-900", bg: "bg-slate-50" },
          { label: "Scope 1 (Direct)", value: stats.scope1, color: "text-rose-600", bg: "bg-rose-50/50" },
          { label: "Scope 2 (Energy)", value: stats.scope2, color: "text-sky-600", bg: "bg-sky-50/50" },
          { label: "Scope 3 (Value Chain)", value: stats.scope3, color: "text-indigo-600", bg: "bg-indigo-50/50" },
        ].map((stat, i) => (
          <div key={i} className={`p-4 rounded-2xl ${stat.bg} border border-white/50 shadow-sm`}>
            <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1">{stat.label}</div>
            <div className={`text-2xl font-black ${stat.color}`}>{loading ? "..." : stat.value}</div>
          </div>
        ))}
      </div>

      {/* Factors Explorer */}
      <div className="flex flex-col lg:flex-row gap-8 items-start">
        <div className={`terra-card border border-white/60 shadow-2xl shadow-slate-200/50 overflow-hidden bg-white/80 backdrop-blur-sm transition-all duration-500 ${selectedFactor ? 'lg:w-[60%]' : 'w-full'}`}>
          <div className="p-4 border-b border-slate-100 flex items-center justify-between bg-white/50">
            <h2 className="text-sm font-bold text-slate-700 flex items-center gap-2">
              <Database className="w-4 h-4 text-emerald-500" />
              Factor Registry
            </h2>
            <button 
              onClick={handleExport}
              disabled={loading || filtered.length === 0}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold text-slate-600 hover:bg-emerald-50 hover:text-emerald-700 transition-colors border border-slate-200 disabled:opacity-50"
            >
              <DownloadSimple weight="bold" />
              Export JSON
            </button>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/50 border-b border-slate-100/80">
                  <th className="px-6 py-4 text-[11px] font-bold text-slate-400 tracking-wider">Activity Taxonomy</th>
                  <th className="px-6 py-4 text-[11px] font-bold text-slate-400 tracking-wider">Region</th>
                  <th className="px-6 py-4 text-[11px] font-bold text-slate-400 tracking-wider text-center">Scope</th>
                  <th className="px-6 py-4 text-[11px] font-bold text-slate-400 tracking-wider text-right">Value</th>
                  <th className="px-6 py-4 text-[11px] font-bold text-slate-400 tracking-wider">Unit</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100/50">
                {loading ? (
                  Array.from({ length: 6 }).map((_, i) => (
                    <tr key={i} className="animate-pulse">
                      <td colSpan={5} className="px-6 py-6">
                        <div className="flex gap-4">
                          <div className="w-10 h-10 bg-slate-100 rounded-xl" />
                          <div className="flex-1 space-y-3">
                            <div className="h-4 bg-slate-100 rounded-full w-1/3" />
                            <div className="h-3 bg-slate-50 rounded-full w-1/4" />
                          </div>
                        </div>
                      </td>
                    </tr>
                  ))
                ) : filtered.length > 0 ? (
                  filtered.map((f) => {
                    const cat = CATEGORIES.find(c => c.id === f.category);
                    const Icon = cat?.icon || Database;
                    const isSelected = selectedFactor?.factor_id === f.factor_id;
                    
                    return (
                      <tr 
                        key={f.factor_id} 
                        onClick={() => setSelectedFactor(f)}
                        className={`hover:bg-emerald-50/40 transition-all duration-200 group cursor-pointer ${isSelected ? 'bg-emerald-50 ring-2 ring-inset ring-emerald-500/20' : ''}`}
                      >
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            <div className={`w-10 h-10 rounded-xl ${cat?.color || "bg-slate-100 text-slate-600"} flex items-center justify-center shrink-0 shadow-sm transition-transform group-hover:scale-105 duration-300`}>
                              <Icon weight="duotone" className="w-5 h-5" />
                            </div>
                            <div>
                              <div className="text-sm font-bold text-slate-900 capitalize leading-tight mb-0.5 group-hover:text-emerald-700 transition-colors">
                                {f.activity_type.replace(/_/g, ' ')}
                              </div>
                              <div className="text-[10px] text-slate-400 font-bold flex items-center gap-1.5">
                                <span className="text-emerald-600/70 capitalize">{f.category.toLowerCase()}</span>
                              </div>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-1.5 text-[11px] text-slate-500 font-bold">
                            <Globe weight="bold" className="w-3 h-3 text-slate-300" />
                            {f.region}
                          </div>
                        </td>
                        <td className="px-6 py-4 text-center">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[9px] font-black tracking-wide ${
                            f.scope === 'SCOPE_1' ? 'bg-rose-50 text-rose-600 border border-rose-100' :
                            f.scope === 'SCOPE_2' ? 'bg-sky-50 text-sky-600 border border-sky-100' :
                            'bg-indigo-50 text-indigo-600 border border-indigo-100'
                          }`}>
                            {f.scope.replace('SCOPE_', 'S')}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-right">
                          <span className="text-sm font-black text-slate-900 tabular-nums tracking-tight">
                            {f.factor_value < 0.001 ? f.factor_value.toExponential(3) : f.factor_value.toFixed(4)}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className="text-[10px] font-bold text-slate-400">
                            {f.unit.replace(/_/g, ' ')}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                ) : (
                  <tr>
                    <td colSpan={5} className="px-8 py-20 text-center">
                      <div className="flex flex-col items-center justify-center">
                        <div className="w-16 h-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                          <MagnifyingGlass className="w-8 h-8 text-slate-200" />
                        </div>
                        <h3 className="text-base font-bold text-slate-900 mb-1">No factors match your search</h3>
                        <p className="text-xs text-slate-500 max-w-xs mx-auto mb-6 leading-relaxed">
                          Try adjusting your filters or search keywords.
                        </p>
                        <button 
                          onClick={() => {setSearch(""); setActiveCategory(null); setActiveRegion(null);}}
                          className="px-5 py-2 bg-emerald-600 text-white rounded-xl text-xs font-bold shadow-lg shadow-emerald-100 hover:bg-emerald-700 transition-all"
                        >
                          Clear Filters
                        </button>
                      </div>
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
          
          {/* Registry Footer */}
          {!loading && filtered.length > 0 && (
            <div className="px-6 py-4 bg-slate-50/80 border-t border-slate-100/80 flex flex-col sm:flex-row items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">
                  Showing {filtered.length} Results
                </span>
              </div>
              <div className="flex items-center gap-4 text-[10px] text-slate-400 font-bold tracking-wider">
                <span className="flex items-center gap-1.5">
                  <CheckCircle weight="fill" className="text-emerald-500" />
                  Audit-Ready
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Factor Detail Sidebar */}
        {selectedFactor && (
          <div className="w-full lg:w-[40%] sticky top-8 animate-in slide-in-from-right duration-500">
            <div className="terra-card border-2 border-emerald-500/10 shadow-2xl bg-white/95 backdrop-blur-xl overflow-hidden ring-1 ring-black/5">
              <div className="p-7 bg-gradient-to-br from-slate-900 via-slate-800 to-emerald-950 text-white relative overflow-hidden">
                <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl" />
                <button 
                  onClick={() => setSelectedFactor(null)}
                  className="absolute top-5 right-5 p-2 rounded-xl bg-white/5 hover:bg-white/10 transition-colors border border-white/10 z-10"
                >
                  <X size={18} weight="bold" />
                </button>
                <div className="flex items-center gap-5 mb-8 relative z-10">
                  <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 flex items-center justify-center shrink-0 border border-emerald-400/30 shadow-inner">
                    {(() => {
                      const cat = CATEGORIES.find(c => c.id === selectedFactor.category);
                      const Icon = cat?.icon || Database;
                      return <Icon weight="duotone" className="w-9 h-9 text-emerald-400" />;
                    })()}
                  </div>
                  <div>
                    <div className="text-[10px] font-bold uppercase tracking-[0.3em] text-emerald-400/60 mb-1.5">Verified Factor</div>
                    <h3 className="text-2xl font-black leading-tight capitalize">{selectedFactor.activity_type.replace(/_/g, ' ')}</h3>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 relative z-10">
                  <div className="bg-white/5 rounded-2xl p-4 border border-white/5 backdrop-blur-md">
                    <div className="text-[9px] font-bold uppercase text-slate-400 tracking-widest mb-1.5">Reporting Scope</div>
                    <div className="flex items-center gap-2">
                      <div className={`w-2 h-2 rounded-full ${
                        selectedFactor.scope === 'SCOPE_1' ? 'bg-rose-400' :
                        selectedFactor.scope === 'SCOPE_2' ? 'bg-sky-400' : 'bg-indigo-400'
                      }`} />
                      <div className="text-sm font-black">{selectedFactor.scope.replace('_', ' ')}</div>
                    </div>
                  </div>
                  <div className="bg-white/5 rounded-2xl p-4 border border-white/5 backdrop-blur-md">
                    <div className="text-[9px] font-bold uppercase text-slate-400 tracking-widest mb-1.5">Regulatory Standard</div>
                    <div className="text-sm font-black flex items-center gap-2">
                      <CheckCircle weight="fill" className="text-emerald-500" />
                      {selectedFactor.standard}
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-8 space-y-8 max-h-[calc(100vh-20rem)] overflow-y-auto sidebar-scroll">
                <div>
                  <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                    <Info weight="bold" className="text-emerald-500" />
                    Activity Context
                  </h4>
                  <div className="text-[13px] text-slate-600 leading-relaxed font-medium bg-slate-50/50 p-5 rounded-2xl border border-slate-100 shadow-inner">
                    {selectedFactor.description || "Comprehensive carbon intensity factor for industrial activity monitoring and sustainability reporting."}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-8">
                  <div className="group relative">
                    <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-3">Intensity Value</h4>
                    <div className="space-y-1">
                      <div className="flex items-baseline gap-2">
                        <span className="text-3xl font-black text-slate-900 tracking-tighter">{selectedFactor.factor_value}</span>
                        <button 
                          onClick={() => navigator.clipboard.writeText(selectedFactor.factor_value.toString())}
                          className="p-1.5 text-slate-300 hover:text-emerald-500 transition-colors"
                          title="Copy to clipboard"
                        >
                          <DownloadSimple size={14} />
                        </button>
                      </div>
                      <div className="text-[11px] font-bold text-emerald-600 uppercase tracking-wider">{selectedFactor.unit.replace(/_/g, ' ')}</div>
                    </div>
                  </div>
                  <div>
                    <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-3">Geographic Region</h4>
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600 border border-blue-100 shadow-sm">
                        <Globe weight="duotone" size={20} />
                      </div>
                      <div className="space-y-0.5">
                        <span className="text-sm font-bold text-slate-700 block leading-none">{selectedFactor.region}</span>
                        {selectedFactor.country_code && <span className="text-[10px] text-slate-400 font-bold uppercase tracking-tighter">ISO: {selectedFactor.country_code}</span>}
                      </div>
                    </div>
                  </div>
                </div>

                {(selectedFactor.wtt_factor !== null || selectedFactor.radiative_forcing_multiplier !== 1) && (
                  <div className="grid grid-cols-2 gap-4 pt-2">
                    {selectedFactor.wtt_factor !== null && (
                      <div className="p-3 rounded-xl bg-amber-50 border border-amber-100">
                        <div className="text-[10px] font-bold text-amber-600 uppercase tracking-widest mb-1">WTT Factor</div>
                        <div className="text-lg font-black text-slate-800">{selectedFactor.wtt_factor}</div>
                        <div className="text-[10px] text-amber-700/70 font-medium">kg CO₂e / {selectedFactor.unit.replace(/_/g, ' ')} upstream</div>
                      </div>
                    )}
                    {selectedFactor.radiative_forcing_multiplier !== 1 && (
                      <div className="p-3 rounded-xl bg-sky-50 border border-sky-100">
                        <div className="text-[10px] font-bold text-sky-600 uppercase tracking-widest mb-1">RFI Multiplier</div>
                        <div className="text-lg font-black text-slate-800">×{selectedFactor.radiative_forcing_multiplier}</div>
                        <div className="text-[10px] text-sky-700/70 font-medium">Aviation radiative forcing (DEFRA)</div>
                      </div>
                    )}
                  </div>
                )}

                <div className="pt-8 border-t border-slate-100">
                  <h4 className="text-[11px] font-bold text-slate-400 uppercase tracking-widest mb-5">Compliance Metadata</h4>
                  <div className="grid grid-cols-1 gap-3">
                    <div className="flex items-center justify-between p-4 rounded-2xl bg-white border border-slate-100 hover:border-emerald-200 transition-colors shadow-sm group">
                      <div className="flex items-center gap-3 text-xs font-bold text-slate-500">
                        <div className="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center group-hover:bg-emerald-50 transition-colors">
                          <Calendar weight="duotone" className="text-slate-400 group-hover:text-emerald-500" />
                        </div>
                        Activation Date
                      </div>
                      <div className="text-xs font-black text-slate-700">{new Date(selectedFactor.valid_from).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}</div>
                    </div>
                    <div className="flex items-center justify-between p-4 rounded-2xl bg-white border border-slate-100 hover:border-emerald-200 transition-colors shadow-sm group">
                      <div className="flex items-center gap-3 text-xs font-bold text-slate-500">
                        <div className="w-8 h-8 rounded-lg bg-slate-50 flex items-center justify-center group-hover:bg-emerald-50 transition-colors">
                          <Faders weight="duotone" className="text-slate-400 group-hover:text-emerald-500" />
                        </div>
                        Registry Version
                      </div>
                      <div className="text-xs font-black text-slate-700 px-2.5 py-1 bg-slate-100 rounded-lg group-hover:bg-emerald-100 group-hover:text-emerald-700 transition-colors">{selectedFactor.version}</div>
                    </div>
                  </div>
                </div>

                <div className="p-5 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-2xl border border-emerald-100/50 flex items-start gap-4 shadow-sm">
                  <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center shrink-0 shadow-sm border border-emerald-100">
                    <CheckCircle weight="fill" className="w-6 h-6 text-emerald-500" />
                  </div>
                  <div className="space-y-1">
                    <h5 className="text-[11px] font-bold text-emerald-900 uppercase tracking-widest">Audit Stability</h5>
                    <p className="text-[12px] text-emerald-800/80 font-medium leading-relaxed">
                      This factor is cryptographically hashed and pinned to the {selectedFactor.standard} database for audit-ready calculations.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Informational Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="terra-tile-emerald p-8 rounded-3xl flex gap-6 group hover:shadow-2xl hover:shadow-emerald-100 transition-all duration-500 border-2 border-transparent hover:border-emerald-200">
          <div className="w-14 h-14 rounded-2xl bg-white flex items-center justify-center shrink-0 shadow-xl shadow-emerald-200/50 group-hover:scale-110 transition-transform">
            <Leaf weight="duotone" className="w-8 h-8 text-emerald-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-emerald-900 mb-2">Audit-Ready Reliability</h3>
            <p className="text-sm text-emerald-800/70 leading-relaxed font-medium">
              Every factor in our registry is cryptographically linked to official regulatory sources. Terra automatically versions these factors, ensuring historical reports remain bulletproof even as standards evolve.
            </p>
          </div>
        </div>
        <div className="terra-tile-cream p-8 rounded-3xl flex gap-6 group hover:shadow-2xl hover:shadow-amber-100 transition-all duration-500 border-2 border-transparent hover:border-amber-200">
          <div className="w-14 h-14 rounded-2xl bg-white flex items-center justify-center shrink-0 shadow-xl shadow-amber-200/50 group-hover:scale-110 transition-transform">
            <Globe weight="duotone" className="w-8 h-8 text-amber-600" />
          </div>
          <div>
            <h3 className="text-lg font-bold text-amber-900 mb-2">Contextual Intelligence</h3>
            <p className="text-sm text-amber-800/70 leading-relaxed font-medium">
              Our engine dynamically adjusts grid intensity factors based on real-time production coordinates. This ensures Scope 2 calculations reflect actual regional energy mixes rather than generic averages.
            </p>
          </div>
        </div>
      </div>
    </div>

  );
}
