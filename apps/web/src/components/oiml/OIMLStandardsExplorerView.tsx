import React, { useState } from 'react';
import {
  Scale,
  Award,
  Sliders,
  CheckCircle2,
  AlertCircle,
  FileCheck,
  ExternalLink,
  ShieldAlert,
  Info
} from 'lucide-react';
import { AccuracyClassType } from '../../types';

export const OIMLStandardsExplorerView: React.FC = () => {
  const [selectedClass, setSelectedClass] = useState<AccuracyClassType>('Class III');
  const [simLoad, setSimLoad] = useState<number>(5.0);
  const [simMax, setSimMax] = useState<number>(15.0);
  const [simE, setSimE] = useState<number>(0.005);
  const [isInService, setIsInService] = useState<boolean>(false);

  // Calculate MPE based on OIML Table 6
  const mInE = simE > 0 ? simLoad / simE : 0;
  let mpeE = 1.5;

  if (selectedClass === 'Class I') {
    if (mInE <= 50000) mpeE = 0.5;
    else if (mInE <= 200000) mpeE = 1.0;
    else mpeE = 1.5;
  } else if (selectedClass === 'Class II') {
    if (mInE <= 5000) mpeE = 0.5;
    else if (mInE <= 20000) mpeE = 1.0;
    else mpeE = 1.5;
  } else if (selectedClass === 'Class III') {
    if (mInE <= 500) mpeE = 0.5;
    else if (mInE <= 2000) mpeE = 1.0;
    else mpeE = 1.5;
  } else if (selectedClass === 'Class IIII') {
    if (mInE <= 50) mpeE = 0.5;
    else if (mInE <= 200) mpeE = 1.0;
    else mpeE = 1.5;
  }

  if (isInService) mpeE *= 2.0;
  const mpeUnit = mpeE * simE;

  const classSpecs: Record<AccuracyClassType, {
    designation: string;
    eMin: string;
    nMin: number;
    nMax: string;
    minCapacity: string;
    typical: string;
  }> = {
    'Class I': {
      designation: 'Special Accuracy',
      eMin: 'e \u2265 0.001 g',
      nMin: 50000,
      nMax: 'No Limit',
      minCapacity: '100 e',
      typical: 'Analytical microbalances, mass comparators, high-precision research instruments.'
    },
    'Class II': {
      designation: 'High Accuracy',
      eMin: '0.001 g \u2264 e \u2264 0.05 g or e \u2265 0.1 g',
      nMin: 100,
      nMax: '100,000',
      minCapacity: '20 e to 50 e',
      typical: 'Jewellery scales, laboratory precision balances, pharmaceutical prescription scales.'
    },
    'Class III': {
      designation: 'Medium Accuracy',
      eMin: '0.1 g \u2264 e \u2264 2 g or e \u2265 5 g',
      nMin: 100,
      nMax: '10,000',
      minCapacity: '20 e',
      typical: 'Commercial retail scales, price-computing scales, platform scales, weighbridges, crane scales.'
    },
    'Class IIII': {
      designation: 'Ordinary Accuracy',
      eMin: 'e \u2265 5 g',
      nMin: 100,
      nMax: '1,000',
      minCapacity: '10 e',
      typical: 'Coarse aggregate scales, freight sorting scales, non-critical industrial weighing.'
    }
  };

  const currentSpec = classSpecs[selectedClass];

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-16 animate-fade-in font-sans">
      {/* Title Header */}
      <div className="bw-card p-6 sm:p-8 rounded-3xl border border-zinc-200 shadow-sm space-y-2">
        <div className="inline-flex items-center space-x-2 text-zinc-500 text-xs font-mono font-medium uppercase tracking-wider">
          <Award className="w-3.5 h-3.5 text-zinc-900" />
          <span>STATUTORY METROLOGICAL SPECIFICATIONS</span>
        </div>
        <h1 className="text-2xl font-display font-extrabold text-zinc-900 tracking-tight">
          OIML Recommendation R 76-1:2006 (E) Standards &amp; MPE Simulator
        </h1>
        <p className="text-xs text-zinc-500 max-w-3xl leading-relaxed">
          Explore accuracy class specifications, maximum permissible error (MPE) thresholds on initial and in-service verification, and prescribed pattern evaluation test requirements enforced under the Legal Metrology Act, 2009.
        </p>
      </div>

      {/* Class Selector Tabs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {(['Class I', 'Class II', 'Class III', 'Class IIII'] as AccuracyClassType[]).map((cls) => {
          const isSelected = selectedClass === cls;
          return (
            <button
              key={cls}
              onClick={() => setSelectedClass(cls)}
              className={`p-5 rounded-2xl border text-left transition-all ${
                isSelected
                  ? 'bg-black text-white border-black shadow-md font-bold'
                  : 'bg-white border-zinc-200 text-zinc-700 hover:border-zinc-300 hover:bg-zinc-50'
              }`}
            >
              <div className="text-sm font-display font-bold">{cls}</div>
              <div className={`text-[11px] mt-1 ${isSelected ? 'text-zinc-300' : 'text-zinc-500'}`}>
                {classSpecs[cls].designation}
              </div>
            </button>
          );
        })}
      </div>

      {/* Interactive MPE Calculator Simulator */}
      <div className="bw-card p-6 sm:p-8 rounded-3xl border border-zinc-200 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-100 pb-3">
          <h2 className="text-sm font-display font-bold text-zinc-900 flex items-center space-x-2">
            <Sliders className="w-4 h-4 text-zinc-700" />
            <span>Interactive Maximum Permissible Error (MPE) Simulator</span>
          </h2>
          <div className="flex items-center space-x-2">
            <label className="text-xs text-zinc-700 font-mono cursor-pointer flex items-center space-x-2">
              <input
                type="checkbox"
                checked={isInService}
                onChange={(e) => setIsInService(e.target.checked)}
                className="rounded border-zinc-300 text-black focus:ring-0 accent-black"
              />
              <span>In-Service Verification (2 &times; MPE)</span>
            </label>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-xs">
          {/* Controls */}
          <div className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Test Load (m)</label>
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  step="any"
                  value={simLoad}
                  onChange={(e) => setSimLoad(Number(e.target.value))}
                  className="bw-input w-full px-3.5 py-2 text-xs font-mono font-bold"
                />
                <span className="text-zinc-500 font-mono">kg</span>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Verification Interval (e)</label>
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  step="any"
                  value={simE}
                  onChange={(e) => setSimE(Number(e.target.value))}
                  className="bw-input w-full px-3.5 py-2 text-xs font-mono"
                />
                <span className="text-zinc-500 font-mono">kg</span>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Max Capacity</label>
              <div className="flex items-center space-x-2">
                <input
                  type="number"
                  step="any"
                  value={simMax}
                  onChange={(e) => setSimMax(Number(e.target.value))}
                  className="bw-input w-full px-3.5 py-2 text-xs font-mono"
                />
                <span className="text-zinc-500 font-mono">kg</span>
              </div>
            </div>
          </div>

          {/* Results Badge Card */}
          <div className="md:col-span-2 p-6 rounded-2xl bg-zinc-50 border border-zinc-200 flex flex-col justify-between space-y-4">
            <div>
              <div className="text-[11px] text-zinc-500 font-mono uppercase tracking-wider">
                OIML R 76 TABLE 6 TOLERANCES
              </div>
              <div className="text-xs text-zinc-700 mt-1 font-mono">
                Load in Verification Scale Intervals: <span className="font-bold text-zinc-900">{mInE.toFixed(1)} e</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-4 rounded-xl bg-white border border-zinc-200 text-center shadow-sm">
                <div className="text-xs text-zinc-500 font-mono">MPE in Scale Intervals</div>
                <div className="text-2xl font-mono font-extrabold text-zinc-900 mt-1">
                  &plusmn;{mpeE.toFixed(1)} e
                </div>
              </div>

              <div className="p-4 rounded-xl bg-white border border-zinc-200 text-center shadow-sm">
                <div className="text-xs text-zinc-500 font-mono">MPE in Engineering Units</div>
                <div className="text-2xl font-mono font-extrabold text-zinc-900 mt-1">
                  &plusmn;{mpeUnit.toFixed(4)} kg
                </div>
              </div>
            </div>

            <div className="text-[11px] text-zinc-500 flex items-center space-x-2">
              <Info className="w-3.5 h-3.5 text-zinc-700 shrink-0" />
              <span>
                Any observed error with |E<sub>c</sub>| &le; {mpeUnit.toFixed(4)} kg is compliant with OIML R 76 statutory limits.
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Accuracy Class Specifications Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm space-y-3 text-xs">
          <h3 className="font-display font-bold text-zinc-900 tracking-wide text-sm">Table 3: Metrological Parameters</h3>
          <div className="space-y-2 text-zinc-700">
            <div className="flex justify-between py-2 border-b border-zinc-100">
              <span className="text-zinc-500">Verification Interval (e):</span>
              <span className="font-mono font-bold text-zinc-900">{currentSpec.eMin}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-zinc-100">
              <span className="text-zinc-500">Minimum Scale Intervals (n<sub>min</sub>):</span>
              <span className="font-mono font-bold text-zinc-900">{currentSpec.nMin.toLocaleString()}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-zinc-100">
              <span className="text-zinc-500">Maximum Scale Intervals (n<sub>max</sub>):</span>
              <span className="font-mono font-bold text-zinc-900">{currentSpec.nMax}</span>
            </div>
            <div className="flex justify-between py-2 border-b border-zinc-100">
              <span className="text-zinc-500">Minimum Capacity (Min):</span>
              <span className="font-mono font-bold text-zinc-900">{currentSpec.minCapacity}</span>
            </div>
            <div className="py-2 text-[11px] text-zinc-500 leading-relaxed font-sans">
              <span className="font-bold text-zinc-800">Typical Applications:</span> {currentSpec.typical}
            </div>
          </div>
        </div>

        <div className="bw-card p-6 rounded-3xl border border-zinc-200 shadow-sm space-y-3 text-xs">
          <h3 className="font-display font-bold text-zinc-900 tracking-wide text-sm">Table 6: Error Tolerance Step Bands ({selectedClass})</h3>
          <div className="space-y-2 font-mono text-zinc-700">
            {selectedClass === 'Class III' && (
              <>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span>0 &le; m &le; 500 e:</span>
                  <span className="font-bold text-zinc-900">&plusmn; 0.5 e</span>
                </div>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span>500 e &lt; m &le; 2,000 e:</span>
                  <span className="font-bold text-zinc-900">&plusmn; 1.0 e</span>
                </div>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span>2,000 e &lt; m &le; 10,000 e:</span>
                  <span className="font-bold text-zinc-900">&plusmn; 1.5 e</span>
                </div>
              </>
            )}
            {selectedClass === 'Class II' && (
              <>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span>0 &le; m &le; 5,000 e:</span>
                  <span className="font-bold text-zinc-900">&plusmn; 0.5 e</span>
                </div>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span>5,000 e &lt; m &le; 20,000 e:</span>
                  <span className="font-bold text-zinc-900">&plusmn; 1.0 e</span>
                </div>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span>20,000 e &lt; m &le; 100,000 e:</span>
                  <span className="font-bold text-zinc-900">&plusmn; 1.5 e</span>
                </div>
              </>
            )}
            {selectedClass === 'Class I' && (
              <>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span>0 &le; m &le; 50,000 e:</span>
                  <span className="font-bold text-zinc-900">&plusmn; 0.5 e</span>
                </div>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span>50,000 e &lt; m &le; 200,000 e:</span>
                  <span className="font-bold text-zinc-900">&plusmn; 1.0 e</span>
                </div>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span>m &gt; 200,000 e:</span>
                  <span className="font-bold text-zinc-900">&plusmn; 1.5 e</span>
                </div>
              </>
            )}
            {selectedClass === 'Class IIII' && (
              <>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span>0 &le; m &le; 50 e:</span>
                  <span className="font-bold text-zinc-900">&plusmn; 0.5 e</span>
                </div>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span>50 e &lt; m &le; 200 e:</span>
                  <span className="font-bold text-zinc-900">&plusmn; 1.0 e</span>
                </div>
                <div className="flex justify-between py-2 border-b border-zinc-100">
                  <span>200 e &lt; m &le; 1,000 e:</span>
                  <span className="font-bold text-zinc-900">&plusmn; 1.5 e</span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
