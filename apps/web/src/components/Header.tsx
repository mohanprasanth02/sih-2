import React, { useState, useEffect } from 'react';
import { Shield, Activity, UserCircle2, Scale, Package, LogOut, FileText } from 'lucide-react';
import { UserRole } from '../types';
import { api } from '../api';
import { useI18n } from '../i18n';

interface HeaderProps {
  currentRole: UserRole;
  onRoleChange: (role: UserRole) => void;
  currentUser: { email: string; name: string };
  onLogout: () => void;
  activeModule: 'oiml' | 'labelguard';
  onModuleChange: (mod: 'oiml' | 'labelguard') => void;
}

export const Header: React.FC<HeaderProps> = ({
  currentRole,
  onRoleChange,
  currentUser,
  onLogout,
  activeModule,
  onModuleChange,
}) => {
  const { language, setLanguage, t } = useI18n();
  const [healthStatus, setHealthStatus] = useState<string>('ONLINE');

  useEffect(() => {
    api.getHealth()
      .then((data) => setHealthStatus(data.status || 'ONLINE'))
      .catch(() => setHealthStatus('OFFLINE'));
  }, []);

  return (
    <header className="h-16 bg-white/95 backdrop-blur-md border-b border-zinc-200/80 flex items-center justify-between px-6 sticky top-0 z-40">
      {/* Left Masthead */}
      <div className="flex items-center space-x-3.5">
        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-black text-white font-extrabold shadow-sm transition-transform hover:scale-105">
          <Scale className="w-4 h-4 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-display font-extrabold text-sm tracking-tight text-zinc-900">
              {activeModule === 'oiml' ? 'OIML R 76' : 'LABELGUARD'}
            </span>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded-full font-bold uppercase tracking-wider bg-zinc-100 text-zinc-800 border border-zinc-200">
              {activeModule === 'oiml' ? 'Pattern Evaluation' : 'Rules 2011'}
            </span>
          </div>
          <p className="text-[11px] text-zinc-500 font-sans hidden sm:block">
            {activeModule === 'oiml'
              ? 'Non-Automatic Weighing Instruments • Legal Metrology Act, 2009'
              : 'Packaged Commodities Automated Compliance'}
          </p>
        </div>
      </div>

      {/* Center Minimalist Pill Switcher */}
      <div className="hidden md:flex items-center bg-zinc-100/80 p-1 rounded-full border border-zinc-200 space-x-1">
        <button
          onClick={() => onModuleChange('oiml')}
          className={`flex items-center space-x-2 px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
            activeModule === 'oiml'
              ? 'bg-black text-white shadow-sm'
              : 'text-zinc-600 hover:text-black hover:bg-zinc-200/60'
          }`}
        >
          <Scale className="w-3.5 h-3.5" />
          <span>NAWI Model Approval (OIML R 76)</span>
        </button>

        <button
          onClick={() => onModuleChange('labelguard')}
          className={`flex items-center space-x-2 px-4 py-1.5 rounded-full text-xs font-semibold transition-all ${
            activeModule === 'labelguard'
              ? 'bg-black text-white shadow-sm'
              : 'text-zinc-600 hover:text-black hover:bg-zinc-200/60'
          }`}
        >
          <Package className="w-3.5 h-3.5" />
          <span>Packaged Commodities</span>
        </button>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-2.5">
        {/* Language Switcher Pill */}
        <div className="flex items-center bg-zinc-100 rounded-full p-0.5 border border-zinc-200 text-xs font-semibold">
          <button
            onClick={() => setLanguage('en')}
            className={`px-2.5 py-1 rounded-full text-[11px] transition-all ${
              language === 'en'
                ? 'bg-black text-white shadow-sm font-bold'
                : 'text-zinc-600 hover:text-black'
            }`}
          >
            EN
          </button>
          <button
            onClick={() => setLanguage('hi')}
            className={`px-2.5 py-1 rounded-full text-[11px] transition-all ${
              language === 'hi'
                ? 'bg-black text-white shadow-sm font-bold'
                : 'text-zinc-600 hover:text-black'
            }`}
          >
            हिंदी
          </button>
        </div>

        {/* User Manual PDF Download */}
        <a
          href="/api/v1/oiml/user-manual"
          download="NAWI_OIML_R76_Application_User_Manual.pdf"
          target="_blank"
          rel="noreferrer"
          title="Download Complete PDF User Manual with all Scenarios & Data"
          className="hidden md:flex items-center space-x-1.5 px-3 py-1 rounded-full bg-zinc-900 text-white hover:bg-black text-[11px] font-mono font-bold transition-all shadow-sm"
        >
          <FileText className="w-3.5 h-3.5 text-white" />
          <span>User Manual (PDF)</span>
        </a>

        {/* Core Status indicator */}
        <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1 rounded-full bg-zinc-100 border border-zinc-200 text-[11px] font-mono">
          <div className="w-1.5 h-1.5 rounded-full bg-black animate-pulse" />
          <span className="text-zinc-500 font-sans">{t('core_status')}</span>
          <span className="text-zinc-900 font-bold">{healthStatus}</span>
        </div>

        {/* Role Selector */}
        <div className="flex items-center bg-zinc-100 rounded-full p-1 border border-zinc-200">
          {(['inspector', 'supervisor', 'admin', 'viewer'] as UserRole[]).map((r) => (
            <button
              key={r}
              onClick={() => onRoleChange(r)}
              className={`px-2.5 py-1 text-xs font-medium rounded-full transition-all capitalize ${
                currentRole === r
                  ? 'bg-black text-white font-semibold shadow-sm'
                  : 'text-zinc-600 hover:text-black'
              }`}
            >
              {t(`role_${r}`)}
            </button>
          ))}
        </div>

        {/* User Info & Logout */}
        <div className="flex items-center space-x-2.5 pl-2 border-l border-zinc-200">
          <div className="text-right hidden lg:block">
            <div className="text-xs font-bold text-zinc-900">{currentUser.name}</div>
            <div className="text-[10px] text-zinc-500 uppercase font-mono">{t(`role_${currentRole}`)}</div>
          </div>
          <button
            onClick={onLogout}
            title="Sign out / Switch account"
            className="p-1.5 rounded-full bg-zinc-100 hover:bg-zinc-200 text-zinc-700 hover:text-black transition-colors border border-zinc-200"
          >
            <UserCircle2 className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
