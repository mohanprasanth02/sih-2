import React, { useState, useEffect } from 'react';
import { Cpu, CheckCircle2, Activity, Server, Database, HardDrive, Shield } from 'lucide-react';
import { api } from '../api';
import { useI18n } from '../i18n';

export const AIModelsView: React.FC = () => {
  const { t } = useI18n();
  const [modelData, setModelData] = useState<any[]>([]);
  const [health, setHealth] = useState<any>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getAIModels(), api.getHealth()])
      .then(([models, healthRes]) => {
        setModelData(models.models || []);
        setHealth(healthRes);
      })
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12 animate-fade-in">
      {/* Masthead Header */}
      <div className="bw-card p-8 bg-white border border-zinc-200">
        <div className="flex items-center space-x-2 text-zinc-900 text-xs font-bold uppercase tracking-wider mb-2">
          <Cpu className="w-4 h-4 text-zinc-900" />
          <span className="font-mono">{t('ai_telemetry_title')}</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-zinc-950 tracking-tight">
          {t('ai_telemetry_title')}
        </h1>
        <p className="text-sm text-zinc-500 mt-2 max-w-2xl">
          {t('ai_telemetry_sub')}
        </p>
      </div>

      {/* System Health Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
        <div className="bw-card p-6 bg-white border border-zinc-200 flex items-center justify-between">
          <div>
            <span className="text-xs text-zinc-500 font-semibold">{t('ai_fastapi')}</span>
            <div className="text-xl font-bold text-zinc-950 mt-1 flex items-center space-x-2">
              <span>{t('ai_operational')}</span>
              <span className="w-2 h-2 rounded-full bg-zinc-950 animate-pulse-beacon"></span>
            </div>
            <span className="text-[11px] text-zinc-400 font-mono">Port 8005 • Uvicorn</span>
          </div>
          <div className="p-3 rounded-2xl bg-zinc-100 text-zinc-900">
            <Server className="w-5 h-5" />
          </div>
        </div>

        <div className="bw-card p-6 bg-white border border-zinc-200 flex items-center justify-between">
          <div>
            <span className="text-xs text-zinc-500 font-semibold">{t('ai_db')}</span>
            <div className="text-xl font-bold text-zinc-950 mt-1 flex items-center space-x-2">
              <span>{t('ai_connected')}</span>
              <span className="w-2 h-2 rounded-full bg-zinc-950"></span>
            </div>
            <span className="text-[11px] text-zinc-400 font-mono">SQLite / SQLAlchemy</span>
          </div>
          <div className="p-3 rounded-2xl bg-zinc-100 text-zinc-900">
            <Database className="w-5 h-5" />
          </div>
        </div>

        <div className="bw-card p-6 bg-white border border-zinc-200 flex items-center justify-between">
          <div>
            <span className="text-xs text-zinc-500 font-semibold">{t('ai_storage')}</span>
            <div className="text-xl font-bold text-zinc-950 mt-1 flex items-center space-x-2">
              <span>{t('ai_encrypted')}</span>
              <span className="w-2 h-2 rounded-full bg-zinc-950"></span>
            </div>
            <span className="text-[11px] text-zinc-400 font-mono">Private Object Mount</span>
          </div>
          <div className="p-3 rounded-2xl bg-zinc-100 text-zinc-900">
            <HardDrive className="w-5 h-5" />
          </div>
        </div>

        <div className="bw-card p-6 bg-white border border-zinc-200 flex items-center justify-between">
          <div>
            <span className="text-xs text-zinc-500 font-semibold">{t('ai_engine')}</span>
            <div className="text-xl font-bold text-zinc-950 mt-1 flex items-center space-x-2">
              <span>{t('ai_deterministic')}</span>
              <span className="w-2 h-2 rounded-full bg-zinc-950"></span>
            </div>
            <span className="text-[11px] text-zinc-400 font-mono">LM Rules 2011 Codified</span>
          </div>
          <div className="p-3 rounded-2xl bg-zinc-100 text-zinc-900">
            <Shield className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* AI Models Telemetry Table */}
      <div className="bw-card p-8 bg-white border border-zinc-200 space-y-4 animate-slide-up stagger-1">
        <h2 className="text-base font-bold text-zinc-900 flex items-center space-x-2">
          <Activity className="w-4 h-4 text-zinc-900" />
          <span>{t('ai_active_components')}</span>
        </h2>

        <div className="space-y-3">
          {modelData.map((m, idx) => (
            <div
              key={idx}
              className="p-5 rounded-xl bg-zinc-50 border border-zinc-200 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-zinc-300 transition-colors"
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs font-bold text-zinc-950">{m.name}</span>
                  <span className="px-2 py-0.5 rounded-md text-[10px] font-mono bg-white border border-zinc-200 text-zinc-700">
                    {m.type}
                  </span>
                </div>
                <p className="text-xs text-zinc-600">{m.purpose}</p>
              </div>

              <div className="flex items-center space-x-6 text-xs shrink-0">
                <div>
                  <div className="text-[10px] text-zinc-400 uppercase font-semibold">{t('ai_latency')}</div>
                  <div className="font-mono font-bold text-zinc-900">{m.avg_latency_ms} ms</div>
                </div>
                <div>
                  <div className="text-[10px] text-zinc-400 uppercase font-semibold">Failure Rate</div>
                  <div className="font-mono font-bold text-zinc-900">{m.failure_rate_pct}%</div>
                </div>
                <span className="bw-badge-pass text-xs">
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  <span>ACTIVE</span>
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
