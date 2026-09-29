import React from 'react';
import {
  LayoutDashboard,
  ScanLine,
  FileCheck2,
  AlertTriangle,
  Scale,
  BarChart3,
  Smartphone,
  Cpu,
  Info,
  CheckCircle,
  Package
} from 'lucide-react';
import { UserRole } from '../types';
import { useI18n } from '../i18n';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  role: UserRole;
  pendingReviewCount?: number;
  activeModule?: 'oiml' | 'labelguard';
}

interface NavItem {
  id: string;
  labelKey: string;
  icon: any;
  highlight?: boolean;
  badge?: string | number;
  badgeColor?: string;
  accent?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  role,
  pendingReviewCount = 3,
  activeModule = 'oiml',
}) => {
  const { t } = useI18n();

  const oimlNavItems: NavItem[] = [
    { id: 'oiml-dashboard', labelKey: 'nav_nawi_dashboard', icon: LayoutDashboard },
    { id: 'oiml-wizard', labelKey: 'nav_new_evaluation', icon: Scale, highlight: true },
    { id: 'oiml-repository', labelKey: 'nav_reports_history', icon: FileCheck2 },
    { id: 'oiml-standards', labelKey: 'nav_standards_explorer', icon: Info },
  ];

  const labelguardNavItems: NavItem[] = [
    { id: 'dashboard', labelKey: 'nav_dashboard', icon: LayoutDashboard },
    { id: 'verify', labelKey: 'nav_verify_product', icon: ScanLine, highlight: true },
    { id: 'inspections', labelKey: 'nav_inspections', icon: FileCheck2 },
    {
      id: 'review-queue',
      labelKey: 'nav_review_queue',
      icon: AlertTriangle,
      badge: pendingReviewCount > 0 ? pendingReviewCount : undefined,
      badgeColor: 'bg-zinc-100 text-zinc-900 border border-zinc-200',
    },
    { id: 'rules', labelKey: 'nav_rules_playground', icon: Scale },
    { id: 'analytics', labelKey: 'nav_analytics', icon: BarChart3 },
    { id: 'mobile-sim', labelKey: 'nav_mobile_sim', icon: Smartphone, accent: true },
    { id: 'ai-models', labelKey: 'nav_ai_models', icon: Cpu },
  ];

  const navItems = activeModule === 'oiml' ? oimlNavItems : labelguardNavItems;

  return (
    <aside className="w-64 bg-white border-r border-zinc-200/80 flex flex-col justify-between py-5 px-3 min-h-[calc(100vh-4rem)]">
      <div className="space-y-6">
        {/* Navigation list */}
        <div className="space-y-1">
          <div className="px-3 pb-2 text-[10px] font-mono font-bold tracking-widest text-zinc-400 uppercase">
            {activeModule === 'oiml' ? 'OIML R 76 Modules' : 'Commodity Modules'}
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onSelectTab(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-black text-white font-bold shadow-sm'
                    : item.highlight
                    ? 'text-zinc-900 hover:bg-zinc-100 border border-zinc-200 font-semibold'
                    : 'text-zinc-600 hover:bg-zinc-100 hover:text-black'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-zinc-500'}`} />
                  <span className="font-sans">{t(item.labelKey)}</span>
                </div>
                {item.badge && (
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full font-bold ${item.badgeColor || 'bg-zinc-100 text-zinc-800'}`}>
                    {item.badge}
                  </span>
                )}
                {item.accent && (
                  <span className="text-[9px] font-mono px-2 py-0.5 rounded-full font-bold bg-zinc-100 text-zinc-800 border border-zinc-200">
                    LIVE
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Statutory Footnote */}
      <div className="p-3.5 bg-zinc-50 rounded-xl border border-zinc-200 text-[11px] space-y-1.5 font-sans">
        <div className="flex items-center space-x-1.5 text-zinc-900 font-bold text-xs">
          <Info className="w-3.5 h-3.5 text-zinc-900" />
          <span>{t('statutory_authority')}</span>
        </div>
        <p className="text-[10px] leading-relaxed text-zinc-500">
          {activeModule === 'oiml'
            ? t('statutory_footnote_oiml')
            : t('statutory_footnote_labelguard')}
        </p>
      </div>
    </aside>
  );
};
