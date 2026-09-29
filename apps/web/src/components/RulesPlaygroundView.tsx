import React, { useState, useEffect } from 'react';
import { Scale, Play, CheckCircle2, AlertTriangle, Shield, Info, ArrowRight } from 'lucide-react';
import { ComplianceRuleItem } from '../types';
import { api } from '../api';
import { useI18n } from '../i18n';

export const RulesPlaygroundView: React.FC = () => {
  const { t } = useI18n();
  const [rules, setRules] = useState<ComplianceRuleItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Testing Playground State
  const [testCategory, setTestCategory] = useState('food');
  const [testProductName, setTestProductName] = useState('Organic Almond Cookies');
  const [testNetQty, setTestNetQty] = useState('500 g');
  const [testMRP, setTestMRP] = useState('MRP Rs. 150.00 incl. of all taxes');
  const [testUSP, setTestUSP] = useState('₹0.30 per g');
  const [testMfg, setTestMfg] = useState('ABC Foods Pvt Ltd, Industrial Area, Phase II, New Delhi');
  const [testOrigin, setTestOrigin] = useState('India');
  const [testDate, setTestDate] = useState('PKD 08/2026');
  const [testCare, setTestCare] = useState('Helpline: 1800-111-222 customercare@abcfoods.com');

  const [testResult, setTestResult] = useState<any | null>(null);
  const [isRunningTest, setIsRunningTest] = useState(false);

  useEffect(() => {
    api.getRules()
      .then((data) => setRules(data))
      .catch((err) => console.error(err))
      .finally(() => setLoading(false));
  }, []);

  const handleExecuteRuleTest = async () => {
    try {
      setIsRunningTest(true);
      const payload = {
        category_code: testCategory,
        fields: {
          product_name: testProductName,
          net_quantity: testNetQty,
          mrp: testMRP,
          unit_sale_price: testUSP,
          manufacturer_packer: testMfg,
          country_of_origin: testOrigin,
          mfg_packing_date: testDate,
          consumer_care: testCare,
        },
      };
      const res = await api.testRules(payload);
      setTestResult(res);
    } catch (err: any) {
      alert(err.message || 'Rule test failed');
    } finally {
      setIsRunningTest(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-12 animate-fade-in">
      {/* Clean White Masthead */}
      <div className="bw-card p-8 bg-white border border-zinc-200">
        <div className="flex items-center space-x-2 text-zinc-900 text-xs font-bold uppercase tracking-wider mb-2">
          <Scale className="w-4 h-4 text-zinc-900" />
          <span className="font-mono">{t('rules_title')}</span>
        </div>
        <h1 className="text-2xl sm:text-3xl font-bold text-zinc-950 tracking-tight">
          {t('rules_title')}
        </h1>
        <p className="text-sm text-zinc-500 mt-2 max-w-2xl">
          {t('rules_sub')}
        </p>
      </div>

      {/* Interactive Rule Testing Playground */}
      <div className="bw-card p-8 bg-white border border-zinc-200 space-y-6 animate-slide-up">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between border-b border-zinc-200 pb-4 gap-4">
          <div>
            <h2 className="text-base font-bold text-zinc-900 flex items-center space-x-2">
              <Play className="w-4 h-4 text-zinc-900 fill-zinc-900" />
              <span>{t('rules_tool_title')}</span>
            </h2>
            <p className="text-xs text-zinc-500 mt-0.5">
              {t('rules_tool_sub')}
            </p>
          </div>
          <button
            onClick={handleExecuteRuleTest}
            disabled={isRunningTest}
            className="bw-btn-primary px-6 py-2.5 text-xs flex items-center space-x-2 self-start sm:self-auto shadow-sm"
          >
            <span>{isRunningTest ? t('rules_evaluating') : t('rules_test_btn')}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        {/* Inputs Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-xs font-semibold text-zinc-600 mb-1">{t('rules_category')}</label>
            <select
              value={testCategory}
              onChange={(e) => setTestCategory(e.target.value)}
              className="bw-input w-full px-3 py-2 text-xs text-zinc-900"
            >
              <option value="food">Packaged Food</option>
              <option value="cosmetics">Cosmetics & Toiletries</option>
              <option value="imported">Imported Commodity</option>
              <option value="household">Household / Cleaning</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-600 mb-1">{t('rules_product_name')}</label>
            <input
              type="text"
              value={testProductName}
              onChange={(e) => setTestProductName(e.target.value)}
              className="bw-input w-full px-3 py-2 text-xs text-zinc-900"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-600 mb-1">{t('rules_net_qty')}</label>
            <input
              type="text"
              value={testNetQty}
              onChange={(e) => setTestNetQty(e.target.value)}
              placeholder="e.g. 500 g"
              className="bw-input w-full px-3 py-2 text-xs text-zinc-900 font-mono"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-600 mb-1">{t('rules_mrp')}</label>
            <input
              type="text"
              value={testMRP}
              onChange={(e) => setTestMRP(e.target.value)}
              placeholder="e.g. MRP Rs. 150.00 incl. of all taxes"
              className="bw-input w-full px-3 py-2 text-xs text-zinc-900"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-600 mb-1">{t('rules_usp')}</label>
            <input
              type="text"
              value={testUSP}
              onChange={(e) => setTestUSP(e.target.value)}
              placeholder="e.g. ₹0.30 per g"
              className="bw-input w-full px-3 py-2 text-xs text-zinc-900"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-zinc-600 mb-1">{t('rules_date')}</label>
            <input
              type="text"
              value={testDate}
              onChange={(e) => setTestDate(e.target.value)}
              placeholder="e.g. PKD 08/2026"
              className="bw-input w-full px-3 py-2 text-xs text-zinc-900"
            />
          </div>

          <div className="sm:col-span-2">
            <label className="block text-xs font-semibold text-zinc-600 mb-1">{t('rules_mfg')}</label>
            <input
              type="text"
              value={testMfg}
              onChange={(e) => setTestMfg(e.target.value)}
              className="bw-input w-full px-3 py-2 text-xs text-zinc-900"
            />
          </div>
        </div>

        {/* Evaluation Output */}
        {testResult && (
          <div className="p-5 rounded-2xl bg-zinc-50 border border-zinc-200 space-y-4 animate-scale-in">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-zinc-900 uppercase tracking-wider font-mono">
                {t('rules_result_title')}:
              </span>
              <span
                className={`px-3 py-1 rounded-full text-xs font-bold font-mono tracking-wider ${
                  testResult.overall_status === 'COMPLIANT'
                    ? 'bw-badge-pass'
                    : 'bw-badge-fail'
                }`}
              >
                {testResult.overall_status}
              </span>
            </div>

            <div className="space-y-2 max-h-60 overflow-y-auto">
              {testResult.evaluated_rules.map((r: any, idx: number) => (
                <div key={idx} className="p-3 rounded-xl bg-white border border-zinc-200 text-xs flex items-start justify-between gap-4 shadow-sm">
                  <div>
                    <div className="font-semibold text-zinc-900">
                      <span className="font-mono text-zinc-500 mr-2">{r.rule_code}</span>
                      {r.legal_reference} — {r.title}
                    </div>
                    <div className="text-xs text-zinc-500 mt-1">{r.reason}</div>
                  </div>
                  <span
                    className={`px-2.5 py-0.5 rounded-full text-[11px] font-mono font-bold shrink-0 ${
                      r.status === 'PASS'
                        ? 'bg-zinc-100 text-zinc-900 border border-zinc-300'
                        : r.status === 'FAIL'
                        ? 'bg-zinc-950 text-white'
                        : 'bg-zinc-100 text-zinc-600'
                    }`}
                  >
                    {r.status}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Official Legal Rules Table */}
      <div className="bw-card p-8 bg-white border border-zinc-200 space-y-4">
        <h2 className="text-base font-bold text-zinc-900 flex items-center space-x-2">
          <Info className="w-4 h-4 text-zinc-700" />
          <span>{t('rules_codified_list')}</span>
        </h2>

        <div className="space-y-3">
          {rules.map((r) => (
            <div key={r.id} className="p-4 rounded-xl bg-zinc-50 border border-zinc-200/80 space-y-1.5 hover:border-zinc-300 transition-colors">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <span className="font-mono text-xs font-bold text-zinc-950">{r.code}</span>
                  <span className="px-2 py-0.5 rounded-md text-[10px] font-mono bg-white border border-zinc-200 text-zinc-600">
                    {r.legal_reference}
                  </span>
                  <span className="px-2 py-0.5 rounded-md text-[10px] font-mono bg-zinc-200/60 text-zinc-700">
                    v{r.version}
                  </span>
                </div>
                <span
                  className={`text-[10px] px-2.5 py-0.5 rounded-full font-bold font-mono ${
                    r.severity === 'CRITICAL' ? 'bg-zinc-900 text-white' : 'bg-zinc-200 text-zinc-800'
                  }`}
                >
                  {r.severity}
                </span>
              </div>
              <div className="text-xs font-bold text-zinc-900">{r.title}</div>
              <p className="text-xs text-zinc-500 leading-relaxed">{r.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
