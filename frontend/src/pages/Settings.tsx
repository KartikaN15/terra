import { useState } from "react";
import {
  Users,
  CloudArrowUp,
  CreditCard,
  CheckCircle,
  GearSix,
  ShieldCheck,
  Bell,
  ArrowRight,
  Lightning,
  Tree
} from "@phosphor-icons/react";
import heroImage from "../assets/illustrations/settings-hero.png";

const TEAM_MEMBERS = [
  { id: 1, name: "Sarah Chen", role: "Sustainability Lead", email: "sarah.chen@terra.com", status: "Active", avatar: "SC" },
  { id: 2, name: "Marcus Thorne", role: "Production Manager", email: "m.thorne@indie-films.co", status: "Active", avatar: "MT" },
  { id: 3, name: "Elena Rodriguez", role: "Compliance Auditor", email: "elena@ecoverify.org", status: "Pending", avatar: "ER" },
];

const INTEGRATIONS = [
  { id: "albert", name: "BAFTA albert", description: "Automated data sync with carbon calculators.", status: "Connected", icon: Lightning, color: "bg-emerald-100 text-emerald-700" },
  { id: "aws", name: "AWS S3", description: "Storage for production receipts and evidence.", status: "Not Connected", icon: CloudArrowUp, color: "bg-orange-100 text-orange-700" },
  { id: "stripe", name: "Stripe", description: "Billing and subscription management.", status: "Connected", icon: CreditCard, color: "bg-blue-100 text-blue-700" },
];

