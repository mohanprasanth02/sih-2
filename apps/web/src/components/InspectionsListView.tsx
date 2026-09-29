import React, { useState, useEffect } from 'react';
import { Search, Filter, FileCheck2, ArrowRight, AlertTriangle, ShieldAlert } from 'lucide-react';
import { InspectionListItem } from '../types';
import { api } from '../api';

interface InspectionsListViewProps {
  onSelectInspection: (id: string) => void;
  initialFilter?: string;
}

export const InspectionsListView: React.FC<InspectionsListViewProps> = ({
  onSelectInspection,
  initialFilter,
}) => {
  const [inspections, setInspections] = useState<InspectionListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState(initialFilter || 'ALL');
  const [categoryFilter, setCategoryFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [statusFilter, categoryFilter, search]);

  const loadData = async () => {
    try {
      setLoading(true);
      const res = await api.getInspections({
        status: statusFilter,
        category: categoryFilter,
        search: search.trim() || undefined,
      });
      setInspections(res.items);
      setTotal(res.total);
    } catch (err) {
      console.error('Failed to load inspections:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-16 animate-fade-in font-sans">
      {/* Header */}
      <div className="bw-card p-6 sm:p-7 rounded-3xl border border-zinc-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-display font-extrabold text-zinc-900 tracking-tight">Inspection Records Repository</h1>
          <p className="text-xs text-zinc-500 mt-1">
            Browse and filter field inspections conducted under Legal Metrology Rules 2011
          </p>
        </div>
        <div className="text-xs text-zinc-500 font-mono">
          Showing <span className="text-zinc-900 font-bold">{inspections.length}</span> of {total} records
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="bw-card p-4 rounded-2xl border border-zinc-200 shadow-sm flex flex-col md:flex-row items-center gap-3">
        {/* Search */}
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-zinc-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by Docket ID, Product Name, or Brand..."
            className="bw-input w-full pl-10 pr-4 py-2 text-xs"
          />
        </div>

        {/* Status Filter */}
        <div className="flex items-center space-x-2 w-full md:w-auto">
          <Filter className="w-4 h-4 text-zinc-400 shrink-0" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bw-input px-3 py-2 text-xs bg-white font-medium"
          >
            <option value="ALL">All Statuses</option>
            <option value="COMPLIANT">Compliant</option>
            <option value="NEEDS_REVIEW">Needs Review</option>
            <option value="NON_COMPLIANT">Non Compliant</option>
            <option value="PENDING">Pending</option>
          </select>

          {/* Category Filter */}
          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value)}
            className="bw-input px-3 py-2 text-xs bg-white font-medium"
          >
            <option value="ALL">All Categories</option>
            <option value="food">Food &amp; Beverages</option>
            <option value="cosmetics">Cosmetics</option>
            <option value="imported">Imported</option>
            <option value="household">Household</option>
            <option value="electronics">Electronics</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="bw-card p-6 sm:p-7 rounded-3xl border border-zinc-200 shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-zinc-200 text-zinc-500 font-mono bg-zinc-50/70">
                <th className="py-2.5 px-3">Docket ID</th>
                <th className="py-2.5 px-3">Commodity &amp; Brand</th>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3">Surfaces</th>
                <th className="py-2.5 px-3">Legal Status</th>
                <th className="py-2.5 px-3">Inspection Date</th>
                <th className="py-2.5 px-3 text-right">Evidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 font-sans">
              {inspections.map((item) => {
                const isCompliant = item.status === 'COMPLIANT';
                const isFail = item.status === 'NON_COMPLIANT';
                return (
                  <tr key={item.id} className="hover:bg-zinc-50 transition-colors">
                    <td className="py-3 px-3 font-mono text-[11px] text-zinc-900 font-semibold">
                      {item.id}
                      {item.is_demo && (
                        <span className="block text-[9px] text-zinc-500 font-normal">DEMO</span>
                      )}
                    </td>
                    <td className="py-3 px-3">
                      <div className="font-semibold text-zinc-900">{item.product_name}</div>
                      {item.brand && <div className="text-[10px] text-zinc-400">{item.brand}</div>}
                    </td>
                    <td className="py-3 px-3">
                      <span className="capitalize px-2 py-0.5 rounded-full bg-zinc-100 border border-zinc-200 text-zinc-800 text-[10px]">
                        {item.category_code}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-zinc-500 font-mono">
                      <span className="px-2 py-0.5 rounded-full bg-zinc-100 border border-zinc-200 text-[10px]">
                        {item.image_count} surfaces
                      </span>
                      {item.conflicts_count > 0 && (
                        <span className="ml-1.5 px-2 py-0.5 rounded-full bg-black text-white text-[9px] font-bold">
                          CONFLICT
                        </span>
                      )}
                    </td>
                    <td className="py-3 px-3">
                      <span
                        className={`text-[10px] ${
                          isCompliant
                            ? 'bw-badge-pass'
                            : isFail
                            ? 'bw-badge-fail'
                            : 'bw-badge-neutral'
                        }`}
                      >
                        {item.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-zinc-500 font-mono text-[11px]">
                      {item.created_at ? new Date(item.created_at).toLocaleDateString() : ''}
                    </td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => onSelectInspection(item.id)}
                        className="px-3.5 py-1 bg-zinc-100 hover:bg-black hover:text-white text-zinc-800 font-semibold rounded-full text-xs transition-colors flex items-center space-x-1 ml-auto border border-zinc-200"
                      >
                        <span>Examine</span>
                        <ArrowRight className="w-3 h-3" />
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
  );
};
