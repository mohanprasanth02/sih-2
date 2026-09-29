import React, { useEffect, useState } from 'react';
import {
  Scale,
  CheckCircle2,
  XCircle,
  Clock,
  FileText,
  Download,
  PlusCircle,
  Database,
  ArrowRight,
  TrendingUp,
  Award,
  Sparkles,
  ExternalLink,
  ShieldCheck,
  Search,
  Sliders,
  ChevronRight,
  BarChart3,
  Layers,
  Activity,
  Check,
  Play,
  RotateCcw
} from 'lucide-react';
import { NAWIDashboardStats, NAWIModelEvaluation } from '../../types';
import { api } from '../../api';
import { useI18n } from '../../i18n';

interface NAWIDashboardViewProps {
  onNavigate: (tab: string, evalId?: string) => void;
}

export const NAWIDashboardView: React.FC<NAWIDashboardViewProps> = ({ onNavigate }) => {
  const { t } = useI18n();
  const [stats, setStats] = useState<NAWIDashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const loadData = async () => {
    try {
      setLoading(true);
      const res = await api.getOIMLDashboardStats();
      setStats(res);
    } catch (err) {
      console.error('Failed to load OIML dashboard stats:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSeedDemo = async () => {
    try {
      setSeeding(true);
      await api.seedOIMLDemo();
      await loadData();
    } catch (err) {
      console.error('Seed demo error:', err);
    } finally {
      setSeeding(false);
    }
  };

  const filteredRecent = (stats?.recent_evaluations || []).filter((item) =>
    item.model_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.manufacturer_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    item.report_number.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-12 max-w-6xl mx-auto pb-16 animate-fade-in font-sans">
      {/* 1. Hero Section (Styled exactly like the reference image) */}
      <div className="text-center pt-8 pb-4 space-y-5">
        {/* Pill Announcement Badge */}
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full border border-zinc-200 bg-white text-xs font-medium text-zinc-800 shadow-sm hover:border-zinc-300 transition-all cursor-pointer">
          <span className="px-1.5 py-0.5 rounded-full bg-black text-white text-[10px] font-bold uppercase tracking-wider">
            OIML R 76
          </span>
          <span>{t('hero_badge')}</span>
          <ArrowRight className="w-3.5 h-3.5 text-zinc-500" />
        </div>

        {/* Big Bold Headline */}
        <h1 className="text-4xl sm:text-5xl lg:text-6xl font-display font-extrabold text-zinc-900 tracking-tight max-w-4xl mx-auto leading-[1.1]">
          {t('hero_title')}
        </h1>

        {/* Gray Subtitle */}
        <p className="text-zinc-600 text-sm sm:text-base max-w-2xl mx-auto leading-relaxed font-normal">
          {t('hero_subtitle')}
        </p>

        {/* Centered Pill Action Buttons */}
        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <button
            onClick={() => onNavigate('oiml-wizard')}
            className="bw-btn-primary px-6 py-2.5 text-xs font-semibold shadow-sm hover:shadow"
          >
            {t('btn_start_evaluation')}
          </button>

          <button
            onClick={() => onNavigate('oiml-standards')}
            className="bw-btn-secondary px-6 py-2.5 text-xs font-semibold"
          >
            {t('btn_explore_standards')}
          </button>
        </div>
      </div>

      {/* 2. Central Visual Showcase Card (Interactive Test Battery Terminal) */}
      <div className="bw-card p-6 sm:p-8 rounded-3xl border border-zinc-200/90 shadow-sm bg-gradient-to-b from-white to-zinc-50/50">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-zinc-200 pb-5">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-2xl bg-black text-white flex items-center justify-center shadow-sm">
              <Scale className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-base font-display font-bold text-zinc-900">
                {t('terminal_title')}
              </h2>
              <p className="text-xs text-zinc-500 font-mono">
                Model: SIM-SmartScale-15K &bull; Class III &bull; Max 15kg &bull; e=5g &bull; n=3,000
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleSeedDemo}
              disabled={seeding}
              className="bw-btn-secondary px-3.5 py-1.5 text-xs font-medium flex items-center space-x-1.5"
            >
              <Database className="w-3.5 h-3.5 text-zinc-700" />
              <span>{seeding ? '...' : t('btn_load_samples')}</span>
            </button>
            <span className="bw-badge-pass">
              {t('verified')}
            </span>
          </div>
        </div>

        {/* Live OLED Simulation Display */}
        <div className="mt-6 p-6 rounded-2xl bg-zinc-900 text-white shadow-inner">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-zinc-800 pb-4">
            <div className="flex items-center space-x-2">
              <div className="w-2.5 h-2.5 rounded-full bg-white animate-pulse" />
              <span className="font-mono text-xs font-bold text-zinc-400 uppercase tracking-widest">
                {t('digital_readout')}
              </span>
            </div>
            <div className="flex items-center space-x-3 font-mono text-xs text-zinc-400">
              <span>ZERO TRACKING: ON</span>
              <span>•</span>
              <span>FILTER: 24-BIT ADC</span>
              <span>•</span>
              <span className="text-white font-bold">STATUS: STABLE</span>
            </div>
          </div>

          <div className="my-6 text-center">
            <div className="text-5xl sm:text-6xl font-mono font-extrabold text-white tracking-wider">
              15.000 <span className="text-2xl text-zinc-400 font-sans">kg</span>
            </div>
            <p className="text-xs font-mono text-zinc-400 mt-2">
              L = 15.000 kg &bull; &Delta;L = 0.0025 kg &bull; Corrected Error E<sub>c</sub> = +0.0000 kg &bull; MPE = &plusmn;0.0075 kg
            </p>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-zinc-800 font-mono text-xs">
            <div className="p-2.5 rounded-xl bg-black/60 border border-zinc-800 text-center">
              <span className="text-zinc-500 text-[10px]">CLAUSE A.4.4</span>
              <div className="font-bold text-white mt-0.5">Weighing: PASS</div>
            </div>
            <div className="p-2.5 rounded-xl bg-black/60 border border-zinc-800 text-center">
              <span className="text-zinc-500 text-[10px]">CLAUSE A.4.10</span>
              <div className="font-bold text-white mt-0.5">Repeat: &Delta;=0.005kg</div>
            </div>
            <div className="p-2.5 rounded-xl bg-black/60 border border-zinc-800 text-center">
              <span className="text-zinc-500 text-[10px]">CLAUSE A.4.7</span>
              <div className="font-bold text-white mt-0.5">Corner Load: PASS</div>
            </div>
            <div className="p-2.5 rounded-xl bg-black/60 border border-zinc-800 text-center">
              <span className="text-zinc-500 text-[10px]">SEC 22 LM ACT</span>
              <div className="font-bold text-white mt-0.5">Seal: SHA-256 Valid</div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Authority / Trust Bar */}
      <div className="pt-4 text-center space-y-4">
        <div className="text-xs font-mono font-semibold uppercase tracking-widest text-zinc-400">
          {t('trusted_by')}
        </div>
        <div className="flex flex-wrap items-center justify-center gap-8 sm:gap-14 text-zinc-500 font-mono text-xs font-semibold opacity-75">
          <span>OIML RECOMMENDATION R 76-1</span>
          <span>NABL ISO/IEC 17025</span>
          <span>LEGAL METROLOGY ACT, 2009</span>
          <span>CSIR-NPL TRACEABLE</span>
          <span>OIML R 76-2 FORMAT</span>
        </div>
      </div>

      {/* 4. Section: Modular Metrological Intelligence */}
      <div className="space-y-6 pt-6">
        <div className="text-center space-y-2">
          <h2 className="text-2xl sm:text-3xl font-display font-bold text-zinc-900 tracking-tight">
            {t('modular_title')}
          </h2>
          <p className="text-xs sm:text-sm text-zinc-500 max-w-xl mx-auto">
            {t('modular_subtitle')}
          </p>
        </div>

        {/* 3 Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Card 1: Weighing Performance */}
          <div className="bw-card p-6 rounded-2xl flex flex-col justify-between space-y-4 group">
            <div className="w-full h-32 rounded-xl bg-zinc-100 flex items-center justify-center transition-colors group-hover:bg-zinc-200/70">
              <Activity className="w-8 h-8 text-zinc-700" />
            </div>
            <div className="space-y-1.5">
              <h3 className="text-base font-display font-bold text-zinc-900">
                {t('card_weighing_title')}
              </h3>
              <p className="text-xs text-zinc-500 leading-relaxed">
                {t('card_weighing_desc')}
              </p>
            </div>
            <button
              onClick={() => onNavigate('oiml-wizard')}
              className="text-xs font-semibold text-zinc-900 group-hover:text-black flex items-center space-x-1.5 pt-2"
            >
              <span>{t('card_weighing_link')}</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

          {/* Card 2: Repeatability & Eccentricity */}
          <div className="bw-card p-6 rounded-2xl flex flex-col justify-between space-y-4 group">
            <div className="w-full h-32 rounded-xl bg-zinc-100 flex items-center justify-center transition-colors group-hover:bg-zinc-200/70">
              <Layers className="w-8 h-8 text-zinc-700" />
            </div>
            <div className="space-y-1.5">
              <h3 className="text-base font-display font-bold text-zinc-900">
                {t('card_repeat_title')}
              </h3>
              <p className="text-xs text-zinc-500 leading-relaxed">
                {t('card_repeat_desc')}
              </p>
            </div>
            <button
              onClick={() => onNavigate('oiml-wizard')}
              className="text-xs font-semibold text-zinc-900 group-hover:text-black flex items-center space-x-1.5 pt-2"
            >
              <span>{t('card_repeat_link')}</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>

          {/* Card 3: Standardized Reports */}
          <div className="bw-card p-6 rounded-2xl flex flex-col justify-between space-y-4 group">
            <div className="w-full h-32 rounded-xl bg-zinc-100 flex items-center justify-center transition-colors group-hover:bg-zinc-200/70">
              <FileText className="w-8 h-8 text-zinc-700" />
            </div>
            <div className="space-y-1.5">
              <h3 className="text-base font-display font-bold text-zinc-900">
                {t('card_reports_title')}
              </h3>
              <p className="text-xs text-zinc-500 leading-relaxed">
                {t('card_reports_desc')}
              </p>
            </div>
            <button
              onClick={() => onNavigate('oiml-repository')}
              className="text-xs font-semibold text-zinc-900 group-hover:text-black flex items-center space-x-1.5 pt-2"
            >
              <span>{t('card_reports_link')}</span>
              <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </div>

      {/* 5. Recent Evaluations & Search Archive */}
      <div className="bw-card p-6 sm:p-8 rounded-2xl border border-zinc-200 space-y-5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-display font-bold text-zinc-900">
              {t('recent_evaluations')}
            </h2>
            <p className="text-xs text-zinc-500 font-mono">
              {t('recent_evaluations_sub')}
            </p>
          </div>

          <div className="relative w-full sm:w-72">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3.5 top-2.5" />
            <input
              type="text"
              placeholder={t('search_evaluations')}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="bw-input w-full pl-9 pr-3 py-2 text-xs"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="border-b border-zinc-200 text-zinc-500 font-mono bg-zinc-50/70">
                <th className="py-2.5 px-3">{t('th_report')}</th>
                <th className="py-2.5 px-3">{t('th_model')}</th>
                <th className="py-2.5 px-3">{t('th_manufacturer')}</th>
                <th className="py-2.5 px-3">{t('th_accuracy_class')}</th>
                <th className="py-2.5 px-3">{t('th_capacity')}</th>
                <th className="py-2.5 px-3">{t('th_status')}</th>
                <th className="py-2.5 px-3 text-right">{t('th_exports')}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-100 font-sans">
              {filteredRecent.length === 0 ? (
                <tr>
                  <td colSpan={7} className="py-8 text-center text-zinc-400">
                    No evaluations found. Click &quot;Load Sample Data&quot; to populate.
                  </td>
                </tr>
              ) : (
                filteredRecent.map((item) => {
                  const isApproved = item.status === 'APPROVED_COMPLIANT';
                  return (
                    <tr
                      key={item.id}
                      onClick={() => onNavigate('oiml-repository', item.id)}
                      className="hover:bg-zinc-50 cursor-pointer transition-colors"
                    >
                      <td className="py-3 px-3 font-mono font-bold text-zinc-900">
                        {item.report_number}
                      </td>
                      <td className="py-3 px-3 font-medium text-zinc-900">
                        {item.model_name}
                      </td>
                      <td className="py-3 px-3 text-zinc-600">
                        {item.manufacturer_name}
                      </td>
                      <td className="py-3 px-3">
                        <span className="px-2 py-0.5 rounded-full font-mono text-[10px] font-semibold bg-zinc-100 border border-zinc-200 text-zinc-800">
                          {item.accuracy_class}
                        </span>
                      </td>
                      <td className="py-3 px-3 font-mono font-bold text-zinc-900">
                        {item.max_capacity} {item.units}
                      </td>
                      <td className="py-3 px-3">
                        <span
                          className={`text-[10px] ${
                            isApproved
                              ? 'bw-badge-pass'
                              : 'bw-badge-neutral'
                          }`}
                        >
                          {isApproved ? t('compliant') : item.status.replace(/_/g, ' ')}
                        </span>
                      </td>
                      <td className="py-3 px-3 text-right">
                        <div className="flex items-center justify-end space-x-1.5" onClick={(e) => e.stopPropagation()}>
                          <a
                            href={api.getOIMLPdfUrl(item.id)}
                            download
                            className="px-2.5 py-1 rounded-full bg-zinc-100 hover:bg-black hover:text-white text-zinc-800 font-mono text-[10px] font-bold border border-zinc-200 transition-colors"
                          >
                            PDF
                          </a>
                          <a
                            href={api.getOIMLDocxUrl(item.id)}
                            download
                            className="px-2.5 py-1 rounded-full bg-zinc-100 hover:bg-black hover:text-white text-zinc-800 font-mono text-[10px] font-bold border border-zinc-200 transition-colors"
                          >
                            DOCX
                          </a>
                        </div>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
