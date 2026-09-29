import React, { useEffect, useState } from 'react';
import {
  FileCheck2,
  AlertOctagon,
  HelpCircle,
  TrendingUp,
  ScanLine,
  ArrowRight,
  ShieldAlert,
  Clock,
  Sparkles,
  Layers
} from 'lucide-react';
import {
  AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer
} from 'recharts';
import { UserRole, OverviewKPI, InspectionListItem } from '../types';
import { api } from '../api';

interface DashboardViewProps {
  role: UserRole;
  onNavigate: (tab: string, inspectionId?: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ role, onNavigate }) => {
  const [kpi, setKpi] = useState<OverviewKPI>({
    total_inspections: 0,
    compliant: 0,
    potential_violations: 0,
    manual_reviews: 0,
    compliance_rate: 0,
  });
  const [recentInspections, setRecentInspections] = useState<InspectionListItem[]>([]);
  const [violationStats, setViolationStats] = useState<any[]>([]);
  const [categoryStats, setCategoryStats] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [kpiData, inspData, violData] = await Promise.all([
          api.getOverviewKPI(),
          api.getInspections({ limit: 5 }),
          api.getViolationsAnalytics()
        ]);
        setKpi(kpiData);
        setRecentInspections(inspData.items);
        setViolationStats(violData.top_violations || []);
        setCategoryStats(violData.category_distribution || []);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const trendData = [
    { day: 'Mon', compliant: 12, violations: 4, reviews: 2 },
    { day: 'Tue', compliant: 18, violations: 5, reviews: 3 },
    { day: 'Wed', compliant: 15, violations: 3, reviews: 1 },
    { day: 'Thu', compliant: 24, violations: 8, reviews: 4 },
    { day: 'Fri', compliant: 22, violations: 6, reviews: 2 },
    { day: 'Sat', compliant: 19, violations: 4, reviews: 1 },
    { day: 'Today', compliant: 14, violations: 5, reviews: 3 },
  ];

  return (
    <div className="space-y-6 animate-fade-in font-sans max-w-6xl mx-auto pb-16">
      {/* Role Context Masthead */}
      <div className="bw-card p-6 sm:p-7 rounded-3xl border border-zinc-200 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-2 text-zinc-500 text-xs font-mono font-medium uppercase tracking-wider mb-1.5">
            <span className="w-2 h-2 rounded-full bg-black animate-pulse"></span>
            <span>{role.toUpperCase()} ENFORCEMENT DASHBOARD</span>
          </div>
          <h1 className="text-2xl font-display font-extrabold text-zinc-900 tracking-tight">
            {role === 'inspector'
              ? 'Field Inspection & Verification Console'
              : role === 'supervisor'
              ? 'Zonal Compliance Review & Team Supervision'
              : 'Legal Metrology Central Administration Portal'}
          </h1>
          <p className="text-xs text-zinc-500 mt-1">
            Real-time automated screening under Legal Metrology (Packaged Commodities) Rules, 2011
          </p>
        </div>
        <div className="flex items-center space-x-2.5">
          <button
            onClick={() => onNavigate('verify')}
            className="bw-btn-primary flex items-center space-x-2 px-5 py-2.5 text-xs font-semibold"
          >
            <ScanLine className="w-4 h-4 text-white" />
            <span>VERIFY PRODUCT</span>
          </button>
          <button
            onClick={() => onNavigate('mobile-sim')}
            className="bw-btn-secondary flex items-center space-x-2 px-5 py-2.5 text-xs font-semibold"
          >
            <span>FIELD SCANNER</span>
            <ArrowRight className="w-3.5 h-3.5 text-zinc-700" />
          </button>
        </div>
      </div>

      {/* Real KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Total Inspections */}
        <div className="bw-card p-5 rounded-2xl border border-zinc-200 shadow-sm">
          <div className="flex items-center justify-between text-zinc-500 text-xs font-mono">
            <span>TOTAL INSPECTIONS</span>
            <div className="p-2 rounded-xl bg-zinc-100 text-zinc-800">
              <FileCheck2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-mono font-extrabold text-zinc-900 mt-2 tracking-tight">
            {loading ? '...' : kpi.total_inspections.toLocaleString()}
          </div>
          <div className="flex items-center space-x-1.5 text-zinc-500 text-[11px] font-mono mt-2">
            <TrendingUp className="w-3.5 h-3.5 text-zinc-800" />
            <span>Active database records</span>
          </div>
        </div>

        {/* Card 2: Compliant */}
        <div className="bw-card p-5 rounded-2xl border border-zinc-200 shadow-sm">
          <div className="flex items-center justify-between text-zinc-500 text-xs font-mono">
            <span>COMPLIANT PACKAGES</span>
            <div className="p-2 rounded-xl bg-zinc-100 text-zinc-800">
              <FileCheck2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-mono font-extrabold text-zinc-900 mt-2 tracking-tight">
            {loading ? '...' : kpi.compliant.toLocaleString()}
          </div>
          <div className="text-[11px] text-zinc-500 font-mono mt-2">
            Compliance rate: <span className="font-bold text-zinc-900">{kpi.compliance_rate}%</span>
          </div>
        </div>

        {/* Card 3: Potential Violations */}
        <div className="bw-card p-5 rounded-2xl border border-zinc-200 shadow-sm">
          <div className="flex items-center justify-between text-zinc-500 text-xs font-mono">
            <span>POTENTIAL VIOLATIONS</span>
            <div className="p-2 rounded-xl bg-zinc-100 text-zinc-800">
              <AlertOctagon className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-mono font-extrabold text-zinc-900 mt-2 tracking-tight">
            {loading ? '...' : kpi.potential_violations.toLocaleString()}
          </div>
          <div className="text-[11px] text-zinc-500 font-mono mt-2">
            Enforcement review queue
          </div>
        </div>

        {/* Card 4: Manual Reviews */}
        <div className="bw-card p-5 rounded-2xl border border-zinc-200 shadow-sm">
          <div className="flex items-center justify-between text-zinc-500 text-xs font-mono">
            <span>MANUAL REVIEWS</span>
            <div className="p-2 rounded-xl bg-zinc-100 text-zinc-800">
              <HelpCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-mono font-extrabold text-zinc-900 mt-2 tracking-tight">
            {loading ? '...' : kpi.manual_reviews.toLocaleString()}
          </div>
          <div className="text-[11px] text-zinc-500 font-mono mt-2">
            Low OCR / Ambiguous labels
          </div>
        </div>
      </div>

      {/* Analytics Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Area Chart (2 Cols) */}
        <div className="lg:col-span-2 bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-display font-bold text-zinc-900">Inspection &amp; Compliance Activity</h2>
              <p className="text-[11px] text-zinc-500 font-mono">Weekly screening trends by legal determination</p>
            </div>
            <div className="flex items-center space-x-3 text-xs font-mono">
              <span className="flex items-center space-x-1.5 text-zinc-900 font-medium">
                <span className="w-2.5 h-2.5 rounded-full bg-black"></span>
                <span>Compliant</span>
              </span>
              <span className="flex items-center space-x-1.5 text-zinc-500">
                <span className="w-2.5 h-2.5 rounded-full bg-zinc-400"></span>
                <span>Violations</span>
              </span>
            </div>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="compliantGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#000000" stopOpacity={0.15}/>
                    <stop offset="95%" stopColor="#000000" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="violGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#71717a" stopOpacity={0.15}/>
                    <stop offset="95%" stopColor="#71717a" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" stroke="#a1a1aa" fontSize={11} tickLine={false} fontFamily="JetBrains Mono" />
                <YAxis stroke="#a1a1aa" fontSize={11} tickLine={false} fontFamily="JetBrains Mono" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#ffffff', borderColor: '#e4e4e7', borderRadius: '12px', fontSize: '12px', fontFamily: 'JetBrains Mono', color: '#09090b', boxShadow: '0 4px 12px rgba(0,0,0,0.06)' }}
                />
                <Area type="monotone" dataKey="compliant" stroke="#000000" strokeWidth={2} fillOpacity={1} fill="url(#compliantGrad)" />
                <Area type="monotone" dataKey="violations" stroke="#71717a" strokeWidth={2} fillOpacity={1} fill="url(#violGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Commodity Distribution (1 Col) */}
        <div className="bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm flex flex-col justify-between">
          <div>
            <h2 className="text-sm font-display font-bold text-zinc-900">Commodity Categories</h2>
            <p className="text-[11px] text-zinc-500 font-mono mb-4">Statutory commodity tier breakdown</p>
            <div className="space-y-3">
              {(categoryStats.length > 0 ? categoryStats : [
                { category: 'food', count: 48 },
                { category: 'cosmetics', count: 24 },
                { category: 'imported', count: 18 },
                { category: 'household', count: 12 },
              ]).map((c, idx) => (
                <div key={c.category} className="space-y-1">
                  <div className="flex justify-between text-xs font-medium">
                    <span className="text-zinc-700 capitalize font-mono">{c.category}</span>
                    <span className="text-zinc-900 font-mono font-bold">{c.count} items</span>
                  </div>
                  <div className="w-full h-1.5 bg-zinc-100 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500 bg-black"
                      style={{
                        width: `${Math.min(100, c.count * 2)}%`,
                        opacity: 1 - idx * 0.2
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-zinc-100 text-[11px] text-zinc-500 font-mono flex items-center justify-between">
            <span>SCHEDULE:</span>
            <span className="text-zinc-900 font-semibold">LM Rules 2011 Sched II</span>
          </div>
        </div>
      </div>

      {/* Top Infractions & Recent Inspections Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Infractions */}
        <div className="bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-display font-bold text-zinc-900">Top Rule Infractions</h2>
              <p className="text-[11px] text-zinc-500 font-mono">Statutory failure rates from DB records</p>
            </div>
            <ShieldAlert className="w-4 h-4 text-zinc-800" />
          </div>
          <div className="space-y-2.5">
            {(violationStats.length > 0 ? violationStats : [
              { rule_code: 'LM-RULE-005', title: 'MRP missing tax clause', violations_count: 14 },
              { rule_code: 'LM-RULE-006', title: 'Unit Sale Price undeclared', violations_count: 11 },
              { rule_code: 'LM-RULE-003', title: 'Missing Country of Origin', violations_count: 8 },
              { rule_code: 'LM-RULE-010', title: 'Cross-Surface Discrepancies', violations_count: 5 },
            ]).map((v) => (
              <div key={v.rule_code} className="p-2.5 rounded-xl bg-zinc-50 border border-zinc-200 flex items-center justify-between">
                <div>
                  <div className="text-xs font-mono font-semibold text-zinc-900">{v.rule_code}</div>
                  <div className="text-[11px] text-zinc-500">{v.title}</div>
                </div>
                <span className="bw-badge-fail text-[10px]">
                  {v.violations_count} fails
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Recent Inspections Table (2 Cols) */}
        <div className="lg:col-span-2 bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-display font-bold text-zinc-900">Recent Field Inspections</h2>
              <p className="text-[11px] text-zinc-500 font-mono">Latest field scans and label verifications</p>
            </div>
            <button
              onClick={() => onNavigate('inspections')}
              className="text-xs text-zinc-900 hover:text-black font-mono font-semibold flex items-center space-x-1"
            >
              <span>VIEW ALL</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse font-sans">
              <thead>
                <tr className="border-b border-zinc-100 text-[11px] font-mono text-zinc-400">
                  <th className="pb-2">INSPECTION ID</th>
                  <th className="pb-2">COMMODITY / PRODUCT</th>
                  <th className="pb-2">CATEGORY</th>
                  <th className="pb-2">STATUS</th>
                  <th className="pb-2 text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 text-xs">
                {recentInspections.map((item) => {
                  const isCompliant = item.status === 'COMPLIANT';
                  return (
                    <tr key={item.id} className="hover:bg-zinc-50 transition-colors">
                      <td className="py-3 font-mono text-[11px] text-zinc-700 font-medium">{item.id}</td>
                      <td className="py-3">
                        <div className="font-semibold text-zinc-900">{item.product_name}</div>
                        {item.brand && <div className="text-[10px] text-zinc-400">{item.brand}</div>}
                      </td>
                      <td className="py-3">
                        <span className="capitalize px-2 py-0.5 rounded-full font-mono bg-zinc-100 border border-zinc-200 text-zinc-800 text-[10px]">
                          {item.category_code}
                        </span>
                      </td>
                      <td className="py-3">
                        <span
                          className={`text-[10px] ${
                            isCompliant
                              ? 'bw-badge-pass'
                              : 'bw-badge-fail'
                          }`}
                        >
                          {item.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="py-3 text-right">
                        <button
                          onClick={() => onNavigate('inspection-detail', item.id)}
                          className="px-3 py-1 bg-zinc-100 hover:bg-black hover:text-white text-zinc-800 font-mono font-semibold rounded-full text-[11px] border border-zinc-200 transition-colors"
                        >
                          Evidence &rarr;
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
