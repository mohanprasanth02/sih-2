import React, { useState, useEffect } from 'react';
import {
  Scale,
  Building,
  Thermometer,
  Activity,
  CheckCircle,
  XCircle,
  FileText,
  Download,
  Save,
  RotateCcw,
  Sparkles,
  Shield,
  Layers,
  Camera,
  AlertTriangle,
  Info,
  Check,
  ChevronRight,
  ChevronLeft,
  Cpu,
  CornerDownRight,
  Sliders,
  CheckCircle2
} from 'lucide-react';
import { api } from '../../api';
import { AccuracyClassType, WeighingReading, RepeatabilityLoadSeries, EccentricityPosition } from '../../types';

interface NAWITestWizardViewProps {
  onSuccess: (id: string) => void;
  onCancel: () => void;
  role?: string;
}

export const NAWITestWizardView: React.FC<NAWITestWizardViewProps> = ({ onSuccess, onCancel, role = 'inspector' }) => {
  const [activeStep, setActiveStep] = useState<number>(1);
  const [calculating, setCalculating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedId, setSavedId] = useState<string | null>(null);
  const [calcResult, setCalcResult] = useState<any>(null);
  const [registeredManufacturers, setRegisteredManufacturers] = useState<any[]>([]);
  const [registeredLaboratories, setRegisteredLaboratories] = useState<any[]>([]);

  useEffect(() => {
    api.getOIMLManufacturers().then(setRegisteredManufacturers).catch(() => {});
    api.getOIMLLaboratories().then(setRegisteredLaboratories).catch(() => {});
  }, []);

  // Form State: 1. Instrument & Manufacturer Specs
  const [manufacturerName, setManufacturerName] = useState('Standard Instruments & Metrology Ltd');
  const [manufacturerAddress, setManufacturerAddress] = useState('Plot 12, Metrology Industrial Estate, Pune, Maharashtra - 411026');
  const [countryOfOrigin, setCountryOfOrigin] = useState('India');
  const [contactEmail, setContactEmail] = useState('compliance@standardmetrology.in');
  const [contactPhone, setContactPhone] = useState('+91 20 2712 4400');
  const [licenseNumber, setLicenseNumber] = useState('LM-IND-MFG-MH-5521');

  const [instrumentType, setInstrumentType] = useState('Electronic Retail Counter Scale');
  const [modelName, setModelName] = useState('SIM-SmartScale-15K');
  const [serialNumber, setSerialNumber] = useState('SN-2026-SIM-0992');
  const [accuracyClass, setAccuracyClass] = useState<AccuracyClassType>('Class III');
  const [maxCapacity, setMaxCapacity] = useState<number>(15.0);
  const [minCapacity, setMinCapacity] = useState<number>(0.1);
  const [verificationIntervalE, setVerificationIntervalE] = useState<number>(0.005);
  const [scaleIntervalD, setScaleIntervalD] = useState<number>(0.005);
  const [units, setUnits] = useState('kg');
  const [tareType, setTareType] = useState('Subtractive');
  const [maxTare, setMaxTare] = useState<number>(15.0);
  const [tempMin, setTempMin] = useState<number>(-10.0);
  const [tempMax, setTempMax] = useState<number>(40.0);
  const [powerSupply, setPowerSupply] = useState('230V AC (+10% / -15%), 50Hz / 6V Rechargeable Battery');
  const [loadCellDetails, setLoadCellDetails] = useState('Zemic L6E3 Aluminum Single Point C3 Load Cell (OIML R60 Certified)');
  const [indicatorDetails, setIndicatorDetails] = useState('High Precision 24-bit Sigma-Delta ADC with Dual Display');
  const [softwareVersion, setSoftwareVersion] = useState('v2.4.0');
  const [softwareChecksum, setSoftwareChecksum] = useState('CRC32: 0x8A14C3D9');

  // Form State: 2. Laboratory & Environmental Conditions
  const [labName, setLabName] = useState('National Legal Metrology Type Evaluation Laboratory');
  const [labAccreditation, setLabAccreditation] = useState('NABL ISO/IEC 17025 Accredited & OIML Issuing Authority');
  const [labTemperature, setLabTemperature] = useState<number>(23.2);
  const [labHumidity, setLabHumidity] = useState<number>(50.5);
  const [labPressure, setLabPressure] = useState<number>(1012.4);
  const [localGravityG, setLocalGravityG] = useState<number>(9.7803);
  const [standardWeightsUsed, setStandardWeightsUsed] = useState('Class M1 & F2 Working Standards (Traceable to NPL India)');
  const [testingOfficerName, setTestingOfficerName] = useState('Er. Rajesh Sharma (Senior Metrological Officer)');
  const [approvingOfficerName, setApprovingOfficerName] = useState('Dr. Priya V. Iyer (Director of Legal Metrology)');

  // Form State: 3. Test Observations
  const [weighingReadings, setWeighingReadings] = useState<WeighingReading[]>([
    { index: 1, direction: 'INCR', load: 0.0, indication: 0.0, delta_l: 0.0025 },
    { index: 2, direction: 'INCR', load: 0.1, indication: 0.1, delta_l: 0.0025 },
    { index: 3, direction: 'INCR', load: 2.5, indication: 2.5, delta_l: 0.0024 },
    { index: 4, direction: 'INCR', load: 5.0, indication: 5.0, delta_l: 0.0025 },
    { index: 5, direction: 'INCR', load: 7.5, indication: 7.5, delta_l: 0.0026 },
    { index: 6, direction: 'INCR', load: 10.0, indication: 10.0, delta_l: 0.0026 },
    { index: 7, direction: 'INCR', load: 15.0, indication: 15.0, delta_l: 0.0025 },
    { index: 8, direction: 'DECR', load: 10.0, indication: 10.0, delta_l: 0.0026 },
    { index: 9, direction: 'DECR', load: 5.0, indication: 5.0, delta_l: 0.0025 },
    { index: 10, direction: 'DECR', load: 2.5, indication: 2.5, delta_l: 0.0025 },
    { index: 11, direction: 'DECR', load: 0.1, indication: 0.1, delta_l: 0.0025 },
    { index: 12, direction: 'DECR', load: 0.0, indication: 0.0, delta_l: 0.0025 },
  ]);

  const [repeatabilitySeries, setRepeatabilitySeries] = useState<RepeatabilityLoadSeries[]>([
    { load: 7.5, readings: [7.500, 7.500, 7.505, 7.500, 7.500, 7.505, 7.500, 7.500, 7.505, 7.500] },
    { load: 15.0, readings: [15.000, 15.005, 15.000, 15.005, 15.000, 15.000, 15.005, 15.000, 15.005, 15.000] },
  ]);

  const [eccentricityPositions, setEccentricityPositions] = useState<EccentricityPosition[]>([
    { position: 'Center (1)', indication: 5.000, delta_l: 0.0025 },
    { position: 'Front-Left (2)', indication: 5.000, delta_l: 0.0025 },
    { position: 'Rear-Left (3)', indication: 5.005, delta_l: 0.0025 },
    { position: 'Rear-Right (4)', indication: 5.000, delta_l: 0.0025 },
    { position: 'Front-Right (5)', indication: 5.000, delta_l: 0.0025 },
  ]);

  const [tareZeroData, setTareZeroData] = useState({
    zero_setting_indication: 0.0,
    zero_delta_l: 0.0025,
    tare_load: 5.0,
    tare_indication: 5.0,
    tare_delta_l: 0.0025,
    net_load: 10.0,
    net_indication: 10.0,
    net_delta_l: 0.0025,
  });

  // Scale intervals n = Max / e
  const nIntervals = verificationIntervalE > 0 ? Math.round(maxCapacity / verificationIntervalE) : 0;
  const isNValid = nIntervals >= 100 && nIntervals <= 10000;

  // Real-time calculation on changes
  const runCalculation = async () => {
    try {
      setCalculating(true);
      const payload = {
        accuracy_class: accuracyClass,
        max_capacity: Number(maxCapacity),
        min_capacity: Number(minCapacity),
        verification_scale_interval_e: Number(verificationIntervalE),
        scale_interval_d: Number(scaleIntervalD),
        is_in_service_test: false,
        test_data: {
          weighing_test: weighingReadings,
          repeatability_test: repeatabilitySeries,
          eccentricity_test: {
            test_load: Number(maxCapacity) / 3.0,
            positions: eccentricityPositions,
          },
          tare_zero_test: tareZeroData,
          discrimination_test: [
            { load_level: 'Min (0.1kg)', load: 0.1, initial_indication: 0.1, extra_load: 0.007, new_indication: 0.105 },
            { load_level: 'Half-Max (7.5kg)', load: 7.5, initial_indication: 7.5, extra_load: 0.007, new_indication: 7.505 },
            { load_level: 'Max (15.0kg)', load: 15.0, initial_indication: 15.0, extra_load: 0.007, new_indication: 15.005 }
          ],
          environmental_voltage_test: {
            temperatures: [
              { temperature_c: 20.0, load: Number(maxCapacity), corrected_error: 0.001 },
              { temperature_c: 40.0, load: Number(maxCapacity), corrected_error: 0.002 },
              { temperature_c: -10.0, load: Number(maxCapacity), corrected_error: 0.002 }
            ],
            voltages: [
              { condition: 'Nominal (230V)', load: Number(maxCapacity), corrected_error: 0.001 },
              { condition: 'High Mains (+10%)', load: Number(maxCapacity), corrected_error: 0.002 },
              { condition: 'Low Mains (-15%)', load: Number(maxCapacity), corrected_error: 0.002 }
            ]
          }
        },
      };

      const result = await api.calculateOIML(payload);
      setCalcResult(result);
      if (result.test_summaries?.weighing_test?.readings) {
        setWeighingReadings(result.test_summaries.weighing_test.readings);
      }
      if (result.test_summaries?.eccentricity_test?.positions) {
        setEccentricityPositions(result.test_summaries.eccentricity_test.positions);
      }
    } catch (err) {
      console.error('Calculation error:', err);
    } finally {
      setCalculating(false);
    }
  };

  useEffect(() => {
    runCalculation();
  }, [accuracyClass, maxCapacity, verificationIntervalE, scaleIntervalD]);

  const handleAutoPopulatePoints = () => {
    const e = verificationIntervalE;
    const max = maxCapacity;
    const min = minCapacity;
    const p500e = Math.min(500 * e, max);
    const p2000e = Math.min(2000 * e, max);
    const halfMax = max / 2;

    const points = [
      { index: 1, direction: 'INCR' as const, load: 0.0, indication: 0.0, delta_l: e / 2 },
      { index: 2, direction: 'INCR' as const, load: min, indication: min, delta_l: e / 2 },
      { index: 3, direction: 'INCR' as const, load: p500e, indication: p500e, delta_l: e / 2 },
      { index: 4, direction: 'INCR' as const, load: p2000e, indication: p2000e, delta_l: e / 2 },
      { index: 5, direction: 'INCR' as const, load: halfMax, indication: halfMax, delta_l: e / 2 },
      { index: 6, direction: 'INCR' as const, load: max, indication: max, delta_l: e / 2 },
      { index: 7, direction: 'DECR' as const, load: halfMax, indication: halfMax, delta_l: e / 2 },
      { index: 8, direction: 'DECR' as const, load: p2000e, indication: p2000e, delta_l: e / 2 },
      { index: 9, direction: 'DECR' as const, load: p500e, indication: p500e, delta_l: e / 2 },
      { index: 10, direction: 'DECR' as const, load: min, indication: min, delta_l: e / 2 },
      { index: 11, direction: 'DECR' as const, load: 0.0, indication: 0.0, delta_l: e / 2 },
    ];
    setWeighingReadings(points);
  };

  const handleSaveEvaluation = async () => {
    try {
      setSaving(true);
      const payload = {
        applicant_type: 'Manufacturer',
        manufacturer_name: manufacturerName,
        manufacturer_address: manufacturerAddress,
        country_of_origin: countryOfOrigin,
        contact_email: contactEmail,
        contact_phone: contactPhone,
        license_number: licenseNumber,
        instrument_type: instrumentType,
        model_name: modelName,
        serial_number: serialNumber,
        accuracy_class: accuracyClass,
        max_capacity: Number(maxCapacity),
        min_capacity: Number(minCapacity),
        verification_scale_interval_e: Number(verificationIntervalE),
        scale_interval_d: Number(scaleIntervalD),
        units: units,
        tare_type: tareType,
        max_tare: Number(maxTare),
        temp_range_min: Number(tempMin),
        temp_range_max: Number(tempMax),
        power_supply: powerSupply,
        load_cell_details: loadCellDetails,
        indicator_details: indicatorDetails,
        software_version: softwareVersion,
        software_checksum: softwareChecksum,
        lab_name: labName,
        lab_accreditation: labAccreditation,
        lab_temperature: Number(labTemperature),
        lab_humidity: Number(labHumidity),
        lab_pressure: Number(labPressure),
        local_gravity_g: Number(localGravityG),
        standard_weights_used: standardWeightsUsed,
        testing_officer_name: testingOfficerName,
        approving_officer_name: approvingOfficerName,
        test_data: {
          weighing_test: weighingReadings,
          repeatability_test: repeatabilitySeries,
          eccentricity_test: {
            test_load: Number(maxCapacity) / 3.0,
            positions: eccentricityPositions,
          },
          tare_zero_test: tareZeroData,
          discrimination_test: [
            { load_level: 'Min (0.1kg)', load: 0.1, initial_indication: 0.1, extra_load: 0.007, new_indication: 0.105 },
            { load_level: 'Half-Max (7.5kg)', load: 7.5, initial_indication: 7.5, extra_load: 0.007, new_indication: 7.505 },
            { load_level: 'Max (15.0kg)', load: 15.0, initial_indication: 15.0, extra_load: 0.007, new_indication: 15.005 }
          ],
          environmental_voltage_test: {
            temperatures: [
              { temperature_c: 20.0, load: Number(maxCapacity), corrected_error: 0.001 },
              { temperature_c: 40.0, load: Number(maxCapacity), corrected_error: 0.002 },
              { temperature_c: -10.0, load: Number(maxCapacity), corrected_error: 0.002 }
            ],
            voltages: [
              { condition: 'Nominal (230V)', load: Number(maxCapacity), corrected_error: 0.001 },
              { condition: 'High Mains (+10%)', load: Number(maxCapacity), corrected_error: 0.002 },
              { condition: 'Low Mains (-15%)', load: Number(maxCapacity), corrected_error: 0.002 }
            ]
          }
        },
      };

      const res = await api.createOIMLEvaluation(payload);
      setSavedId(res.id);
      onSuccess(res.id);
    } catch (err) {
      console.error('Save evaluation error:', err);
      alert('Failed to save evaluation: ' + (err as Error).message);
    } finally {
      setSaving(false);
    }
  };

  const steps = [
    { num: 1, label: 'Instrument Specs', icon: Scale },
    { num: 2, label: 'Lab Conditions', icon: Thermometer },
    { num: 3, label: 'Weighing Test (A.4.4)', icon: Activity },
    { num: 4, label: 'Repeat & Eccentricity', icon: Layers },
    { num: 5, label: 'Review & Certification', icon: Shield },
  ];

  return (
    <div className="space-y-6 max-w-6xl mx-auto pb-16 animate-fade-in font-sans">
      {/* Wizard Header Bar */}
      <div className="bw-card p-6 sm:p-7 rounded-3xl border border-zinc-200 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center space-x-2 text-zinc-500 text-xs font-mono font-medium uppercase tracking-wider mb-1.5">
              <Scale className="w-3.5 h-3.5 text-zinc-900" />
              <span>OIML R 76-1:2006 (E) &bull; DIGITAL PATTERN EVALUATION</span>
            </div>
            <h1 className="text-2xl font-display font-extrabold text-zinc-900 tracking-tight">
              Test Observation &amp; Error Compliance Engine
            </h1>
            <p className="text-xs text-zinc-500 mt-1">
              Automated MPE Table 6 calculation with flash-point changeover formulas
            </p>
          </div>

          <div className="flex items-center space-x-3">
            <button
              onClick={runCalculation}
              disabled={calculating}
              className="bw-btn-secondary px-4 py-2 text-xs flex items-center space-x-2"
            >
              <Sparkles className="w-3.5 h-3.5 text-zinc-700" />
              <span>{calculating ? 'Evaluating...' : 'Recalculate Metrology'}</span>
            </button>
            <button
              onClick={onCancel}
              className="bw-btn-secondary px-4 py-2 text-xs"
            >
              Back
            </button>
          </div>
        </div>

        {/* Live Metrology Scale Terminal */}
        <div className="p-4 rounded-2xl bg-zinc-900 text-white flex flex-wrap items-center justify-between gap-4 font-mono">
          <div className="flex items-center space-x-2.5">
            <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
            <div className="text-xs text-zinc-400 uppercase tracking-widest font-bold">
              ACTIVE SCALE PARAMETERS:
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-6 text-xs">
            <div>
              <span className="text-zinc-500">CLASS: </span>
              <span className="text-white font-bold">{accuracyClass}</span>
            </div>
            <div>
              <span className="text-zinc-500">MAX: </span>
              <span className="text-white font-bold">{maxCapacity} {units}</span>
            </div>
            <div>
              <span className="text-zinc-500">e: </span>
              <span className="text-white font-bold">{verificationIntervalE} {units}</span>
            </div>
            <div>
              <span className="text-zinc-500">d: </span>
              <span className="text-white font-bold">{scaleIntervalD} {units}</span>
            </div>
            <div>
              <span className="text-zinc-500">n = Max/e: </span>
              <span className="text-white font-extrabold">{nIntervals.toLocaleString()}</span>
              <span className="text-zinc-400 ml-1.5 font-sans text-[11px]">
                {isNValid ? '(Valid)' : '(Out of range)'}
              </span>
            </div>
          </div>
        </div>

        {/* Stepper Navigation Pills */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 border-t border-zinc-100 pt-4">
          {steps.map((st) => {
            const Icon = st.icon;
            const isCurrent = activeStep === st.num;
            const isDone = activeStep > st.num;
            return (
              <button
                key={st.num}
                onClick={() => setActiveStep(st.num)}
                className={`flex items-center space-x-2.5 p-3 rounded-full text-left transition-all ${
                  isCurrent
                    ? 'bg-black text-white font-bold shadow-md'
                    : isDone
                    ? 'bg-zinc-100 text-zinc-800 border border-zinc-200'
                    : 'text-zinc-500 hover:bg-zinc-50 border border-transparent'
                }`}
              >
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-mono font-bold shrink-0 ${
                    isCurrent
                      ? 'bg-white text-black'
                      : isDone
                      ? 'bg-black text-white'
                      : 'bg-zinc-200 text-zinc-600'
                  }`}
                >
                  {isDone ? <Check className="w-3.5 h-3.5" /> : st.num}
                </div>
                <div className="truncate pr-2">
                  <div className="text-xs truncate">{st.label}</div>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* STEP 1: Instrument & Manufacturer Profile */}
      {activeStep === 1 && (
        <div className="bw-card p-6 sm:p-8 rounded-3xl border border-zinc-200 space-y-6">
          <div className="border-b border-zinc-100 pb-3 flex items-center justify-between">
            <h2 className="text-sm font-display font-bold text-zinc-900 flex items-center space-x-2">
              <Building className="w-4 h-4 text-zinc-700" />
              <span>Manufacturer Details &amp; Technical Parameters</span>
            </h2>
            <span className="text-xs text-zinc-400 font-mono">Legal Metrology Act, 2009 Sec 22</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Manufacturer Name</label>
              <input
                type="text"
                value={manufacturerName}
                onChange={(e) => setManufacturerName(e.target.value)}
                className="bw-input w-full px-3.5 py-2.5 text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Manufacturing License Number</label>
              <input
                type="text"
                value={licenseNumber}
                onChange={(e) => setLicenseNumber(e.target.value)}
                className="bw-input w-full px-3.5 py-2.5 font-mono text-xs"
              />
            </div>

            <div className="space-y-1.5 md:col-span-2">
              <label className="text-zinc-700 font-medium">Factory / Workshop Address</label>
              <input
                type="text"
                value={manufacturerAddress}
                onChange={(e) => setManufacturerAddress(e.target.value)}
                className="bw-input w-full px-3.5 py-2.5 text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Instrument Type</label>
              <input
                type="text"
                value={instrumentType}
                onChange={(e) => setInstrumentType(e.target.value)}
                className="bw-input w-full px-3.5 py-2.5 text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Model Designation</label>
              <input
                type="text"
                value={modelName}
                onChange={(e) => setModelName(e.target.value)}
                className="bw-input w-full px-3.5 py-2.5 font-bold text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Accuracy Class (OIML Table 3)</label>
              <select
                value={accuracyClass}
                onChange={(e) => setAccuracyClass(e.target.value as AccuracyClassType)}
                className="bw-input w-full px-3.5 py-2.5 font-medium text-xs bg-white"
              >
                <option value="Class I">Class I (Special Accuracy)</option>
                <option value="Class II">Class II (High Accuracy)</option>
                <option value="Class III">Class III (Medium Accuracy)</option>
                <option value="Class IIII">Class IIII (Ordinary Accuracy)</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Units of Measurement</label>
              <select
                value={units}
                onChange={(e) => setUnits(e.target.value)}
                className="bw-input w-full px-3.5 py-2.5 text-xs bg-white"
              >
                <option value="kg">Kilograms (kg)</option>
                <option value="g">Grams (g)</option>
                <option value="mg">Milligrams (mg)</option>
                <option value="t">Tonnes (t)</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Maximum Capacity (Max)</label>
              <input
                type="number"
                step="any"
                value={maxCapacity}
                onChange={(e) => setMaxCapacity(Number(e.target.value))}
                className="bw-input w-full px-3.5 py-2.5 font-mono font-bold text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Minimum Capacity (Min)</label>
              <input
                type="number"
                step="any"
                value={minCapacity}
                onChange={(e) => setMinCapacity(Number(e.target.value))}
                className="bw-input w-full px-3.5 py-2.5 font-mono text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Verification Interval (e)</label>
              <input
                type="number"
                step="any"
                value={verificationIntervalE}
                onChange={(e) => setVerificationIntervalE(Number(e.target.value))}
                className="bw-input w-full px-3.5 py-2.5 font-mono text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Scale Interval (d)</label>
              <input
                type="number"
                step="any"
                value={scaleIntervalD}
                onChange={(e) => setScaleIntervalD(Number(e.target.value))}
                className="bw-input w-full px-3.5 py-2.5 font-mono text-xs"
              />
            </div>

            <div className="space-y-1.5 md:col-span-2">
              <label className="text-zinc-700 font-medium">Load Cell Model &amp; OIML R 60 Certificate</label>
              <input
                type="text"
                value={loadCellDetails}
                onChange={(e) => setLoadCellDetails(e.target.value)}
                className="bw-input w-full px-3.5 py-2.5 text-xs"
              />
            </div>
          </div>

          {/* Scale Intervals Live Metrology Indicator */}
          <div className="p-4 rounded-2xl bg-zinc-50 border border-zinc-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <span className="text-xs text-zinc-500 font-mono">Verification Scale Intervals: n = Max / e</span>
              <div className="text-lg font-mono font-extrabold text-zinc-900 mt-0.5">
                n = {nIntervals.toLocaleString()} intervals
              </div>
            </div>
            <div>
              <span className={isNValid ? 'bw-badge-pass' : 'bw-badge-fail'}>
                {isNValid ? 'PERMISSIBLE RANGE [100 to 10,000]' : 'EXCEEDS CLASS RANGE'}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* STEP 2: Laboratory Conditions */}
      {activeStep === 2 && (
        <div className="bw-card p-6 sm:p-8 rounded-3xl border border-zinc-200 space-y-6">
          <div className="border-b border-zinc-100 pb-3 flex items-center justify-between">
            <h2 className="text-sm font-display font-bold text-zinc-900 flex items-center space-x-2">
              <Thermometer className="w-4 h-4 text-zinc-700" />
              <span>Laboratory &amp; Environmental Conditions (Clause A.3)</span>
            </h2>
            <span className="text-xs text-zinc-400 font-mono">Traceable Reference Standards</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Testing Laboratory Name</label>
              <input
                type="text"
                value={labName}
                onChange={(e) => setLabName(e.target.value)}
                className="bw-input w-full px-3.5 py-2.5 text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Accreditation Details</label>
              <input
                type="text"
                value={labAccreditation}
                onChange={(e) => setLabAccreditation(e.target.value)}
                className="bw-input w-full px-3.5 py-2.5 text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Ambient Temperature (&deg;C)</label>
              <input
                type="number"
                step="0.1"
                value={labTemperature}
                onChange={(e) => setLabTemperature(Number(e.target.value))}
                className="bw-input w-full px-3.5 py-2.5 font-mono font-bold text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Relative Humidity (% RH)</label>
              <input
                type="number"
                step="0.1"
                value={labHumidity}
                onChange={(e) => setLabHumidity(Number(e.target.value))}
                className="bw-input w-full px-3.5 py-2.5 font-mono font-bold text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Barometric Pressure (hPa)</label>
              <input
                type="number"
                step="0.1"
                value={labPressure}
                onChange={(e) => setLabPressure(Number(e.target.value))}
                className="bw-input w-full px-3.5 py-2.5 font-mono text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Local Gravity g (m/s&sup2;)</label>
              <input
                type="number"
                step="0.0001"
                value={localGravityG}
                onChange={(e) => setLocalGravityG(Number(e.target.value))}
                className="bw-input w-full px-3.5 py-2.5 font-mono text-xs"
              />
            </div>

            <div className="space-y-1.5 md:col-span-2">
              <label className="text-zinc-700 font-medium">Reference Mass Standards Used</label>
              <input
                type="text"
                value={standardWeightsUsed}
                onChange={(e) => setStandardWeightsUsed(e.target.value)}
                className="bw-input w-full px-3.5 py-2.5 text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Senior Testing Metrological Officer</label>
              <input
                type="text"
                value={testingOfficerName}
                onChange={(e) => setTestingOfficerName(e.target.value)}
                className="bw-input w-full px-3.5 py-2.5 text-xs"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-zinc-700 font-medium">Approving Director</label>
              <input
                type="text"
                value={approvingOfficerName}
                onChange={(e) => setApprovingOfficerName(e.target.value)}
                className="bw-input w-full px-3.5 py-2.5 text-xs"
              />
            </div>
          </div>
        </div>
      )}

      {/* STEP 3: Weighing Performance Test (Clause A.4.4) */}
      {activeStep === 3 && (
        <div className="bw-card p-6 sm:p-8 rounded-3xl border border-zinc-200 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-zinc-100 pb-4">
            <div>
              <h2 className="text-sm font-display font-bold text-zinc-900 flex items-center space-x-2">
                <Activity className="w-4 h-4 text-zinc-700" />
                <span>Weighing Performance Test (Clause A.4.4)</span>
              </h2>
              <p className="text-xs text-zinc-500 font-mono mt-1">
                E = I + 0.5e - &Delta;L - L &bull; Corrected Error: E<sub>c</sub> = E - E<sub>0</sub> &bull; |E<sub>c</sub>| &le; MPE
              </p>
            </div>

            <button
              onClick={handleAutoPopulatePoints}
              className="bw-btn-secondary px-4 py-2 text-xs flex items-center space-x-2"
            >
              <Sparkles className="w-3.5 h-3.5 text-zinc-700" />
              <span>Auto-Populate OIML Load Points</span>
            </button>
          </div>

          {/* Weighing Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="border-b border-zinc-200 text-zinc-600 font-mono bg-zinc-50/80">
                  <th className="py-2.5 px-3">#</th>
                  <th className="py-2.5 px-3">DIR</th>
                  <th className="py-2.5 px-3">LOAD ({units})</th>
                  <th className="py-2.5 px-3">INDICATION I</th>
                  <th className="py-2.5 px-3">&Delta;L (Small Weight)</th>
                  <th className="py-2.5 px-3">ERROR E<sub>c</sub></th>
                  <th className="py-2.5 px-3">E<sub>c</sub> (e)</th>
                  <th className="py-2.5 px-3">MPE (&plusmn;e)</th>
                  <th className="py-2.5 px-3">MPE ({units})</th>
                  <th className="py-2.5 px-3 text-right">VERDICT</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-zinc-100 font-mono">
                {weighingReadings.map((r, idx) => {
                  const isPass = r.status === 'PASS';
                  return (
                    <tr key={idx} className="hover:bg-zinc-50 transition-colors">
                      <td className="py-2 px-3 text-zinc-400">{idx + 1}</td>
                      <td className="py-2 px-3">
                        <span className="text-[10px] px-2 py-0.5 rounded-full font-mono border border-zinc-200 bg-zinc-100 text-zinc-800">
                          {r.direction}
                        </span>
                      </td>
                      <td className="py-2 px-3">
                        <input
                          type="number"
                          step="any"
                          value={r.load}
                          onChange={(e) => {
                            const newRows = [...weighingReadings];
                            newRows[idx].load = Number(e.target.value);
                            setWeighingReadings(newRows);
                          }}
                          className="w-20 px-2 py-1 bg-white border border-zinc-200 focus:border-black rounded-lg text-zinc-900 text-xs font-bold font-mono"
                        />
                      </td>
                      <td className="py-2 px-3">
                        <input
                          type="number"
                          step="any"
                          value={r.indication}
                          onChange={(e) => {
                            const newRows = [...weighingReadings];
                            newRows[idx].indication = Number(e.target.value);
                            setWeighingReadings(newRows);
                          }}
                          className="w-20 px-2 py-1 bg-white border border-zinc-200 focus:border-black rounded-lg text-zinc-900 text-xs font-bold font-mono"
                        />
                      </td>
                      <td className="py-2 px-3">
                        <input
                          type="number"
                          step="any"
                          value={r.delta_l ?? ''}
                          placeholder="e/2"
                          onChange={(e) => {
                            const newRows = [...weighingReadings];
                            newRows[idx].delta_l = e.target.value ? Number(e.target.value) : null;
                            setWeighingReadings(newRows);
                          }}
                          className="w-20 px-2 py-1 bg-white border border-zinc-200 focus:border-black rounded-lg text-zinc-600 text-xs font-mono"
                        />
                      </td>
                      <td className="py-2 px-3 text-zinc-900 font-bold">
                        {r.corrected_error !== undefined ? r.corrected_error.toFixed(4) : '-'}
                      </td>
                      <td className="py-2 px-3 text-zinc-600">
                        {r.corrected_error_e !== undefined ? `${r.corrected_error_e.toFixed(2)} e` : '-'}
                      </td>
                      <td className="py-2 px-3 text-zinc-900 font-bold">
                        {r.mpe_e !== undefined ? `\u00B1${r.mpe_e.toFixed(1)} e` : '-'}
                      </td>
                      <td className="py-2 px-3 text-zinc-600">
                        {r.mpe_unit !== undefined ? `\u00B1${r.mpe_unit.toFixed(4)}` : '-'}
                      </td>
                      <td className="py-2 px-3 text-right">
                        {r.status ? (
                          <span className={isPass ? 'bw-badge-pass' : 'bw-badge-fail'}>
                            {r.status}
                          </span>
                        ) : (
                          <span className="text-zinc-400">-</span>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* STEP 4: Repeatability & Eccentricity */}
      {activeStep === 4 && (
        <div className="space-y-6">
          {/* Repeatability Test */}
          <div className="bw-card p-6 sm:p-8 rounded-3xl border border-zinc-200 space-y-4">
            <div className="border-b border-zinc-100 pb-3 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-display font-bold text-zinc-900 flex items-center space-x-2">
                  <Layers className="w-4 h-4 text-zinc-700" />
                  <span>Repeatability Test (Clause A.4.10)</span>
                </h2>
                <p className="text-xs text-zinc-500 font-mono mt-0.5">
                  10 weighings at 0.5 Max and Max. Difference between results &le; |MPE|.
                </p>
              </div>
            </div>

            <div className="space-y-4">
              {repeatabilitySeries.map((s, sIdx) => {
                const minVal = Math.min(...s.readings);
                const maxVal = Math.max(...s.readings);
                const diff = Number((maxVal - minVal).toFixed(4));
                const repSummary = calcResult?.test_summaries?.repeatability_test?.load_series?.[sIdx];
                const mpeE = s.load <= 500 * verificationIntervalE ? 0.5 : s.load <= 2000 * verificationIntervalE ? 1.0 : 1.5;
                const mpeUnit = Number((mpeE * verificationIntervalE).toFixed(4));
                const isPass = repSummary ? repSummary.status === 'PASS' : diff <= (mpeUnit + 1e-9);

                return (
                  <div key={sIdx} className="p-4 rounded-2xl bg-zinc-50 border border-zinc-200 space-y-3">
                    <div className="flex items-center justify-between text-xs">
                      <span className="font-bold text-zinc-900 font-mono">
                        SERIES {sIdx + 1}: TEST LOAD = {s.load} {units} (|MPE| = &plusmn;{mpeUnit} {units})
                      </span>
                      <div className="flex items-center space-x-3 font-mono">
                        <span className="text-zinc-500">Range &Delta; = {diff} {units}</span>
                        <span className={isPass ? 'bw-badge-pass' : 'bw-badge-fail'}>
                          {isPass ? 'PASS' : 'FAIL'}
                        </span>
                      </div>
                    </div>

                    <div className="grid grid-cols-5 sm:grid-cols-10 gap-2 font-mono">
                      {s.readings.map((val, rIdx) => (
                        <div key={rIdx} className="space-y-1">
                          <label className="text-[10px] text-zinc-400">#{rIdx + 1}</label>
                          <input
                            type="number"
                            step="any"
                            value={val}
                            onChange={(e) => {
                              const newSeries = [...repeatabilitySeries];
                              newSeries[sIdx].readings[rIdx] = Number(e.target.value);
                              setRepeatabilitySeries(newSeries);
                            }}
                            className="w-full px-2 py-1 bg-white border border-zinc-200 focus:border-black rounded-lg text-zinc-900 text-xs text-center font-bold font-mono"
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Eccentricity Test */}
          <div className="bw-card p-6 sm:p-8 rounded-3xl border border-zinc-200 space-y-4">
            <div className="border-b border-zinc-100 pb-3 flex items-center justify-between">
              <div>
                <h2 className="text-sm font-display font-bold text-zinc-900 flex items-center space-x-2">
                  <Scale className="w-4 h-4 text-zinc-700" />
                  <span>Eccentricity / Off-Center Loading Test (Clause A.4.7)</span>
                </h2>
                <p className="text-xs text-zinc-500 font-mono mt-0.5">
                  Load applied at Center and 4 corner quadrants (1/3 Max = {(maxCapacity / 3).toFixed(2)} {units})
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
              {eccentricityPositions.map((pos, pIdx) => {
                const isPosPass = pos.status ? pos.status === 'PASS' : true;
                return (
                  <div key={pIdx} className="p-4 rounded-2xl bg-zinc-50 border border-zinc-200 space-y-2 text-xs">
                    <div className="font-bold text-zinc-800 font-mono">{pos.position}</div>
                    <div className="space-y-1">
                      <label className="text-[10px] text-zinc-500 font-mono">Indication I</label>
                      <input
                        type="number"
                        step="any"
                        value={pos.indication}
                        onChange={(e) => {
                          const newPos = [...eccentricityPositions];
                          newPos[pIdx].indication = Number(e.target.value);
                          setEccentricityPositions(newPos);
                        }}
                        className="w-full px-2 py-1.5 bg-white border border-zinc-200 focus:border-black rounded-lg text-zinc-900 font-mono font-bold"
                      />
                    </div>
                    <div className="flex items-center justify-between text-[11px] pt-1">
                      <span className="text-zinc-500 font-mono">Ec: {pos.corrected_error !== undefined ? pos.corrected_error.toFixed(4) : '0.000'}</span>
                      <span className={isPosPass ? 'bw-badge-pass text-[10px]' : 'bw-badge-fail text-[10px]'}>
                        {isPosPass ? 'PASS' : 'FAIL'}
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* STEP 5: Final Review & Download */}
      {activeStep === 5 && (
        <div className="bw-card p-6 sm:p-8 rounded-3xl border border-zinc-200 space-y-6">
          <div className="border-b border-zinc-100 pb-3 flex items-center justify-between">
            <h2 className="text-sm font-display font-bold text-zinc-900 flex items-center space-x-2">
              <Shield className="w-4 h-4 text-zinc-900" />
              <span>Final Compliance Review &amp; Report Generation</span>
            </h2>
            <span className="text-xs text-zinc-500 font-mono">OIML R 76-2:2007 (E)</span>
          </div>

          {/* Dynamic Compliance Verdict Banner */}
          {calcResult?.is_fully_compliant ? (
            <div className="p-5 rounded-2xl bg-zinc-50 border border-zinc-300 flex items-start space-x-3.5">
              <CheckCircle className="w-6 h-6 text-black shrink-0 mt-0.5" />
              <div className="space-y-1">
                <h3 className="text-sm font-display font-bold text-zinc-900 tracking-wide">
                  STATUTORY MODEL EVALUATION: COMPLIANT WITH OIML R 76-1:2006
                </h3>
                <p className="text-xs text-zinc-600 leading-relaxed font-sans">
                  The weighing instrument submitted meets all metrological and technical requirements of OIML Recommendation R 76-1:2006 (E) Table 6 MPE limits. All {calcResult?.tests_evaluated_count || 'prescribed'} test series passed deterministic verification.
                </p>
              </div>
            </div>
          ) : (
            <div className="p-5 rounded-2xl bg-zinc-900 text-white flex items-start space-x-3.5">
              <AlertTriangle className="w-6 h-6 text-white shrink-0 mt-0.5" />
              <div className="space-y-1">
                <h3 className="text-sm font-display font-bold text-white tracking-wide">
                  COMPLIANCE REVIEW: NON-COMPLIANCE DETECTED
                </h3>
                <p className="text-xs text-zinc-300 leading-relaxed font-sans">
                  One or more observation points violate Table 6 Maximum Permissible Error (MPE) thresholds. {calcResult?.final_verdict || 'Review readings or submit draft for supervisor review.'}
                </p>
              </div>
            </div>
          )}

          {/* Workflow Status Info */}
          <div className="p-4 rounded-2xl bg-zinc-50 border border-zinc-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="space-y-1">
              <span className="font-bold text-zinc-900 font-mono">STATUTORY APPROVAL WORKFLOW</span>
              <p className="text-[11px] text-zinc-500">
                Saving will create a persistent Draft Test Report in the national laboratory database. A supervisor can then inspect, approve, and apply a cryptographic digital signature.
              </p>
            </div>
            <div>
              <span className="px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-zinc-200 text-zinc-800">
                STATUS: DRAFT
              </span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-wrap items-center justify-end gap-3 pt-4 border-t border-zinc-100">
            {role === 'viewer' ? (
              <span className="text-xs text-zinc-400 italic">Viewers have read-only access</span>
            ) : (
              <button
                onClick={handleSaveEvaluation}
                disabled={saving}
                className="bw-btn-primary px-6 py-2.5 text-xs font-bold flex items-center space-x-2 disabled:opacity-50"
              >
                <Save className="w-4 h-4 text-white" />
                <span>{saving ? 'Saving to Database...' : 'Save Draft Test Report'}</span>
              </button>
            )}
          </div>
        </div>
      )}

      {/* Wizard Footer Controls */}
      <div className="flex items-center justify-between pt-4">
        <button
          onClick={() => setActiveStep((prev) => Math.max(prev - 1, 1))}
          disabled={activeStep === 1}
          className="bw-btn-secondary flex items-center space-x-2 px-5 py-2.5 text-xs font-semibold disabled:opacity-30"
        >
          <ChevronLeft className="w-4 h-4" />
          <span>Previous Step</span>
        </button>

        <span className="text-xs text-zinc-400 font-mono">
          Step {activeStep} of {steps.length}
        </span>

        <button
          onClick={() => {
            if (activeStep < steps.length) {
              setActiveStep((prev) => prev + 1);
            } else {
              handleSaveEvaluation();
            }
          }}
          className="bw-btn-primary flex items-center space-x-2 px-6 py-2.5 text-xs font-bold"
        >
          <span>{activeStep === steps.length ? 'Finalize & Save' : 'Next Step'}</span>
          <ChevronRight className="w-4 h-4 text-white" />
        </button>
      </div>
    </div>
  );
};