export default function Settings() {
  const [activeTab, setActiveTab] = useState<"general" | "team" | "integrations" | "billing">("general");

  const renderTabContent = () => {
    switch (activeTab) {
      case "general":
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="terra-card p-6 bg-white border border-slate-100 hover:border-emerald-200 transition-all group">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-emerald-50 flex items-center justify-center text-emerald-600">
                    <ShieldCheck weight="duotone" size={24} />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900">Security & Privacy</h3>
                    <p className="text-xs text-slate-500">Manage password and security keys</p>
                  </div>
                </div>
                <button className="w-full py-2.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-600 hover:bg-slate-50 transition-colors flex items-center justify-center gap-2">
                  Update Settings <ArrowRight size={14} />
                </button>
              </div>
              <div className="terra-card p-6 bg-white border border-slate-100 hover:border-emerald-200 transition-all group">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-blue-50 flex items-center justify-center text-blue-600">
                    <Bell weight="duotone" size={24} />
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-900">Notifications</h3>
                    <p className="text-xs text-slate-500">Manage email and push alerts</p>
                  </div>
                </div>
                <button className="w-full py-2.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-600 hover:bg-slate-50 transition-colors flex items-center justify-center gap-2">
                  Configure Alerts <ArrowRight size={14} />
                </button>
              </div>
            </div>

            <div className="terra-card overflow-hidden bg-white border border-slate-100">
              <div className="p-6 border-b border-slate-50 flex items-center justify-between bg-slate-50/50">
                <div className="flex items-center gap-3">
                  <GearSix weight="duotone" size={20} className="text-slate-400" />
                  <h2 className="font-bold text-slate-900">Workspace Preferences</h2>
                </div>
              </div>
              <div className="p-6 space-y-6">
                <div className="flex items-center justify-between py-2 border-b border-slate-50">
                  <div>
                    <div className="text-sm font-bold text-slate-800">Primary Domain</div>
                    <div className="text-xs text-slate-500">Select your industry vertical</div>
                  </div>
                  <select className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-500/10 focus:border-emerald-500">
                    <option>Film & TV Production</option>
                    <option>Live Events</option>
                    <option>Commercial Real Estate</option>
                  </select>
                </div>
                <div className="flex items-center justify-between py-2 border-b border-slate-50">
                  <div>
                    <div className="text-sm font-bold text-slate-800">Default Currency</div>
                    <div className="text-xs text-slate-500">Used for budget and ROI reporting</div>
                  </div>
                  <select className="bg-slate-50 border border-slate-200 rounded-lg px-3 py-1.5 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-emerald-500/10 focus:border-emerald-500">
                    <option>USD ($)</option>
                    <option>GBP (£)</option>
                    <option>EUR (€)</option>
                  </select>
                </div>
                <div className="flex items-center justify-between py-2">
                  <div>
                    <div className="text-sm font-bold text-slate-800">Anomaly Sensitivity</div>
                    <div className="text-xs text-slate-500">AI detection threshold for outliers</div>
                  </div>
                  <input type="range" className="w-32 accent-emerald-600" />
                </div>
              </div>
            </div>
          </div>
        );
      case "team":
        return (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="flex items-center justify-between mb-2">
              <h2 className="text-lg font-bold text-slate-900">Team Members</h2>
              <button className="px-4 py-2 bg-emerald-600 text-white rounded-xl text-xs font-bold hover:bg-emerald-700 transition-all flex items-center gap-2 shadow-lg shadow-emerald-100">
                <Users size={16} /> Invite Member
              </button>
            </div>
            <div className="terra-card overflow-hidden bg-white border border-slate-100">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-slate-50/50 border-b border-slate-100">
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-400 tracking-wider">Member</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-400 tracking-wider">Role</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-400 tracking-wider">Status</th>
                    <th className="px-6 py-4 text-[10px] font-bold text-slate-400 tracking-wider text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {TEAM_MEMBERS.map(member => (
                    <tr key={member.id} className="hover:bg-slate-50/50 transition-colors group">
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center text-xs font-bold text-slate-600 group-hover:scale-110 transition-transform">
                            {member.avatar}
                          </div>
                          <div>
                            <div className="text-sm font-bold text-slate-900">{member.name}</div>
                            <div className="text-xs text-slate-500">{member.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-xs font-medium text-slate-600">{member.role}</span>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                          member.status === 'Active' ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-700'
                        }`}>
                          <div className={`w-1 h-1 rounded-full ${member.status === 'Active' ? 'bg-emerald-500' : 'bg-amber-500'}`} />
                          {member.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button className="text-xs font-bold text-slate-400 hover:text-rose-600 transition-colors">Remove</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        );
      case "integrations":
        return (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            {INTEGRATIONS.map(int => (
              <div key={int.id} className="terra-card p-6 bg-white border border-slate-100 hover:border-emerald-200 transition-all flex flex-col h-full">
                <div className="flex items-center justify-between mb-4">
                  <div className={`w-12 h-12 rounded-2xl ${int.color} flex items-center justify-center`}>
                    <int.icon weight="duotone" size={24} />
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-lg ${
                    int.status === 'Connected' ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'
                  }`}>
                    {int.status}
                  </span>
                </div>
                <h3 className="font-bold text-slate-900 mb-2">{int.name}</h3>
                <p className="text-xs text-slate-500 leading-relaxed mb-6 flex-1">
                  {int.description}
                </p>
                <button className={`w-full py-2.5 rounded-xl text-xs font-bold transition-all ${
                  int.status === 'Connected' 
                  ? 'border border-slate-200 text-slate-600 hover:bg-slate-50' 
                  : 'bg-slate-900 text-white hover:bg-slate-800'
                }`}>
                  {int.status === 'Connected' ? 'Configure Integration' : 'Connect Now'}
                </button>
              </div>
            ))}
            <div className="terra-card p-6 bg-slate-50/50 border border-dashed border-slate-200 flex flex-col items-center justify-center text-center group cursor-pointer hover:bg-emerald-50/30 hover:border-emerald-200 transition-all">
              <div className="w-12 h-12 rounded-full border-2 border-dashed border-slate-200 flex items-center justify-center text-slate-300 mb-3 group-hover:border-emerald-200 group-hover:text-emerald-300 transition-all">
                <CloudArrowUp size={24} />
              </div>
              <div className="text-xs font-bold text-slate-400 group-hover:text-emerald-600 transition-all">Request New Integration</div>
            </div>
          </div>
        );
      case "billing":
        return (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="terra-card overflow-hidden bg-white border border-emerald-100 shadow-xl shadow-emerald-50">
              <div className="bg-gradient-to-r from-emerald-600 to-teal-600 p-8 text-white relative">
                <div className="relative z-10">
                  <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/20 backdrop-blur-md text-[10px] font-bold mb-4 border border-white/20">
                    <Tree weight="duotone" size={14} /> Terra Pro Plan
                  </div>
                  <h2 className="text-3xl font-black mb-2">$499 <span className="text-sm font-medium text-emerald-100">/ month</span></h2>
                  <p className="text-emerald-50/80 text-sm max-w-sm">Standard agency tier for up to 10 active productions and 50 team members.</p>
                </div>
                <div className="absolute right-0 top-0 bottom-0 w-1/3 opacity-20 pointer-events-none overflow-hidden">
                  <Lightning weight="fill" className="w-full h-full text-white translate-x-1/2" />
                </div>
              </div>
              <div className="p-8 grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <div className="text-xs font-bold text-slate-400 tracking-wider mb-1">Billing Cycle</div>
                  <div className="text-sm font-bold text-slate-900">Monthly Billing</div>
                  <div className="text-[10px] text-emerald-600 font-bold mt-1">Next payment: May 15, 2026</div>
                </div>
                <div>
                  <div className="text-xs font-bold text-slate-400 tracking-wider mb-1">Payment Method</div>
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-5 rounded bg-slate-900 flex items-center justify-center text-[8px] font-bold text-white">VISA</div>
                    <div className="text-sm font-bold text-slate-900">•••• 4242</div>
                  </div>
                  <button className="text-[10px] text-emerald-600 font-bold mt-1 hover:underline">Update card</button>
                </div>
                <div className="flex items-end">
                  <button className="w-full py-2.5 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-slate-800 transition-all">Manage Subscription</button>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-bold text-slate-900">Recent Invoices</h3>
              <div className="terra-card bg-white border border-slate-100 divide-y divide-slate-50">
                {[
                  { date: 'Apr 15, 2026', id: 'INV-2026-004', amount: '$499.00' },
                  { date: 'Mar 15, 2026', id: 'INV-2026-003', amount: '$499.00' },
                ].map(inv => (
                  <div key={inv.id} className="p-4 flex items-center justify-between hover:bg-slate-50/50 transition-colors">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-slate-50 flex items-center justify-center text-slate-400">
                        <CheckCircle size={20} />
                      </div>
                      <div>
                        <div className="text-sm font-bold text-slate-800">{inv.id}</div>
                        <div className="text-xs text-slate-500">{inv.date}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-6">
                      <span className="text-sm font-bold text-slate-900">{inv.amount}</span>
                      <button className="text-xs font-bold text-emerald-600 hover:text-emerald-700">Download</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        );
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-700 via-emerald-600 to-teal-700 p-10 text-white shadow-2xl shadow-emerald-200/50">
        <div className="relative z-10 flex flex-col md:flex-row items-center gap-12">
          <div className="flex-1 text-center md:text-left space-y-6">
            <h1 className="text-4xl md:text-5xl font-extrabold mb-4 tracking-tight leading-tight">
              Workspace <span className="text-emerald-300">Settings</span>
            </h1>
            <p className="text-emerald-50/90 text-lg max-w-xl leading-relaxed font-medium">
              Customize your sustainability cockpit. Manage team access, connect data pipelines, and control your subscription.
            </p>
          </div>
          <div className="w-56 h-56 md:w-72 md:h-72 shrink-0 relative">
            <div className="absolute inset-0 bg-emerald-400/20 rounded-full blur-[80px] animate-pulse" />
            <img 
              src={heroImage} 
              alt="" 
              className="relative z-10 w-full h-full object-contain drop-shadow-[0_20px_50px_rgba(0,0,0,0.3)]"
            />
          </div>
        </div>
        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-96 h-96 bg-white/5 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute bottom-0 left-0 -ml-20 -mb-20 w-96 h-96 bg-teal-400/10 rounded-full blur-[100px] pointer-events-none" />
      </div>

      {/* Tabs */}
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 pb-1 px-1">
        {[
          { id: "general", label: "General", icon: GearSix },
          { id: "team", label: "Team", icon: Users },
          { id: "integrations", label: "Integrations", icon: CloudArrowUp },
          { id: "billing", label: "Billing", icon: CreditCard },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id as any)}
            className={`flex items-center gap-2.5 px-6 py-3 text-sm font-bold transition-all relative ${
              activeTab === tab.id 
              ? "text-emerald-700" 
              : "text-slate-500 hover:text-slate-900"
            }`}
          >
            <tab.icon weight={activeTab === tab.id ? "duotone" : "regular"} size={20} />
            {tab.label}
            {activeTab === tab.id && (
              <div className="absolute bottom-[-1px] left-0 right-0 h-0.5 bg-emerald-600 rounded-full animate-in fade-in slide-in-from-bottom-1 duration-300" />
            )}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="min-h-[400px]">
        {renderTabContent()}
      </div>
    </div>
  );
}
